"""Search API routes."""

from fastapi import APIRouter, Query

from dictionary_service.services.aggregator import DictionaryAggregator
from dictionary_service.services.search_service import SearchService, SearchScope

router = APIRouter()


@router.get("")
async def search(
    q: str = Query(..., min_length=1, description="Search query"),
    scope: SearchScope = Query(SearchScope.ALL, description="Search scope"),
    data_type: str | None = Query(None, description="Filter by data type"),
    is_pii: bool | None = Query(None, description="Filter by PII flag"),
    team: str | None = Query(None, description="Filter by publisher team"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """
    Search across the data dictionary.

    Searches through field names, dataset names, and descriptions.
    Results are ranked by relevance.
    """
    aggregator = DictionaryAggregator()
    try:
        search_service = SearchService(aggregator)
        results = await search_service.search(
            query=q,
            scope=scope,
            data_type=data_type,
            is_pii=is_pii,
            team=team,
            limit=limit,
            offset=offset,
        )
        return results
    finally:
        await aggregator.close()


@router.get("/suggest")
async def suggest(
    prefix: str = Query(..., min_length=1, description="Prefix for autocomplete"),
    limit: int = Query(10, ge=1, le=50),
):
    """
    Get autocomplete suggestions for a prefix.

    Returns suggestions grouped by type (fields, datasets, teams).
    """
    aggregator = DictionaryAggregator()
    try:
        search_service = SearchService(aggregator)
        suggestions = await search_service.suggest(prefix=prefix, limit=limit)
        return suggestions
    finally:
        await aggregator.close()


@router.get("/fields/type/{data_type}")
async def search_by_type(data_type: str):
    """
    Get all fields of a specific data type.

    Useful for finding all UUID fields, all timestamp fields, etc.
    """
    aggregator = DictionaryAggregator()
    try:
        search_service = SearchService(aggregator)
        fields = await search_service.get_fields_by_type(data_type)
        return {
            "data_type": data_type,
            "fields": fields,
            "total": len(fields),
        }
    finally:
        await aggregator.close()
