"""API routes for Dictionary Service."""

from dictionary_service.api.routes.dictionary import router as dictionary_router
from dictionary_service.api.routes.search import router as search_router
from dictionary_service.api.routes.erd import router as erd_router

__all__ = ["dictionary_router", "search_router", "erd_router"]
