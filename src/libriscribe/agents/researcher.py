# src/libriscribe/agents/researcher.py
import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from pathlib import Path

from libriscribe.utils.llm_client import LLMClient
from libriscribe.utils import prompts_context as prompts
from libriscribe.agents.agent_base import Agent
from libriscribe.utils.file_utils import write_markdown_file
from rich.console import Console
import requests
from bs4 import BeautifulSoup

console = Console()
# Third-party imports for web scraping (requests and BeautifulSoup)


logger = logging.getLogger(__name__)

class ResearcherAgent(Agent):
    """Conducts web research."""

    def __init__(self, llm_client: LLMClient):
        super().__init__("ResearcherAgent", llm_client)

    def execute(self, query: str, output_path: str) -> None:
        """Performs web research and saves the results to a Markdown file."""

        try:
            # Use LLM to generate initial research summary
            console.print(f"🔎 [cyan]Researching: {query}...[/cyan]")

            # --- Load language from project_data.json if available ---
            from pathlib import Path
            language = "English"  # Default
            try:
                project_dir = Path(output_path).parent
                project_data_path = project_dir / "project_data.json"
                if project_data_path.exists():
                    from libriscribe.knowledge_base import ProjectKnowledgeBase
                    project_kb = ProjectKnowledgeBase.load_from_file(str(project_data_path))
                    if project_kb and hasattr(project_kb, 'language'):
                        language = project_kb.language
            except Exception as e:
                self.logger.warning(f"Could not load project data for language detection: {e}")
                # Continue with default language

            prompt = prompts.RESEARCH_PROMPT.format(query=query, language=language)
            llm_summary = self.llm_client.generate_content(prompt, model=prompts.RESEARCH_PROMPT_MODEL) # , max_tokens=1000

            # Basic web scraping (example with Google Search - adapt as needed)
            search_results = self.scrape_google_search(query)
            scraped_content = ""
            for result in search_results:
                scraped_content += f"### [{result['title']}]({result['url']})\n\n"
                scraped_content += f"{result['snippet']}\n\n"

            # Combine LLM summary and scraped content
            final_report = f"# Research Report: {query}\n\n## AI-Generated Summary\n\n{llm_summary}\n\n## Web Search Results\n\n{scraped_content}"
            write_markdown_file(output_path, final_report)

        except Exception as e:
            self.logger.exception(f"Error during research for query '{query}': {e}")
            print(f"ERROR: Failed to perform research for '{query}'. See log.")


    def scrape_google_search(self, query: str, num_results: int = 5) -> List[Dict[str, str]]:
        """Scrapes Google Search results for a given query."""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            url = f"https://www.google.com/search?q={query}&num={num_results}"
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

            soup = BeautifulSoup(response.text, "html.parser")
            results = []

            for g in soup.find_all('div', class_='tF2Cxc'):  # Updated class based on recent Google Search layout
                try:  # Handle cases where elements might be missing
                    anchor = g.find('a')
                    link = anchor['href']
                    title = g.find('h3').text  # Extract text from h3 tag
                    snippet = g.find('div', class_='VwiC3b').text  # Updated class for snippet
                    results.append({'title': title, 'url': link, 'snippet': snippet})
                except Exception as e:
                    self.logger.warning(f"Error parsing a search result: {e}") # Log the specific error, but continue
                    continue

            return results
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error during Google Search scraping: {e}")
            print(f"ERROR: Could not perform web search: {e}")
            return []  # Return an empty list on error
        except Exception as e:
             self.logger.exception(f"An unexpected error occurred during google scraping {e}")
             return []