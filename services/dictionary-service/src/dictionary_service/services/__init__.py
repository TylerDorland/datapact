"""Services module for Dictionary Service."""

from dictionary_service.services.aggregator import DictionaryAggregator
from dictionary_service.services.search_service import SearchService
from dictionary_service.services.erd_generator import ERDGenerator

__all__ = ["DictionaryAggregator", "SearchService", "ERDGenerator"]
