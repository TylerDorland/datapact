"""GitHub API service for PR-based contract enforcement."""

import base64
import logging
from typing import Any

import httpx

from contract_service.config import settings

logger = logging.getLogger(__name__)


class GitHubService:
    """Service for interacting with GitHub API."""

    GITHUB_API_URL = "https://api.github.com"

    def __init__(self, token: str | None = None):
        """
        Initialize GitHub service.

        Args:
            token: GitHub API token (personal access token or GitHub App token)
        """
        self.token = token or settings.github_token
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client with auth headers."""
        if self._client is None:
            headers = {
                "Accept": "application/vnd.github.v3+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"

            self._client = httpx.AsyncClient(
                base_url=self.GITHUB_API_URL,
                headers=headers,
                timeout=30.0,
            )
        return self._client

    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def get_pr_files(
        self,
        owner: str,
        repo: str,
        pr_number: int,
    ) -> list[dict[str, Any]]:
        """
        Get list of files changed in a pull request.

        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number

        Returns:
            List of file objects with filename, status, additions, deletions, etc.
        """
        client = await self._get_client()

        files = []
        page = 1
        per_page = 100

        while True:
            resp = await client.get(
                f"/repos/{owner}/{repo}/pulls/{pr_number}/files",
                params={"page": page, "per_page": per_page},
            )
            resp.raise_for_status()

            page_files = resp.json()
            if not page_files:
                break

            files.extend(page_files)

            if len(page_files) < per_page:
                break

            page += 1

        return files

    async def get_file_content(
        self,
        owner: str,
        repo: str,
        path: str,
        ref: str = "main",
    ) -> str | None:
        """
        Get content of a file from a repository.

        Args:
            owner: Repository owner
            repo: Repository name
            path: File path within repository
            ref: Git reference (branch, tag, or commit SHA)

        Returns:
            File content as string, or None if not found
        """
        client = await self._get_client()

        try:
            resp = await client.get(
                f"/repos/{owner}/{repo}/contents/{path}",
                params={"ref": ref},
            )

            if resp.status_code == 404:
                return None

            resp.raise_for_status()
            data = resp.json()

            # GitHub returns base64-encoded content
            if data.get("encoding") == "base64" and data.get("content"):
                content = base64.b64decode(data["content"]).decode("utf-8")
                return content

            return None
        except httpx.HTTPError as e:
            logger.error(f"Failed to get file content: {e}")
            return None

    async def create_check_run(
        self,
        owner: str,
        repo: str,
        head_sha: str,
        name: str,
        status: str = "completed",
        conclusion: str | None = None,
        output: dict[str, Any] | None = None,
        details_url: str | None = None,
    ) -> dict[str, Any]:
        """
        Create a check run for a commit.

        Args:
            owner: Repository owner
            repo: Repository name
            head_sha: Commit SHA
            name: Name of the check
            status: Check status (queued, in_progress, completed)
            conclusion: Check conclusion (success, failure, neutral, cancelled, skipped, timed_out, action_required)
            output: Check output with title, summary, and optional text/annotations
            details_url: URL for more details

        Returns:
            Created check run object
        """
        client = await self._get_client()

        payload: dict[str, Any] = {
            "name": name,
            "head_sha": head_sha,
            "status": status,
        }

        if status == "completed" and conclusion:
            payload["conclusion"] = conclusion

        if output:
            payload["output"] = output

        if details_url:
            payload["details_url"] = details_url

        resp = await client.post(
            f"/repos/{owner}/{repo}/check-runs",
            json=payload,
        )
        resp.raise_for_status()

        return resp.json()

    async def update_check_run(
        self,
        owner: str,
        repo: str,
        check_run_id: int,
        status: str | None = None,
        conclusion: str | None = None,
        output: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Update an existing check run.

        Args:
            owner: Repository owner
            repo: Repository name
            check_run_id: Check run ID
            status: New status
            conclusion: Check conclusion
            output: Updated output

        Returns:
            Updated check run object
        """
        client = await self._get_client()

        payload: dict[str, Any] = {}

        if status:
            payload["status"] = status

        if conclusion:
            payload["conclusion"] = conclusion

        if output:
            payload["output"] = output

        resp = await client.patch(
            f"/repos/{owner}/{repo}/check-runs/{check_run_id}",
            json=payload,
        )
        resp.raise_for_status()

        return resp.json()

    async def create_commit_status(
        self,
        owner: str,
        repo: str,
        sha: str,
        state: str,
        context: str = "datapact/contract-check",
        description: str | None = None,
        target_url: str | None = None,
    ) -> dict[str, Any]:
        """
        Create a commit status (legacy status API, works without GitHub App).

        Args:
            owner: Repository owner
            repo: Repository name
            sha: Commit SHA
            state: Status state (error, failure, pending, success)
            context: Status context name
            description: Short description
            target_url: URL for more details

        Returns:
            Created status object
        """
        client = await self._get_client()

        payload: dict[str, Any] = {
            "state": state,
            "context": context,
        }

        if description:
            payload["description"] = description[:140]  # GitHub limit

        if target_url:
            payload["target_url"] = target_url

        resp = await client.post(
            f"/repos/{owner}/{repo}/statuses/{sha}",
            json=payload,
        )
        resp.raise_for_status()

        return resp.json()

    async def get_pull_request(
        self,
        owner: str,
        repo: str,
        pr_number: int,
    ) -> dict[str, Any]:
        """
        Get pull request details.

        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number

        Returns:
            Pull request object
        """
        client = await self._get_client()

        resp = await client.get(f"/repos/{owner}/{repo}/pulls/{pr_number}")
        resp.raise_for_status()

        return resp.json()

    async def create_pr_comment(
        self,
        owner: str,
        repo: str,
        pr_number: int,
        body: str,
    ) -> dict[str, Any]:
        """
        Create a comment on a pull request.

        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number
            body: Comment body (markdown supported)

        Returns:
            Created comment object
        """
        client = await self._get_client()

        resp = await client.post(
            f"/repos/{owner}/{repo}/issues/{pr_number}/comments",
            json={"body": body},
        )
        resp.raise_for_status()

        return resp.json()

    async def get_repository(
        self,
        owner: str,
        repo: str,
    ) -> dict[str, Any]:
        """
        Get repository details.

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            Repository object
        """
        client = await self._get_client()

        resp = await client.get(f"/repos/{owner}/{repo}")
        resp.raise_for_status()

        return resp.json()

    async def compare_commits(
        self,
        owner: str,
        repo: str,
        base: str,
        head: str,
    ) -> dict[str, Any]:
        """
        Compare two commits/branches.

        Args:
            owner: Repository owner
            repo: Repository name
            base: Base commit/branch
            head: Head commit/branch

        Returns:
            Comparison object with files, commits, etc.
        """
        client = await self._get_client()

        resp = await client.get(
            f"/repos/{owner}/{repo}/compare/{base}...{head}",
        )
        resp.raise_for_status()

        return resp.json()
