"""Tests for GitHub webhook handlers."""

import hashlib
import hmac
import json

import pytest
import respx
import httpx
from httpx import ASGITransport, AsyncClient

from contract_service.main import app
from contract_service.config import settings


@pytest.fixture
def pr_webhook_payload():
    """Sample pull request webhook payload."""
    return {
        "action": "opened",
        "number": 42,
        "pull_request": {
            "number": 42,
            "head": {
                "sha": "abc123def456",
                "ref": "feature/add-orders",
            },
            "base": {
                "ref": "main",
            },
        },
        "repository": {
            "name": "orders-service",
            "html_url": "https://github.com/example/orders-service",
            "owner": {
                "login": "example",
            },
        },
    }


@pytest.fixture
def push_webhook_payload():
    """Sample push webhook payload."""
    return {
        "ref": "refs/heads/main",
        "repository": {
            "name": "orders-service",
            "html_url": "https://github.com/example/orders-service",
            "owner": {
                "login": "example",
            },
        },
        "commits": [
            {
                "id": "abc123",
                "message": "Update contract",
                "modified": ["contract.yaml"],
                "added": [],
            }
        ],
    }


@pytest.fixture
def sample_contract_yaml():
    """Sample contract YAML content."""
    return """
name: orders
version: 1.0.0
description: Order data
publisher:
  team: commerce
  owner: orders-service
schema:
  - name: order_id
    type: uuid
    nullable: false
    primary_key: true
  - name: total
    type: decimal
    nullable: false
"""


def _create_signature(payload: bytes, secret: str) -> str:
    """Create webhook signature."""
    sig = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return f"sha256={sig}"


