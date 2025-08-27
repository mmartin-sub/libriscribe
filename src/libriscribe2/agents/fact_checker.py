# src/libriscribe2/agents/fact_checker.py
import logging
from typing import Any

# For web scraping
from rich.console import Console

from ..settings import Settings
from ..utils.file_utils import extract_json_from_markdown, read_markdown_file
from ..utils.llm_client_protocol import LLMClientProtocol
from .agent_base import Agent

console = Console()

logger = logging.getLogger(__name__)


class FactCheckerAgent(Agent):
    """Checks factual claims in a chapter."""

    def __init__(self, llm_client: LLMClientProtocol, settings: Settings):
        super().__init__("FactCheckerAgent", llm_client, settings)

    async def execute(self, project_knowledge_base: Any, output_path: str | None = None, **kwargs: Any) -> None:
        """Identifies and checks factual claims, handling Markdown-wrapped JSON."""

        # Extract chapter_path from kwargs
        chapter_path = kwargs.get("chapter_path")
        if chapter_path is None:
            console.print("[red]Error: chapter_path is required[/red]")
            return

        chapter_content = read_markdown_file(chapter_path)
        if not chapter_content:
            print(f"ERROR: Chapter file is empty or not found: {chapter_path}")
            return

        # 1. Identify Claims
        console.print(f"🔍 [cyan]Verifying facts in Chapter {chapter_path.split('_')[-1].split('.')[0]}...[/cyan]")

        identify_claims_prompt = f"""
        You are an expert fact-checker.  Identify all statements in the following text that make factual claims
        that could be verified or refuted.  Do *not* include subjective statements, opinions, or purely fictional elements
        (unless they claim to be based on reality). Output the claims as a JSON array of strings.

        Chapter Content:

        ---

        {chapter_content}

        ---
        """

        try:
            claims_json_str = await self.llm_client.generate_content(identify_claims_prompt)  # , max_tokens=1000
            claims = extract_json_from_markdown(claims_json_str)
            if claims is None:
                print("ERROR: Invalid claims data received.")
                return
            if not isinstance(claims, list):
                self.logger.warning("Claims JSON is not a list.")
                claims = []

            # 2. Check each claim
            fact_check_results = []
            for claim in claims:
                check_result = await self.check_claim(claim)
                fact_check_results.append(check_result)

            # Save results if output_path provided
            if output_path:
                try:
                    from ..utils.file_utils import write_json_file

                    results_dict = {"fact_check_results": fact_check_results}
                    write_json_file(output_path, results_dict)
                    console.print(f"[green]✅ Fact check results saved to {output_path}[/green]")
                except Exception as e:
                    console.print(f"[red]Error saving fact check results: {e}[/red]")

        except Exception as e:
            self.logger.exception(f"Error during fact-checking process for {chapter_path}: {e}")
            print(f"ERROR: Failed to fact-check chapter {chapter_path}.  See log.")

    async def check_claim(self, claim: str) -> dict[str, Any]:
        """Checks a single claim, handling Markdown-wrapped JSON."""
        prompt = f"""
        Fact-check the following claim:

        "{claim}"

        Provide a concise assessment of its accuracy (e.g., "True," "False," "Mostly True," "Unverifiable," "Out of Context").
        Include a brief explanation and, if possible, provide URLs to reputable sources that support your assessment.
        Output as JSON: {{"result": "...", "explanation": "...", "sources": ["url1", "url2"]}}
        """

        try:
            result_json_str = await self.llm_client.generate_content(prompt)  # , max_tokens=500
            result = extract_json_from_markdown(result_json_str)
            if result is None:
                return {
                    "claim": claim,
                    "result": "Error",
                    "explanation": "Failed to parse LLM Response",
                    "sources": [],
                }
            if not isinstance(result, dict):
                self.logger.warning("Fact-check result JSON is not a dictionary.")
                result = {
                    "claim": claim,
                    "result": "Error",
                    "explanation": "Failed to parse LLM Response",
                    "sources": [],
                }  # Use default dict
            else:
                # Add the original claim for context
                result["claim"] = claim
            return result

        except Exception as e:
            self.logger.exception(f"Error while checking claim: {e}")
            return {
                "claim": claim,
                "result": "Error",
                "explanation": str(e),
                "sources": [],
            }
