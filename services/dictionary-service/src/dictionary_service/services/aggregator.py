"""Dictionary aggregation service."""

from typing import Any
import httpx

from dictionary_service.config import settings


class DictionaryAggregator:
    """Aggregates all contracts into a unified data dictionary."""

    def __init__(self, client: httpx.AsyncClient | None = None):
        """Initialize aggregator with optional HTTP client."""
        self._client = client
        self._owns_client = client is None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=settings.contract_service_url,
                timeout=30.0,
            )
        return self._client

    async def close(self):
        """Close the HTTP client if we own it."""
        if self._owns_client and self._client is not None:
            await self._client.aclose()
            self._client = None

    async def get_full_dictionary(self) -> dict[str, Any]:
        """Build complete data dictionary from all contracts."""
        client = await self._get_client()

        # Fetch all contracts
        resp = await client.get("/api/v1/contracts", params={"limit": 500})
        resp.raise_for_status()
        contracts = resp.json().get("contracts", [])

        dictionary: dict[str, Any] = {
            "datasets": [],
            "fields": [],
            "teams": set(),
            "pii_fields": [],
            "relationships": [],
        }

        for contract in contracts:
            # Add dataset entry
            dictionary["datasets"].append({
                "id": contract.get("id"),
                "name": contract["name"],
                "description": contract.get("description"),
                "publisher_team": contract.get("publisher_team"),
                "publisher_owner": contract.get("publisher_owner"),
                "status": contract.get("status"),
                "version": contract.get("version"),
                "subscriber_count": len(contract.get("subscribers", [])),
                "field_count": len(contract.get("fields", [])),
                "tags": contract.get("tags", []),
            })

            # Track teams
            if contract.get("publisher_team"):
                dictionary["teams"].add(contract["publisher_team"])

            # Add field entries
            for field in contract.get("fields", []):
                field_entry = {
                    "name": field["name"],
                    "dataset": contract["name"],
                    "dataset_id": contract.get("id"),
                    "data_type": field["data_type"],
                    "description": field.get("description"),
                    "is_pii": field.get("is_pii", False),
                    "nullable": field.get("nullable", True),
                    "is_primary_key": field.get("is_primary_key", False),
                    "is_foreign_key": field.get("is_foreign_key", False),
                    "foreign_key_reference": field.get("foreign_key_reference"),
                    "example_value": field.get("example_value"),
                    "constraints": field.get("constraints", []),
                    "publisher_team": contract.get("publisher_team"),
                }
                dictionary["fields"].append(field_entry)

                if field.get("is_pii"):
                    dictionary["pii_fields"].append(field_entry)

                # Track foreign key relationships
                if field.get("is_foreign_key") and field.get("foreign_key_reference"):
                    ref_parts = field["foreign_key_reference"].split(".")
                    if len(ref_parts) == 2:
                        dictionary["relationships"].append({
                            "from_dataset": contract["name"],
                            "from_field": field["name"],
                            "to_dataset": ref_parts[0],
                            "to_field": ref_parts[1],
                            "type": "foreign_key",
                        })

            # Track subscriber teams
            for sub in contract.get("subscribers", []):
                if sub.get("team"):
                    dictionary["teams"].add(sub["team"])

        # Convert teams set to sorted list
        dictionary["teams"] = sorted(dictionary["teams"])

        # Add summary statistics
        dictionary["summary"] = {
            "total_datasets": len(dictionary["datasets"]),
            "total_fields": len(dictionary["fields"]),
            "total_teams": len(dictionary["teams"]),
            "pii_field_count": len(dictionary["pii_fields"]),
            "relationship_count": len(dictionary["relationships"]),
            "active_datasets": sum(
                1 for d in dictionary["datasets"] if d.get("status") == "active"
            ),
            "deprecated_datasets": sum(
                1 for d in dictionary["datasets"] if d.get("status") == "deprecated"
            ),
        }

        return dictionary

    async def get_dataset_details(self, dataset_name: str) -> dict[str, Any] | None:
        """Get detailed information about a specific dataset."""
        client = await self._get_client()

        resp = await client.get(f"/api/v1/contracts/name/{dataset_name}")
        if resp.status_code == 404:
            return None
        resp.raise_for_status()

        contract = resp.json()

        # Build detailed view
        return {
            "id": contract.get("id"),
            "name": contract["name"],
            "version": contract.get("version"),
            "description": contract.get("description"),
            "status": contract.get("status"),
            "publisher": {
                "team": contract.get("publisher_team"),
                "owner": contract.get("publisher_owner"),
                "contact_email": contract.get("contact_email"),
                "repository_url": contract.get("repository_url"),
            },
            "fields": contract.get("fields", []),
            "quality_metrics": contract.get("quality_metrics", []),
            "access_config": contract.get("access_config"),
            "subscribers": contract.get("subscribers", []),
            "tags": contract.get("tags", []),
            "created_at": contract.get("created_at"),
            "updated_at": contract.get("updated_at"),
        }

    async def get_team_datasets(self, team: str) -> list[dict[str, Any]]:
        """Get all datasets owned by a specific team."""
        client = await self._get_client()

        resp = await client.get(
            "/api/v1/contracts",
            params={"publisher_team": team, "limit": 500},
        )
        resp.raise_for_status()

        contracts = resp.json().get("contracts", [])

        return [
            {
                "id": c.get("id"),
                "name": c["name"],
                "description": c.get("description"),
                "version": c.get("version"),
                "status": c.get("status"),
                "field_count": len(c.get("fields", [])),
                "subscriber_count": len(c.get("subscribers", [])),
            }
            for c in contracts
        ]

    async def get_field_lineage(self, dataset_name: str, field_name: str) -> dict[str, Any]:
        """Get lineage information for a specific field."""
        dictionary = await self.get_full_dictionary()

        # Find the field
        field_info = None
        for field in dictionary["fields"]:
            if field["dataset"] == dataset_name and field["name"] == field_name:
                field_info = field
                break

        if not field_info:
            return {"error": "Field not found"}

        # Find upstream (what this field references)
        upstream = []
        if field_info.get("foreign_key_reference"):
            ref_parts = field_info["foreign_key_reference"].split(".")
            if len(ref_parts) == 2:
                upstream.append({
                    "dataset": ref_parts[0],
                    "field": ref_parts[1],
                    "relationship": "references",
                })

        # Find downstream (fields that reference this field)
        downstream = []
        for rel in dictionary["relationships"]:
            if rel["to_dataset"] == dataset_name and rel["to_field"] == field_name:
                downstream.append({
                    "dataset": rel["from_dataset"],
                    "field": rel["from_field"],
                    "relationship": "referenced_by",
                })

        # Find fields with the same name across datasets
        similar_fields = [
            {
                "dataset": f["dataset"],
                "data_type": f["data_type"],
                "description": f.get("description"),
            }
            for f in dictionary["fields"]
            if f["name"] == field_name and f["dataset"] != dataset_name
        ]

        return {
            "field": field_info,
            "upstream": upstream,
            "downstream": downstream,
            "similar_fields": similar_fields,
        }