class TestWebhookHandler:
    @pytest.mark.asyncio
    async def test_ping_event(self):
        """Test handling ping event."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/webhooks/github",
                json={"zen": "Keep it simple"},
                headers={"X-GitHub-Event": "ping"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "pong"
            assert data["zen"] == "Keep it simple"

    @pytest.mark.asyncio
    async def test_ignored_event(self):
        """Test that unknown events are ignored."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/webhooks/github",
                json={},
                headers={"X-GitHub-Event": "issues"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ignored"

    @pytest.mark.asyncio
    async def test_pr_ignored_action(self, pr_webhook_payload):
        """Test that non-relevant PR actions are ignored."""
        pr_webhook_payload["action"] = "closed"

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/webhooks/github",
                json=pr_webhook_payload,
                headers={"X-GitHub-Event": "pull_request"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ignored"
            assert data["action"] == "closed"

    @respx.mock
    @pytest.mark.asyncio
    async def test_pr_no_schema_changes(self, pr_webhook_payload):
        """Test PR with no schema changes passes."""
        # Mock GitHub API - PR files
        respx.get(
            "https://api.github.com/repos/example/orders-service/pulls/42/files"
        ).mock(return_value=httpx.Response(200, json=[
            {"filename": "README.md", "status": "modified"},
            {"filename": "src/main.py", "status": "modified"},
        ]))

        # Mock commit status creation
        respx.post(
            "https://api.github.com/repos/example/orders-service/check-runs"
        ).mock(return_value=httpx.Response(201, json={"id": 1}))

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/webhooks/github",
                json=pr_webhook_payload,
                headers={"X-GitHub-Event": "pull_request"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "approved"
            assert data["reason"] == "no_schema_changes"

    @respx.mock
    @pytest.mark.asyncio
    async def test_pr_schema_change_without_contract(self, pr_webhook_payload):
        """Test PR with schema changes but no contract update is blocked."""
        # Mock GitHub API - PR files with schema change
        respx.get(
            "https://api.github.com/repos/example/orders-service/pulls/42/files"
        ).mock(return_value=httpx.Response(200, json=[
            {"filename": "alembic/versions/001_add_column.py", "status": "added"},
        ]))

        # Mock check run creation
        respx.post(
            "https://api.github.com/repos/example/orders-service/check-runs"
        ).mock(return_value=httpx.Response(201, json={"id": 1}))

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/webhooks/github",
                json=pr_webhook_payload,
                headers={"X-GitHub-Event": "pull_request"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "blocked"
            assert data["reason"] == "missing_contract_update"

    @respx.mock
    @pytest.mark.asyncio
    async def test_pr_schema_and_contract_change(self, pr_webhook_payload, sample_contract_yaml):
        """Test PR with both schema and contract changes passes validation."""
        # Mock GitHub API - PR files
        respx.get(
            "https://api.github.com/repos/example/orders-service/pulls/42/files"
        ).mock(return_value=httpx.Response(200, json=[
            {"filename": "alembic/versions/001_add_column.py", "status": "added"},
            {"filename": "contract.yaml", "status": "modified"},
        ]))

        # Mock getting contract content
        import base64
        encoded_content = base64.b64encode(sample_contract_yaml.encode()).decode()
        respx.get(
            "https://api.github.com/repos/example/orders-service/contents/contract.yaml"
        ).mock(return_value=httpx.Response(200, json={
            "content": encoded_content,
            "encoding": "base64",
        }))

        # Mock check run creation
        respx.post(
            "https://api.github.com/repos/example/orders-service/check-runs"
        ).mock(return_value=httpx.Response(201, json={"id": 1}))

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/webhooks/github",
                json=pr_webhook_payload,
                headers={"X-GitHub-Event": "pull_request"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "approved"

    @pytest.mark.asyncio
    async def test_push_ignored_branch(self, push_webhook_payload):
        """Test push to non-main branch is ignored."""
        push_webhook_payload["ref"] = "refs/heads/feature/test"

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/webhooks/github",
                json=push_webhook_payload,
                headers={"X-GitHub-Event": "push"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ignored"
            assert data["ref"] == "refs/heads/feature/test"

    @pytest.mark.asyncio
    async def test_push_no_contract_changes(self, push_webhook_payload):
        """Test push without contract changes is ignored."""
        push_webhook_payload["commits"][0]["modified"] = ["README.md"]

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/webhooks/github",
                json=push_webhook_payload,
                headers={"X-GitHub-Event": "push"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ignored"
            assert data["reason"] == "no_contract_changes"


class TestSignatureVerification:
    @pytest.mark.asyncio
    async def test_invalid_signature_rejected(self, pr_webhook_payload, monkeypatch):
        """Test that invalid signatures are rejected when secret is configured."""
        # Set webhook secret
        monkeypatch.setattr(settings, "github_webhook_secret", "test-secret")

        payload_bytes = json.dumps(pr_webhook_payload).encode()

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/webhooks/github",
                content=payload_bytes,
                headers={
                    "X-GitHub-Event": "pull_request",
                    "X-Hub-Signature-256": "sha256=invalid",
                    "Content-Type": "application/json",
                },
            )

            assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_valid_signature_accepted(self, pr_webhook_payload, monkeypatch):
        """Test that valid signatures are accepted."""
        secret = "test-secret"
        monkeypatch.setattr(settings, "github_webhook_secret", secret)

        payload_bytes = json.dumps(pr_webhook_payload).encode()
        signature = _create_signature(payload_bytes, secret)

        # Mock GitHub API for the actual handler
        with respx.mock:
            respx.get(
                "https://api.github.com/repos/example/orders-service/pulls/42/files"
            ).mock(return_value=httpx.Response(200, json=[]))

            respx.post(
                "https://api.github.com/repos/example/orders-service/check-runs"
            ).mock(return_value=httpx.Response(201, json={"id": 1}))

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                response = await client.post(
                    "/api/v1/webhooks/github",
                    content=payload_bytes,
                    headers={
                        "X-GitHub-Event": "pull_request",
                        "X-Hub-Signature-256": signature,
                        "Content-Type": "application/json",
                    },
                )

                assert response.status_code == 200
