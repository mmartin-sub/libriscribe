# src/libriscribe/agents/concept_generator.py
import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from pathlib import Path

from libriscribe.utils.llm_client import LLMClient
from libriscribe.utils import prompts_context as prompts
from libriscribe.agents.agent_base import Agent
from libriscribe.utils.file_utils import extract_json_from_markdown, read_json_file, write_json_file
from libriscribe.knowledge_base import ProjectKnowledgeBase
#No need to import track
from rich.console import Console #NEW IMPORT

console = Console() # Create a console instance.
logger = logging.getLogger(__name__)

class ConceptGeneratorAgent(Agent):
    """Generates book concepts."""

    def __init__(self, llm_client: LLMClient):
        super().__init__("ConceptGeneratorAgent", llm_client)

    def execute(self, project_knowledge_base: ProjectKnowledgeBase, output_path: Optional[str] = None) -> None:
        """Generates a book concept, with critique and refinement."""
        try:
            # --- Step 1: Initial Concept Generation (Simplified) ---
            if project_knowledge_base.book_length == "Short Story":
                initial_prompt = f"""Generate a concise book concept for a {project_knowledge_base.genre} {project_knowledge_base.category} short story.
                    The book should be written in {project_knowledge_base.language}.

                    Initial ideas: {project_knowledge_base.description}.

                    Return a JSON object within a Markdown code block.  Include:
                    - "title":  A compelling title.
                    - "logline": A one-sentence summary.
                    - "description": A short description (around 100-150 words).

                    ```json
                    {
                        "title": "...",
                        "logline": "...",
                        "description": "..."
                    }
                    ```"""
            else:
                initial_prompt = f"""Generate a book concept for a {project_knowledge_base.genre} {project_knowledge_base.category} ({project_knowledge_base.book_length}).
                The book should be written in {project_knowledge_base.language}.

                Initial ideas: {project_knowledge_base.description}.

                Return a JSON object within a Markdown code block. Include:
                - "title": A title.
                - "logline": A one-sentence summary.
                - "description": A description (around 200 words).

                ```json
                {{
                    "title": "...",
                    "logline": "...",
                    "description": "..."
                }}
                ```"""

            console.print(f"🧠 [cyan]Generating initial concept...[/cyan]")
            initial_concept_md = self.llm_client.generate_content_with_json_repair(initial_prompt)

            if not initial_concept_md:
                logger.error("Initial concept generation failed.")
                return None

            initial_concept_json = extract_json_from_markdown(initial_concept_md)
            if not initial_concept_json:
                logger.error("Initial concept parsing failed.")
                return None

            # --- Step 2: Critique the Concept ---
            critique_prompt = f"""Critique the following book concept:

            ```json
            {json.dumps(initial_concept_json)}
            ```
            The book should be written in {project_knowledge_base.language}.

            Evaluate:
            - **Title:** Is it compelling and relevant?
            - **Logline:** Is it concise and does it capture the core conflict?
            - **Description:** Is it well-written, engaging, and does it provide a clear sense of the story?  Are there any obvious weaknesses or areas for improvement? Be specific and constructive.
            """
            console.print(f"🔍 [cyan]Evaluating concept quality...[/cyan]")
            critique = self.llm_client.generate_content(critique_prompt)
            if not critique:
                logger.error("Critique generation failed.")
                return None


            # --- Step 3: Refine the Concept ---
            refine_prompt = f"""Refine the book concept based on the critique.  Address the weaknesses and improve the concept.
            The book should be written in {project_knowledge_base.language}.

            Original Concept:
            ```json
            {json.dumps(initial_concept_json)}
            ```

            Critique:
            {critique}

            Return the REFINED concept as a JSON object within a Markdown code block:
             ```json
            {{
                "title": "...",
                "logline": "...",
                "description": "..."
            }}
            ```
            """
            console.print(f"✨ [cyan]Refining concept...[/cyan]")
            refined_concept_md = self.llm_client.generate_content_with_json_repair(refine_prompt)
            if not refined_concept_md:
                logger.error("Refined concept generation failed.")
                return None

            refined_concept_json = extract_json_from_markdown(refined_concept_md)
            if not refined_concept_json:
                logger.error("Refined concept parsing failed")
                return None

            # --- Step 4: Update ProjectData (using refined concept) ---
            if 'title' in refined_concept_json:
                project_knowledge_base.title = refined_concept_json['title']
            if 'logline' in refined_concept_json:
                project_knowledge_base.logline = refined_concept_json['logline']
            if 'description' in refined_concept_json:
                project_knowledge_base.description = refined_concept_json['description']

            # --- Step 5: Generate Keywords ---
            console.print(f"🔑 [cyan]Generating keywords from description...[/cyan]")
            keyword_prompt = prompts.KEYWORD_GENERATION_PROMPT.format(
                title=project_knowledge_base.title,
                description=project_knowledge_base.description,
                language=project_knowledge_base.language
            )
            keyword_response = self.llm_client.generate_content(keyword_prompt, model=prompts.KEYWORD_GENERATION_PROMPT_MODEL)
            if not keyword_response:
                logger.warning("Keyword generation failed. No keywords will be added.")
            else:
                keywords_md = keyword_response.strip() # Assuming the LLM response is already in markdown format
                keywords_json = extract_json_from_markdown(keywords_md)
                if keywords_json and isinstance(keywords_json, list):
                    # Ensure all items are strings
                    keywords_list = [str(item) for item in keywords_json]
                    # --- Step 6: Update ProjectKnowledgeBase with keywords ---
                    project_knowledge_base.keywords = keywords_list
                    logger.info(f"Keywords generated: {project_knowledge_base.keywords}")
                    console.print(f"[green]✅ Keywords generated: {', '.join(keywords_list)}[/green]")
                else:
                    logger.warning(f"Keyword parsing failed. Could not extract list from: {keywords_md}")
                    console.print("[yellow]Could not parse keywords from AI response.[/yellow]")

            logger.info(f"Concept generated (refined): Title: {project_knowledge_base.title}, Logline: {project_knowledge_base.logline}")

        except Exception as e:
            self.logger.exception(f"Error generating concept: {e}")
            print(f"ERROR: Failed to generate concept. See log for details.")
            return None