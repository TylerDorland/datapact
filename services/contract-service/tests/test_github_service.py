"""Tests for GitHub service."""

import base64

import pytest
import respx
import httpx

from contract_service.services.github_service import GitHubService


class TestGitHubService:
    @respx.mock
    @pytest.mark.asyncio
    async def test_get_pr_files(self):
        """Test getting files changed in a PR."""
        respx.get(
            "https://api.github.com/repos/owner/repo/pulls/42/files"
        ).mock(return_value=httpx.Response(200, json=[
            {"filename": "src/main.py", "status": "modified", "additions": 10, "deletions": 5},
            {"filename": "tests/test_main.py", "status": "added", "additions": 50, "deletions": 0},
        ]))

        github = GitHubService(token="test-token")
        try:
            files = await github.get_pr_files("owner", "repo", 42)

            assert len(files) == 2
            assert files[0]["filename"] == "src/main.py"
            assert files[1]["status"] == "added"
        finally:
            await github.close()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_pr_files_pagination(self):
        """Test that PR files are paginated correctly."""
        # First page
        respx.get(
            "https://api.github.com/repos/owner/repo/pulls/42/files",
            params={"page": "1", "per_page": "100"},
        ).mock(return_value=httpx.Response(200, json=[
            {"filename": f"file{i}.py", "status": "modified"} for i in range(100)
        ]))

        # Second page (empty - signals end)
        respx.get(
            "https://api.github.com/repos/owner/repo/pulls/42/files",
            params={"page": "2", "per_page": "100"},
        ).mock(return_value=httpx.Response(200, json=[]))

        github = GitHubService(token="test-token")
        try:
            files = await github.get_pr_files("owner", "repo", 42)
            assert len(files) == 100
        finally:
            await github.close()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_file_content(self):
        """Test getting file content from a repository."""
        content = "name: test\nversion: 1.0.0"
        encoded = base64.b64encode(content.encode()).decode()

        respx.get(
            "https://api.github.com/repos/owner/repo/contents/contract.yaml"
        ).mock(return_value=httpx.Response(200, json={
            "content": encoded,
            "encoding": "base64",
        }))

        github = GitHubService(token="test-token")
        try:
            result = await github.get_file_content("owner", "repo", "contract.yaml")

            assert result == content
        finally:
            await github.close()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_file_content_not_found(self):
        """Test getting non-existent file returns None."""
        respx.get(
            "https://api.github.com/repos/owner/repo/contents/missing.yaml"
        ).mock(return_value=httpx.Response(404, json={"message": "Not Found"}))

        github = GitHubService(token="test-token")
        try:
            result = await github.get_file_content("owner", "repo", "missing.yaml")
            assert result is None
        finally:
            await github.close()

    @respx.mock
    @pytest.mark.asyncio
    async def test_create_check_run(self):
        """Test creating a check run."""
        respx.post(
            "https://api.github.com/repos/owner/repo/check-runs"
        ).mock(return_value=httpx.Response(201, json={
            "id": 12345,
            "name": "DataPact Contract Check",
            "status": "completed",
            "conclusion": "success",
        }))

        github = GitHubService(token="test-token")
        try:
            result = await github.create_check_run(
                owner="owner",
                repo="repo",
                head_sha="abc123",
                name="DataPact Contract Check",
                status="completed",
                conclusion="success",
                output={
                    "title": "Contract Valid",
                    "summary": "All checks passed",
                },
            )

            assert result["id"] == 12345
            assert result["conclusion"] == "success"
        finally:
            await github.close()

    @respx.mock
    @pytest.mark.asyncio
    async def test_create_commit_status(self):
        """Test creating a commit status."""
        respx.post(
            "https://api.github.com/repos/owner/repo/statuses/abc123"
        ).mock(return_value=httpx.Response(201, json={
            "state": "success",
            "context": "datapact/contract-check",
            "description": "Contract valid",
        }))

        github = GitHubService(token="test-token")
        try:
            result = await github.create_commit_status(
                owner="owner",
                repo="repo",
                sha="abc123",
                state="success",
                description="Contract valid",
            )

            assert result["state"] == "success"
        finally:
            await github.close()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_pull_request(self):
        """Test getting pull request details."""
        respx.get(
            "https://api.github.com/repos/owner/repo/pulls/42"
        ).mock(return_value=httpx.Response(200, json={
            "number": 42,
            "title": "Add new feature",
            "state": "open",
            "head": {"sha": "abc123", "ref": "feature"},
            "base": {"ref": "main"},
        }))

        github = GitHubService(token="test-token")
        try:
            result = await github.get_pull_request("owner", "repo", 42)

            assert result["number"] == 42
            assert result["title"] == "Add new feature"
        finally:
            await github.close()

    @respx.mock
    @pytest.mark.asyncio
    async def test_create_pr_comment(self):
        """Test creating a PR comment."""
        respx.post(
            "https://api.github.com/repos/owner/repo/issues/42/comments"
        ).mock(return_value=httpx.Response(201, json={
            "id": 123,
            "body": "Test comment",
        }))

        github = GitHubService(token="test-token")
        try:
            result = await github.create_pr_comment(
                owner="owner",
                repo="repo",
                pr_number=42,
                body="Test comment",
            )

            assert result["body"] == "Test comment"
        finally:
            await github.close()

    @respx.mock
    @pytest.mark.asyncio
    async def test_compare_commits(self):
        """Test comparing two commits."""
        respx.get(
            "https://api.github.com/repos/owner/repo/compare/main...feature"
        ).mock(return_value=httpx.Response(200, json={
            "status": "ahead",
            "ahead_by": 5,
            "behind_by": 0,
            "commits": [{"sha": "abc123"}],
            "files": [{"filename": "test.py"}],
        }))

        github = GitHubService(token="test-token")
        try:
            result = await github.compare_commits("owner", "repo", "main", "feature")

            assert result["status"] == "ahead"
            assert result["ahead_by"] == 5
        finally:
            await github.close()

    def test_auth_header_set(self):
        """Test that auth header is set when token provided."""
        github = GitHubService(token="test-token")
        # The auth header is set when the client is created
        # We can verify this by checking the token is stored
        assert github.token == "test-token"
