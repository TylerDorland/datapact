"""Search service for data dictionary."""

from typing import Any
from enum import Enum

from dictionary_service.services.aggregator import DictionaryAggregator


class SearchScope(str, Enum):
    """Scope for search queries."""

    ALL = "all"
    FIELDS = "fields"
    DATASETS = "datasets"
    DESCRIPTIONS = "descriptions"


class SearchService:
    """Search functionality across all contracts in the data dictionary."""

    def __init__(self, aggregator: DictionaryAggregator):
        """Initialize search service with aggregator."""
        self.aggregator = aggregator

    async def search(
        self,
        query: str,
        scope: SearchScope = SearchScope.ALL,
        data_type: str | None = None,
        is_pii: bool | None = None,
        team: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> dict[str, Any]:
        """
        Search across the data dictionary.

        Args:
            query: Search query string
            scope: Where to search (all, fields, datasets, descriptions)
            data_type: Filter by data type
            is_pii: Filter by PII flag
            team: Filter by publisher team
            limit: Maximum results to return
            offset: Offset for pagination

        Returns:
            Search results with matched items
        """
        dictionary = await self.aggregator.get_full_dictionary()
        query_lower = query.lower().strip()

        field_results = []
        dataset_results = []

        # Search fields
        if scope in (SearchScope.ALL, SearchScope.FIELDS, SearchScope.DESCRIPTIONS):
            field_results = self._search_fields(
                dictionary["fields"],
                query_lower,
                scope,
                data_type,
                is_pii,
                team,
            )

        # Search datasets
        if scope in (SearchScope.ALL, SearchScope.DATASETS, SearchScope.DESCRIPTIONS):
            dataset_results = self._search_datasets(
                dictionary["datasets"],
                query_lower,
                scope,
                team,
            )

        # Combine and sort results by relevance
        all_results = []

        for field in field_results:
            all_results.append({
                "type": "field",
                "relevance": field.pop("_relevance", 0),
                "data": field,
            })

        for dataset in dataset_results:
            all_results.append({
                "type": "dataset",
                "relevance": dataset.pop("_relevance", 0),
                "data": dataset,
            })

        # Sort by relevance (higher is better)
        all_results.sort(key=lambda x: x["relevance"], reverse=True)

        # Apply pagination
        total = len(all_results)
        paginated = all_results[offset : offset + limit]

        return {
            "query": query,
            "scope": scope.value,
            "filters": {
                "data_type": data_type,
                "is_pii": is_pii,
                "team": team,
            },
            "total": total,
            "limit": limit,
            "offset": offset,
            "results": paginated,
        }

    def _search_fields(
        self,
        fields: list[dict[str, Any]],
        query: str,
        scope: SearchScope,
        data_type: str | None,
        is_pii: bool | None,
        team: str | None,
    ) -> list[dict[str, Any]]:
        """Search through fields."""
        results = []

        for field in fields:
            relevance = 0

            # Apply filters first
            if data_type and field.get("data_type") != data_type:
                continue
            if is_pii is not None and field.get("is_pii") != is_pii:
                continue
            if team and field.get("publisher_team") != team:
                continue

            # Calculate relevance score
            name_lower = field["name"].lower()
            desc_lower = (field.get("description") or "").lower()
            dataset_lower = field.get("dataset", "").lower()

            # Exact name match - highest score
            if query == name_lower:
                relevance = 100
            # Name starts with query
            elif name_lower.startswith(query):
                relevance = 80
            # Query in name
            elif scope in (SearchScope.ALL, SearchScope.FIELDS) and query in name_lower:
                relevance = 60
            # Query in description
            elif scope in (SearchScope.ALL, SearchScope.DESCRIPTIONS) and query in desc_lower:
                relevance = 40
            # Query in dataset name
            elif scope == SearchScope.ALL and query in dataset_lower:
                relevance = 20
            else:
                continue

            result = field.copy()
            result["_relevance"] = relevance
            results.append(result)

        return results

    def _search_datasets(
        self,
        datasets: list[dict[str, Any]],
        query: str,
        scope: SearchScope,
        team: str | None,
    ) -> list[dict[str, Any]]:
        """Search through datasets."""
        results = []

        for dataset in datasets:
            relevance = 0

            # Apply team filter
            if team and dataset.get("publisher_team") != team:
                continue

            name_lower = dataset["name"].lower()
            desc_lower = (dataset.get("description") or "").lower()

            # Exact name match
            if query == name_lower:
                relevance = 100
            # Name starts with query
            elif name_lower.startswith(query):
                relevance = 80
            # Query in name
            elif scope in (SearchScope.ALL, SearchScope.DATASETS) and query in name_lower:
                relevance = 60
            # Query in description
            elif scope in (SearchScope.ALL, SearchScope.DESCRIPTIONS) and query in desc_lower:
                relevance = 40
            # Query in tags
            elif scope == SearchScope.ALL and any(
                query in tag.lower() for tag in dataset.get("tags", [])
            ):
                relevance = 30
            else:
                continue

            result = dataset.copy()
            result["_relevance"] = relevance
            results.append(result)

        return results

    async def suggest(self, prefix: str, limit: int = 10) -> dict[str, Any]:
        """
        Get autocomplete suggestions for a prefix.

        Args:
            prefix: Prefix to match
            limit: Maximum suggestions

        Returns:
            Suggestions grouped by type
        """
        dictionary = await self.aggregator.get_full_dictionary()
        prefix_lower = prefix.lower().strip()

        # Collect matching field names
        field_names = set()
        for field in dictionary["fields"]:
            if field["name"].lower().startswith(prefix_lower):
                field_names.add(field["name"])

        # Collect matching dataset names
        dataset_names = set()
        for dataset in dictionary["datasets"]:
            if dataset["name"].lower().startswith(prefix_lower):
                dataset_names.add(dataset["name"])

        # Collect matching team names
        team_names = set()
        for team in dictionary["teams"]:
            if team.lower().startswith(prefix_lower):
                team_names.add(team)

        return {
            "prefix": prefix,
            "suggestions": {
                "fields": sorted(field_names)[:limit],
                "datasets": sorted(dataset_names)[:limit],
                "teams": sorted(team_names)[:limit],
            },
        }

    async def get_pii_fields(self, team: str | None = None) -> list[dict[str, Any]]:
        """
        Get all PII fields, optionally filtered by team.

        Args:
            team: Optional team filter

        Returns:
            List of PII fields
        """
        dictionary = await self.aggregator.get_full_dictionary()

        pii_fields = dictionary["pii_fields"]

        if team:
            pii_fields = [f for f in pii_fields if f.get("publisher_team") == team]

        return pii_fields

    async def get_fields_by_type(self, data_type: str) -> list[dict[str, Any]]:
        """
        Get all fields of a specific data type.

        Args:
            data_type: Data type to filter by

        Returns:
            List of fields with the specified type
        """
        dictionary = await self.aggregator.get_full_dictionary()

        return [
            field
            for field in dictionary["fields"]
            if field.get("data_type") == data_type
        ]
