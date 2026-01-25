"""ERD (Entity Relationship Diagram) API routes."""

from fastapi import APIRouter, Query
from fastapi.responses import PlainTextResponse

from dictionary_service.services.aggregator import DictionaryAggregator
from dictionary_service.services.erd_generator import ERDGenerator

router = APIRouter()


@router.get("/mermaid", response_class=PlainTextResponse)
async def get_mermaid_erd(
    team: str | None = Query(None, description="Filter by publisher team"),
    include_subscribers: bool = Query(False, description="Include subscription relationships"),
):
    """
    Generate ERD in Mermaid syntax.

    Returns a Mermaid diagram definition that can be rendered
    using Mermaid.js or compatible tools.
    """
    aggregator = DictionaryAggregator()
    try:
        erd_generator = ERDGenerator(aggregator)
        mermaid = await erd_generator.generate_mermaid(
            team=team,
            include_subscribers=include_subscribers,
        )
        return mermaid
    finally:
        await aggregator.close()


@router.get("/json")
async def get_json_erd(
    team: str | None = Query(None, description="Filter by publisher team"),
    include_subscribers: bool = Query(True, description="Include subscription edges"),
):
    """
    Generate ERD as JSON structure.

    Returns nodes and edges suitable for visualization
    with React Flow, D3.js, or similar libraries.
    """
    aggregator = DictionaryAggregator()
    try:
        erd_generator = ERDGenerator(aggregator)
        erd_json = await erd_generator.generate_json(
            team=team,
            include_subscribers=include_subscribers,
        )
        return erd_json
    finally:
        await aggregator.close()


@router.get("/plantuml", response_class=PlainTextResponse)
async def get_plantuml_erd(
    team: str | None = Query(None, description="Filter by publisher team"),
):
    """
    Generate ERD in PlantUML syntax.

    Returns a PlantUML diagram definition that can be rendered
    using PlantUML or compatible tools.
    """
    aggregator = DictionaryAggregator()
    try:
        erd_generator = ERDGenerator(aggregator)
        plantuml = await erd_generator.generate_plantuml(team=team)
        return plantuml
    finally:
        await aggregator.close()
