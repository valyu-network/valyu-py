"""
Base provider implementation.
"""

from __future__ import annotations

import json
import typing as t
from abc import ABC, abstractmethod

from ..api import Valyu as ValyuClient
from .types import Modifiers, Tool, ToolExecutionResponse

T = t.TypeVar("T")
U = t.TypeVar("U")


class BaseProvider(ABC, t.Generic[T, U]):
    """Base provider class"""

    def __init__(self):
        pass

    @abstractmethod
    def wrap_tool(self, tool: Tool) -> T:
        """Wrap a tool into provider-specific format"""
        pass

    @abstractmethod
    def wrap_tools(self, tools: t.Sequence[Tool]) -> U:
        """Wrap multiple tools into provider-specific format"""
        pass

    def execute_tool(
        self,
        slug: str,
        arguments: t.Dict[str, t.Any],
        modifiers: t.Optional[Modifiers] = None,
    ) -> ToolExecutionResponse:
        """Execute a tool by slug"""
        if slug == "valyu_search":
            return self._execute_valyu_search(arguments)
        else:
            return ToolExecutionResponse(output=None, error=f"Unknown tool: {slug}")

    def _execute_valyu_search(
        self, arguments: t.Dict[str, t.Any]
    ) -> ToolExecutionResponse:
        """Execute Valyu search"""
        try:
            # This will be set by the concrete provider
            if not hasattr(self, "_valyu_client"):
                return ToolExecutionResponse(
                    output=None, error="Valyu client not initialized"
                )

            # Remove None values for the API call
            clean_args = {k: v for k, v in arguments.items() if v is not None}
            print(f"Executing search with args: {clean_args}")
            search_result = self._valyu_client.search(**clean_args)

            print(f"Search result: {search_result}")

            return ToolExecutionResponse(output=search_result.model_dump())
        except Exception as e:
            return ToolExecutionResponse(output=None, error=str(e))

    def get_available_tools(self) -> t.List[Tool]:
        """Get available Valyu tools"""
        return [
            Tool(
                slug="valyu_search",
                description="Performs a deep search using the Valyu Deepsearch API to find relevant information from academic papers, news, financial market data, and authoritative sources.",
                input_parameters={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query to perform",
                        },
                        "max_num_results": {
                            "type": ["integer", "null"],
                            "description": "The maximum number of results to return (1-20)",
                        },
                        "included_sources": {
                            "type": ["array", "null"],
                            "description": "Search over specific sources, can pass a domain (e.g. news.ycombinator.com), a url (e.g. https://arxiv.org/abs/1706.03762), or a specific valyu dataset (e.g. valyu/valyu-arxiv, wiley/wiley-finance-books). For most cases, do not use unless the user asks for it.",
                            "items": {"type": "string"},
                        },
                        "excluded_sources": {
                            "type": ["array", "null"],
                            "description": "Select specific sources to exclude from the search, can pass a domain (e.g. news.ycombinator.com), a url (e.g. https://arxiv.org/abs/1706.03762), or a specific valyu dataset (e.g. valyu/valyu-arxiv, wiley/wiley-finance-book). For most cases, do not use unless the user asks for it.",
                            "items": {"type": "string"},
                        },
                        "category": {
                            "type": ["string", "null"],
                            "description": "Natural language category/guide phrase to help guide the search to the most relevant content. For example 'agentic use-cases'",
                        },
                        "start_date": {
                            "type": ["string", "null"],
                            "description": "The start date of the search in the format YYYY-MM-DD",
                        },
                        "end_date": {
                            "type": ["string", "null"],
                            "description": "The end date of the search in the format YYYY-MM-DD",
                        },
                        "relevance_threshold": {
                            "type": ["number", "null"],
                            "description": "The relevance threshold of the search in the range of 0-1, default is 0.5, you can set to >0.7 for only hyper-relevant results",
                        },
                        "response_length": {
                            "type": ["string", "integer", "null"],
                            "description": "The length of the response. Can be 'short', 'medium', 'large', 'max', or an integer (for character length). Default is max. Only use this if the user asks for it, e.g. to not use much input tokens.",
                        },
                    },
                    "required": ["query"],
                    "additionalProperties": False,
                },
            )
        ]
