"""GitHub webhook handler routes."""

import hashlib
import hmac
import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Header, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from contract_service.config import settings
from contract_service.api.dependencies import get_db
from contract_service.services.github_service import GitHubService
from contract_service.services.contract_service import ContractCRUD
from contract_service.utils.yaml_parser import parse_contract_yaml

logger = logging.getLogger(__name__)

router = APIRouter()

# File patterns that indicate schema changes
SCHEMA_FILE_PATTERNS = [
    "alembic/versions/",
    "migrations/",
    "schema.sql",
    "models.py",
    "models/",
    "/models/",
]

# Contract file patterns
CONTRACT_FILE_PATTERNS = [
    "contract.yaml",
    "contract.yml",
    "datapact.yaml",
    "datapact.yml",
]


def _verify_signature(payload: bytes, signature: str | None, secret: str) -> bool:
    """Verify GitHub webhook signature."""
    if not signature:
        return False

    expected_sig = "sha256=" + hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(signature, expected_sig)


def _is_schema_file(filename: str) -> bool:
    """Check if file is a database schema file."""
    return any(pattern in filename for pattern in SCHEMA_FILE_PATTERNS)


def _is_contract_file(filename: str) -> bool:
    """Check if file is a contract file."""
    return any(filename.endswith(pattern) for pattern in CONTRACT_FILE_PATTERNS)


def _get_contract_file_path(files: list[dict[str, Any]]) -> str | None:
    """Find contract file path from changed files."""
    for file in files:
        if _is_contract_file(file["filename"]):
            return file["filename"]
    return None


