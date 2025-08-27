# src/libriscribe2/agents/researcher.py
import logging
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup, Tag

from ..settings import Settings
from ..utils import prompts_context as prompts
from ..utils.file_utils import write_markdown_file
from ..utils.llm_client_protocol import LLMClientProtocol
from .agent_base import Agent

logger = logging.getLogger(__name__)


class ResearcherAgent(Agent):
    """Conducts web research."""

    def __init__(self, llm_client: LLMClientProtocol, settings: Settings):
        super().__init__("ResearcherAgent", llm_client, settings)

    async def execute(self, project_knowledge_base: Any, output_path: str | None = None, **kwargs: Any) -> None:
        """Performs web research and saves the results to a Markdown file."""
        try:
            # Extract query from kwargs
            query = kwargs.get("query")
            if query is None:
                self.log_error("Error: query is required")
                return

            self.log_info(f"Researching: {query}")

            # Load language from project_data.json if available
            language = self._get_project_language(output_path or "")

            prompt = prompts.RESEARCH_PROMPT.format(query=query, language=language)
            llm_summary = await self.safe_generate_content(prompt, prompt_type="research")

            if not llm_summary:
                self.log_error("Failed to generate research summary")
                return

            # Basic web scraping
            search_results = self.scrape_google_search(query)
            scraped_content = self._format_search_results(search_results)

            # Combine LLM summary and scraped content
            final_report = f"# Research Report: {query}\n\n## AI-Generated Summary\n\n{llm_summary}\n\n## Web Search Results\n\n{scraped_content}"
            if output_path:
                write_markdown_file(output_path, final_report)
            self.log_success(f"Research report saved to {output_path}")

        except Exception as e:
            self.log_error(f"Error during research for query '{query}': {e}")
            logger.exception(f"Error during research for query '{query}': {e}")

    def _get_project_language(self, output_path: str) -> str:
        """Get language from project data or return default."""
        try:
            project_dir = Path(output_path).parent
            project_data_path = project_dir / self.settings.project_data_filename
            if project_data_path.exists():
                from ..knowledge_base import ProjectKnowledgeBase

                project_kb = ProjectKnowledgeBase.load_from_file(str(project_data_path))
                if project_kb and hasattr(project_kb, "language"):
                    # Cast the attribute to `str` to satisfy mypy
                    # return typing.cast(str, project_kb.language)
                    return project_kb.language
        except Exception as e:
            self.logger.warning(f"Could not load project data for language detection: {e}")
        return self.settings.default_language

    def _format_search_results(self, search_results: list[dict[str, str]]) -> str:
        """Format search results as markdown."""
        if not search_results:
            return "No search results found."

        formatted_content = ""
        for result in search_results:
            formatted_content += f"### [{result['title']}]({result['url']})\n\n"
            formatted_content += f"{result['snippet']}\n\n"
        return formatted_content

    def scrape_google_search(self, query: str, num_results: int = 5) -> list[dict[str, str]]:
        """Scrapes Google Search results for a given query."""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            url = f"https://www.google.com/search?q={query}&num={num_results}"
            response = requests.get(
                url,
                headers=headers,
                timeout=30,  # Default timeout
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            results = []

            for g in soup.find_all("div", class_="tF2Cxc"):
                if not isinstance(g, Tag):
                    continue
                try:
                    result = self._extract_search_result(g)
                    if result:
                        results.append(result)
                except Exception as e:
                    self.logger.warning(f"Error parsing a search result: {e}")
                    continue

            return results
        except requests.exceptions.RequestException as e:
            self.log_error(f"Could not perform web search: {e}")
            return []
        except Exception as e:
            self.logger.exception(f"An unexpected error occurred during google scraping: {e}")
            return []

    def _extract_search_result(self, element: Tag) -> dict[str, str]:
        """Extract search result data from a BeautifulSoup element."""
        anchor = element.find("a")
        if anchor is None or not isinstance(anchor, Tag):
            return {}

        link = anchor.get("href", "")
        if not link:
            return {}

        title_elem = element.find("h3")
        if title_elem is None or not isinstance(title_elem, Tag):
            return {}
        title = title_elem.get_text()

        snippet_elem = element.find("div", class_="VwiC3b")
        if snippet_elem is None or not isinstance(snippet_elem, Tag):
            return {}
        snippet = snippet_elem.get_text()

        return {"title": str(title), "url": str(link), "snippet": str(snippet)}
