"""Dictionary API routes."""

from fastapi import APIRouter, HTTPException, Query

from dictionary_service.services.aggregator import DictionaryAggregator

router = APIRouter()


@router.get("")
async def get_dictionary():
    """
    Get the full data dictionary.

    Returns all datasets, fields, teams, and summary statistics.
    """
    aggregator = DictionaryAggregator()
    try:
        dictionary = await aggregator.get_full_dictionary()
        return dictionary
    finally:
        await aggregator.close()


@router.get("/summary")
async def get_dictionary_summary():
    """
    Get summary statistics for the data dictionary.

    Returns high-level counts without full field details.
    """
    aggregator = DictionaryAggregator()
    try:
        dictionary = await aggregator.get_full_dictionary()
        return {
            "summary": dictionary["summary"],
            "teams": dictionary["teams"],
        }
    finally:
        await aggregator.close()


@router.get("/datasets")
async def list_datasets(
    team: str | None = Query(None, description="Filter by publisher team"),
    status: str | None = Query(None, description="Filter by status (active, deprecated)"),
):
    """
    List all datasets in the dictionary.

    Optional filters by team and status.
    """
    aggregator = DictionaryAggregator()
    try:
        dictionary = await aggregator.get_full_dictionary()

        datasets = dictionary["datasets"]

        if team:
            datasets = [d for d in datasets if d.get("publisher_team") == team]

        if status:
            datasets = [d for d in datasets if d.get("status") == status]

        return {
            "datasets": datasets,
            "total": len(datasets),
        }
    finally:
        await aggregator.close()


@router.get("/datasets/{dataset_name}")
async def get_dataset_details(dataset_name: str):
    """
    Get detailed information about a specific dataset.

    Includes fields, quality metrics, subscribers, and access configuration.
    """
    aggregator = DictionaryAggregator()
    try:
        details = await aggregator.get_dataset_details(dataset_name)
        if not details:
            raise HTTPException(
                status_code=404,
                detail=f"Dataset '{dataset_name}' not found",
            )
        return details
    finally:
        await aggregator.close()


@router.get("/teams")
async def list_teams():
    """
    List all teams in the data dictionary.

    Returns teams that either publish or subscribe to datasets.
    """
    aggregator = DictionaryAggregator()
    try:
        dictionary = await aggregator.get_full_dictionary()
        return {
            "teams": dictionary["teams"],
            "total": len(dictionary["teams"]),
        }
    finally:
        await aggregator.close()


@router.get("/teams/{team}/datasets")
async def get_team_datasets(team: str):
    """
    Get all datasets owned by a specific team.
    """
    aggregator = DictionaryAggregator()
    try:
        datasets = await aggregator.get_team_datasets(team)
        return {
            "team": team,
            "datasets": datasets,
            "total": len(datasets),
        }
    finally:
        await aggregator.close()


@router.get("/fields")
async def list_fields(
    team: str | None = Query(None, description="Filter by publisher team"),
    data_type: str | None = Query(None, description="Filter by data type"),
    is_pii: bool | None = Query(None, description="Filter by PII flag"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """
    List all fields across all datasets.

    Optional filters by team, data type, and PII flag.
    """
    aggregator = DictionaryAggregator()
    try:
        dictionary = await aggregator.get_full_dictionary()

        fields = dictionary["fields"]

        if team:
            fields = [f for f in fields if f.get("publisher_team") == team]

        if data_type:
            fields = [f for f in fields if f.get("data_type") == data_type]

        if is_pii is not None:
            fields = [f for f in fields if f.get("is_pii") == is_pii]

        total = len(fields)
        paginated = fields[offset : offset + limit]

        return {
            "fields": paginated,
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    finally:
        await aggregator.close()


@router.get("/fields/pii")
async def list_pii_fields(
    team: str | None = Query(None, description="Filter by publisher team"),
):
    """
    List all PII fields across all datasets.

    This is a convenience endpoint for compliance and security audits.
    """
    aggregator = DictionaryAggregator()
    try:
        dictionary = await aggregator.get_full_dictionary()

        pii_fields = dictionary["pii_fields"]

        if team:
            pii_fields = [f for f in pii_fields if f.get("publisher_team") == team]

        return {
            "pii_fields": pii_fields,
            "total": len(pii_fields),
        }
    finally:
        await aggregator.close()


@router.get("/lineage/{dataset_name}/{field_name}")
async def get_field_lineage(dataset_name: str, field_name: str):
    """
    Get lineage information for a specific field.

    Shows upstream dependencies, downstream dependents, and similar fields.
    """
    aggregator = DictionaryAggregator()
    try:
        lineage = await aggregator.get_field_lineage(dataset_name, field_name)

        if "error" in lineage:
            raise HTTPException(
                status_code=404,
                detail=lineage["error"],
            )

        return lineage
    finally:
        await aggregator.close()


@router.get("/relationships")
async def list_relationships():
    """
    List all relationships (foreign keys) between datasets.
    """
    aggregator = DictionaryAggregator()
    try:
        dictionary = await aggregator.get_full_dictionary()

        return {
            "relationships": dictionary["relationships"],
            "total": len(dictionary["relationships"]),
        }
    finally:
        await aggregator.close()