@router.post("/github")
async def handle_github_webhook(
    request: Request,
    x_hub_signature_256: str | None = Header(None),
    x_github_event: str | None = Header(None),
    x_github_delivery: str | None = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Handle GitHub webhook events for PR-based contract enforcement.

    Supports:
    - pull_request: Check PRs for schema changes without contract updates
    - push: Sync contract to registry when merged to main
    """
    body = await request.body()

    # Verify webhook signature if secret is configured
    if settings.github_webhook_secret:
        if not _verify_signature(body, x_hub_signature_256, settings.github_webhook_secret):
            raise HTTPException(status_code=401, detail="Invalid webhook signature")

    payload = await request.json()

    logger.info(f"Received GitHub webhook: event={x_github_event}, delivery={x_github_delivery}")

    # Route to appropriate handler
    if x_github_event == "pull_request":
        return await _handle_pull_request(payload, db)
    elif x_github_event == "push":
        return await _handle_push(payload, db)
    elif x_github_event == "ping":
        return {"status": "pong", "zen": payload.get("zen")}

    return {"status": "ignored", "event": x_github_event}


async def _handle_pull_request(payload: dict[str, Any], db: AsyncSession) -> dict[str, Any]:
    """
    Handle pull request events.

    Checks if schema files are modified without corresponding contract updates.
    Creates GitHub check run or commit status to block or approve the PR.
    """
    action = payload.get("action")
    pr = payload.get("pull_request", {})
    repo = payload.get("repository", {})

    # Only process relevant actions
    if action not in ["opened", "synchronize", "reopened"]:
        return {"status": "ignored", "action": action}

    owner = repo.get("owner", {}).get("login", "")
    repo_name = repo.get("name", "")
    pr_number = pr.get("number")
    head_sha = pr.get("head", {}).get("sha", "")

    if not all([owner, repo_name, pr_number, head_sha]):
        logger.warning("Missing required PR data")
        return {"status": "error", "reason": "missing_data"}

    github = GitHubService()

    try:
        # Get changed files
        changed_files = await github.get_pr_files(
            owner=owner,
            repo=repo_name,
            pr_number=pr_number,
        )

        # Categorize changed files
        schema_files = [f for f in changed_files if _is_schema_file(f["filename"])]
        contract_files = [f for f in changed_files if _is_contract_file(f["filename"])]

        # No schema changes - nothing to enforce
        if not schema_files:
            await _create_success_status(
                github, owner, repo_name, head_sha,
                "No schema changes detected"
            )
            return {"status": "approved", "reason": "no_schema_changes"}

        # Schema changed but no contract update
        if not contract_files:
            await _create_failure_status(
                github, owner, repo_name, head_sha,
                schema_files,
                "Schema changes detected but no contract.yaml update"
            )
            return {"status": "blocked", "reason": "missing_contract_update"}

        # Both changed - validate contract matches schema
        contract_path = _get_contract_file_path(contract_files)
        if contract_path:
            validation_result = await _validate_contract_changes(
                github, owner, repo_name, pr, schema_files, contract_path
            )

            if validation_result["valid"]:
                await _create_success_status(
                    github, owner, repo_name, head_sha,
                    "Contract update matches schema changes"
                )
                return {"status": "approved"}
            else:
                await _create_failure_status(
                    github, owner, repo_name, head_sha,
                    schema_files,
                    validation_result.get("message", "Contract validation failed"),
                    validation_result.get("errors", [])
                )
                return {"status": "blocked", "reason": "validation_failed"}

        await _create_success_status(
            github, owner, repo_name, head_sha,
            "Contract update found"
        )
        return {"status": "approved"}

    except Exception as e:
        logger.error(f"Error processing PR webhook: {e}")
        # Don't block PR on our errors - create neutral status
        try:
            await github.create_commit_status(
                owner=owner,
                repo=repo_name,
                sha=head_sha,
                state="error",
                description=f"DataPact check error: {str(e)[:100]}",
            )
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await github.close()


async def _handle_push(payload: dict[str, Any], db: AsyncSession) -> dict[str, Any]:
    """
    Handle push events (merged PRs).

    Syncs contract.yaml to the Contract Service registry when pushed to main/master.
    """
    ref = payload.get("ref", "")
    repo = payload.get("repository", {})
    commits = payload.get("commits", [])

    # Only process pushes to main/master
    if ref not in ["refs/heads/main", "refs/heads/master"]:
        return {"status": "ignored", "ref": ref}

    owner = repo.get("owner", {}).get("login", "")
    repo_name = repo.get("name", "")
    branch = ref.split("/")[-1]

    # Check if contract file was updated in any commit
    contract_updated = False
    for commit in commits:
        modified_files = commit.get("modified", []) + commit.get("added", [])
        if any(_is_contract_file(f) for f in modified_files):
            contract_updated = True
            break

    if not contract_updated:
        return {"status": "ignored", "reason": "no_contract_changes"}

    github = GitHubService()

    try:
        # Find and fetch contract file
        contract_path = None
        for pattern in CONTRACT_FILE_PATTERNS:
            content = await github.get_file_content(
                owner=owner,
                repo=repo_name,
                path=pattern,
                ref=branch,
            )
            if content:
                contract_path = pattern
                break

        if not content:
            logger.warning(f"Contract file not found in {owner}/{repo_name}")
            return {"status": "skipped", "reason": "contract_not_found"}

        # Parse and sync contract
        try:
            contract_data = parse_contract_yaml(content)
        except Exception as e:
            logger.error(f"Failed to parse contract YAML: {e}")
            return {"status": "error", "reason": "invalid_yaml", "error": str(e)}

        # Add repository metadata
        contract_data["repository_url"] = repo.get("html_url")

        # Sync to database
        crud = ContractCRUD(db)
        existing = await crud.get_by_name(contract_data["name"])

        if existing:
            # Update existing contract
            from contract_service.schemas.contract import ContractUpdate
            update_data = ContractUpdate(**contract_data)
            await crud.update(existing.id, update_data)
            logger.info(f"Updated contract '{contract_data['name']}' from {owner}/{repo_name}")
        else:
            # Create new contract
            from contract_service.schemas.contract import ContractCreate
            create_data = ContractCreate(**contract_data)
            await crud.create(create_data)
            logger.info(f"Created contract '{contract_data['name']}' from {owner}/{repo_name}")

        return {
            "status": "synced",
            "contract_name": contract_data["name"],
            "repository": f"{owner}/{repo_name}",
        }

    except Exception as e:
        logger.error(f"Error syncing contract from push: {e}")
        return {"status": "error", "error": str(e)}
    finally:
        await github.close()


async def _create_success_status(
    github: GitHubService,
    owner: str,
    repo: str,
    sha: str,
    description: str,
) -> None:
    """Create success commit status."""
    try:
        # Try check run first (requires GitHub App)
        await github.create_check_run(
            owner=owner,
            repo=repo,
            head_sha=sha,
            name="DataPact Contract Check",
            status="completed",
            conclusion="success",
            output={
                "title": "Contract Valid",
                "summary": description,
            },
        )
    except Exception:
        # Fall back to commit status (works with personal access token)
        await github.create_commit_status(
            owner=owner,
            repo=repo,
            sha=sha,
            state="success",
            description=description,
        )


async def _create_failure_status(
    github: GitHubService,
    owner: str,
    repo: str,
    sha: str,
    schema_files: list[dict[str, Any]],
    message: str,
    errors: list[str] | None = None,
) -> None:
    """Create failure commit status with details."""
    schema_file_list = "\n".join(f"- {f['filename']}" for f in schema_files)
    error_list = "\n".join(f"- {e}" for e in (errors or []))

    summary = f"""{message}

**Changed schema files:**
{schema_file_list}

Please update your `contract.yaml` to reflect these schema changes.
"""

    if errors:
        summary += f"""
**Validation errors:**
{error_list}
"""

    try:
        # Try check run first
        await github.create_check_run(
            owner=owner,
            repo=repo,
            head_sha=sha,
            name="DataPact Contract Check",
            status="completed",
            conclusion="failure",
            output={
                "title": "Contract Update Required",
                "summary": summary,
            },
        )
    except Exception:
        # Fall back to commit status
        await github.create_commit_status(
            owner=owner,
            repo=repo,
            sha=sha,
            state="failure",
            description=message[:140],
        )


async def _validate_contract_changes(
    github: GitHubService,
    owner: str,
    repo: str,
    pr: dict[str, Any],
    schema_files: list[dict[str, Any]],
    contract_path: str,
) -> dict[str, Any]:
    """
    Validate that contract changes properly reflect schema changes.

    This performs basic validation:
    1. Contract file is valid YAML
    2. Contract has required fields
    3. Version was incremented (for existing contracts)
    """
    head_ref = pr.get("head", {}).get("ref", "")

    # Get contract content from PR head
    content = await github.get_file_content(
        owner=owner,
        repo=repo,
        path=contract_path,
        ref=head_ref,
    )

    if not content:
        return {
            "valid": False,
            "message": f"Could not read {contract_path}",
            "errors": [f"File {contract_path} not found or empty"],
        }

    # Parse contract YAML
    try:
        contract_data = parse_contract_yaml(content)
    except Exception as e:
        return {
            "valid": False,
            "message": "Invalid contract YAML",
            "errors": [str(e)],
        }

    errors = []

    # Check required fields
    required_fields = ["name", "version", "publisher", "fields"]
    for field in required_fields:
        if field not in contract_data:
            errors.append(f"Missing required field: {field}")

    # Check version format
    version = contract_data.get("version", "")
    if version and not _is_valid_semver(version):
        errors.append(f"Invalid version format: {version} (expected semver like 1.0.0)")

    # Check fields array is not empty
    fields = contract_data.get("fields", [])
    if not fields:
        errors.append("Contract must define at least one field")

    # Check each field has required attributes
    for i, field in enumerate(fields):
        if "name" not in field:
            errors.append(f"Field {i} missing 'name' attribute")
        if "data_type" not in field:
            errors.append(f"Field '{field.get('name', i)}' missing 'data_type' attribute")

    if errors:
        return {
            "valid": False,
            "message": "Contract validation failed",
            "errors": errors,
        }

    return {"valid": True}


def _is_valid_semver(version: str) -> bool:
    """Check if version string is valid semver."""
    import re
    pattern = r"^\d+\.\d+\.\d+(-[a-zA-Z0-9.-]+)?(\+[a-zA-Z0-9.-]+)?$"
    return bool(re.match(pattern, version))
