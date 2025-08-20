# src/libriscribe2/agents/concept_generator.py
import logging
import re
from datetime import datetime
from typing import Any, cast

import pyjson5 as json

from ..knowledge_base import ProjectKnowledgeBase
from ..settings import Settings
from ..utils.file_utils import write_json_file, write_markdown_file
from ..utils.json_utils import JSONProcessor
from ..utils.llm_client import LLMClient
from ..utils.markdown_processor import remove_h3_from_markdown
from .agent_base import Agent


def validate_content(content: str | None) -> None:
    """Validate that the content is not null or contains only code block markers."""
    if content is None:
        raise ValueError("Content cannot be null")
    # Guard against incorrect mock types or unexpected inputs
    if not isinstance(content, str):
        raise ValueError("Content must be a string")
    if content.strip() == "```":
        raise ValueError("Content cannot be only code block markers")


logger = logging.getLogger(__name__)


class ConceptGeneratorAgent(Agent):
    """Generates book concepts."""

    def __init__(self, llm_client: LLMClient, settings: Settings):
        super().__init__("ConceptGeneratorAgent", llm_client)
        self.settings = settings

    def _validate_prompt_length(self, prompt: str, prompt_type: str) -> bool:
        """Validate that prompt length is within acceptable limits."""
        if len(prompt) > self.settings.max_prompt_length:
            self.logger.warning(
                f"{prompt_type} prompt too long: {len(prompt)} chars (max: {self.settings.max_prompt_length})"
            )
            return False
        return True

    def _validate_concept_json(self, concept_json: dict[str, Any]) -> bool:
        """Validate concept JSON structure and content."""
        required_fields = ["title", "logline", "description"]

        # Check required fields
        for field in required_fields:
            if field not in concept_json:
                self.logger.error(f"Missing required field in concept: {field}")
                return False
            if not isinstance(concept_json[field], str):
                self.logger.error(f"Field {field} must be a string, got {type(concept_json[field])}")
                return False
            if len(concept_json[field]) == 0:
                self.logger.error(f"Field {field} cannot be empty")
                return False

        # Check for suspicious content that might trigger content filtering
        suspicious_patterns = [
            r"\\u[0-9a-fA-F]{4}",  # Unicode escape sequences
            r"[<>]",  # HTML-like tags
            r"javascript:",  # JavaScript injection
            r"data:",  # Data URI injection
        ]

        content_str = json.dumps(concept_json, ensure_ascii=False)
        for pattern in suspicious_patterns:
            if re.search(pattern, content_str, re.IGNORECASE):
                self.logger.warning(f"Potentially suspicious content detected in concept: {pattern}")
                # Don't fail, just warn

        return True

    def _build_safe_json_string(self, concept_json: dict[str, Any]) -> str:
        """Build a safe JSON string representation with length validation."""
        try:
            json_str = cast(str, json.dumps(concept_json, ensure_ascii=False))

            # Check if JSON is too long
            if len(json_str) > self.settings.concept_json_max_len:
                self.logger.warning(f"Concept JSON too long: {len(json_str)} chars, truncating description")

                # Truncate description if it's the main culprit
                if (
                    "description" in concept_json
                    and len(concept_json["description"]) > self.settings.concept_prompt_min_len
                ):
                    truncated_desc = concept_json["description"][: self.settings.concept_prompt_min_len] + "..."
                    safe_concept = concept_json.copy()
                    safe_concept["description"] = truncated_desc
                    json_str = cast(str, json.dumps(safe_concept, ensure_ascii=False))
                    self.logger.info(f"Truncated description to {len(truncated_desc)} chars")

            return json_str
        except Exception as e:
            self.logger.error(f"Failed to serialize concept JSON: {e}")
            # Return a minimal safe version
            return cast(
                str,
                json.dumps(
                    {
                        "title": concept_json.get("title", "Unknown Title"),
                        "logline": concept_json.get("logline", "Unknown Logline"),
                        "description": concept_json.get("description", "Description unavailable")[:500],
                    },
                    ensure_ascii=False,
                ),
            )

    async def execute(
        self,
        project_knowledge_base: ProjectKnowledgeBase,
        output_path: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Generates a book concept, with critique and refinement."""
        try:
            self.log_info("Generating initial concept...")

            # Step 1: Initial Concept Generation
            initial_prompt = self._build_initial_prompt(project_knowledge_base)

            # Validate prompt length
            if not self._validate_prompt_length(initial_prompt, "initial concept"):
                self.log_warning("Initial prompt too long, using simplified version")
                initial_prompt = self._build_simple_prompt(project_knowledge_base)

            # --- FIX STARTS HERE ---
            # Added the initial generation call that was missing.
            initial_concept_md = await self.safe_generate_content(
                initial_prompt, prompt_type="concept", temperature=0.7
            )
            # --- FIX ENDS HERE ---

            # If initial generation failed, try with simplified prompt
            if not initial_concept_md:
                self.log_info("Retrying with simplified prompt...")
                simple_prompt = self._build_simple_prompt(project_knowledge_base)
                initial_concept_md = await self.safe_generate_content(
                    simple_prompt, prompt_type="concept", temperature=0.7
                )

            # If both attempts failed, raise error before validation
            if not initial_concept_md:
                error_msg = "Failed to generate book concept - no response from LLM"
                self.logger.error(f"Concept generation failed: prompt={initial_prompt[:100]}...")
                self.log_error(error_msg)  # Log to file only
                raise RuntimeError(error_msg)

            # Only validate if we have content
            validate_content(initial_concept_md)

            # Dump raw response for debugging
            self._dump_raw_response(initial_concept_md, output_path, "concept")

            initial_concept_json = self.safe_extract_json(initial_concept_md, "initial concept", output_path)
            if not initial_concept_json:
                error_msg = "Failed to parse book concept JSON"
                self.logger.error(f"JSON parsing failed for concept: {initial_concept_md[:200]}...")
                self.log_error(error_msg)  # Log to file only
                raise RuntimeError(error_msg)

            # Validate the concept JSON
            if not self._validate_concept_json(initial_concept_json):
                error_msg = "Generated concept JSON failed validation"
                self.log_error(error_msg)
                raise RuntimeError(error_msg)

            # Step 2: Critique the Concept
            critique_prompt = self._build_critique_prompt(initial_concept_json, project_knowledge_base)

            # Validate critique prompt length
            if not self._validate_prompt_length(critique_prompt, "critique"):
                self.log_warning("Critique prompt too long, using simplified version")
                critique_prompt = self._build_simple_critique_prompt(initial_concept_json, project_knowledge_base)

            self.log_info("Evaluating concept quality...")

            critique_response = await self.llm_client.generate_content_with_content_filtering_fallback(
                primary_prompt=critique_prompt,
                fallback_prompt=self._build_simple_critique_prompt(initial_concept_json, project_knowledge_base),
                prompt_type="critique",
                temperature=0.7,
                max_retries=2,
            )

            if not critique_response:
                error_msg = "Failed to critique book concept - content filtering likely blocked all attempts"
                self.log_error(error_msg)
                critique_response = "Critique unavailable due to content filtering. Proceeding with original concept."

            # Step 3: Refine the Concept
            refine_prompt = self._build_refine_prompt(initial_concept_json, critique_response, project_knowledge_base)

            if not self._validate_prompt_length(refine_prompt, "refine"):
                self.log_warning("Refine prompt too long, using simplified version")
                refine_prompt = self._build_simple_refine_prompt(
                    initial_concept_json, critique_response, project_knowledge_base
                )

            self.log_info("Refining concept...")

            refined_concept_md = await self.llm_client.generate_content_with_content_filtering_fallback(
                primary_prompt=refine_prompt,
                fallback_prompt=self._build_simple_refine_prompt(
                    initial_concept_json, critique_response, project_knowledge_base
                ),
                prompt_type="refine",
                temperature=0.7,
                max_retries=2,
            )
            validate_content(refined_concept_md)

            if not refined_concept_md:
                self.log_warning("Concept refinement failed, using original concept")
                refined_concept_md = initial_concept_md
                refined_concept_json = initial_concept_json
            else:
                self._dump_raw_response(refined_concept_md, output_path, "concept_revised")
                refined_concept_result = self.safe_extract_json(refined_concept_md, "refined concept", output_path)
                if not refined_concept_result:
                    self.log_warning("Failed to parse refined concept, using original")
                    refined_concept_json = initial_concept_json
                else:
                    refined_concept_json = refined_concept_result

            if not self._validate_concept_json(refined_concept_json):
                self.log_warning("Refined concept failed validation, using original")
                refined_concept_json = initial_concept_json

            # Step 4: Generate Keywords
            keywords_prompt = self._build_keywords_prompt(refined_concept_json, project_knowledge_base)

            if not self._validate_prompt_length(keywords_prompt, "keywords"):
                self.log_warning("Keywords prompt too long, using simplified version")
                keywords_prompt = self._build_simple_keywords_prompt(refined_concept_json, project_knowledge_base)

            self.log_info("Generating keywords from description...")

            keywords_md = await self.llm_client.generate_content_with_content_filtering_fallback(
                primary_prompt=keywords_prompt,
                fallback_prompt=self._build_simple_keywords_prompt(refined_concept_json, project_knowledge_base),
                prompt_type="keywords",
                temperature=0.7,
                max_retries=2,
            )
            validate_content(keywords_md)

            if not keywords_md:
                error_msg = "Failed to generate keywords"
                self.log_error(error_msg)
                fallback_keywords = self._generate_fallback_keywords(refined_concept_json)
                keywords_md = f"```json\n{json.dumps(fallback_keywords, indent=2, ensure_ascii=False)}\n```"

            # Process and format the keywords response
            if keywords_md:
                # Format the keywords into a clean structure
                keywords_json, raw_keywords = self._format_keywords_response(keywords_md)

                # Save the raw response for debugging
                self._dump_raw_response(keywords_md, output_path, "keywords")

                # If we couldn't extract any keywords, generate fallback ones
                if not any(keywords_json.values()):
                    self.log_warning("No valid keywords found in response, using fallback")
                    keywords_json = self._generate_fallback_keywords(refined_concept_json)
            else:
                # If no response, use fallback
                self.log_warning("No keywords generated, using fallback")
                keywords_json = self._generate_fallback_keywords(refined_concept_json)

            self._update_knowledge_base(project_knowledge_base, refined_concept_json, keywords_json)

            if output_path:
                try:
                    initial_concept_path = output_path.replace("concept.json", "1-concept.json")
                    timestamp = datetime.now().strftime("%y%m%d%H%M%S")
                    initial_concept_data = {"concept": initial_concept_json, "timestamp": timestamp}
                    write_json_file(initial_concept_path, initial_concept_data)

                    refined_concept_path = output_path.replace("concept.json", "2-concept_revised.json")
                    refined_concept_data = {
                        "concept": refined_concept_json,
                        "keywords": keywords_json,
                        "critique": critique_response,
                    }
                    write_json_file(refined_concept_path, refined_concept_data)

                    markdown_path = output_path.replace("concept.json", "2-concept_revised.md")
                    markdown_content = self._format_concept_as_markdown(
                        refined_concept_json, keywords_json, critique_response
                    )

                    try:
                        markdown_content = remove_h3_from_markdown(markdown_content, action="remove")
                        self.logger.debug("Removed level 3 headers from concept markdown")
                    except (ValueError, RuntimeError) as e:
                        self.logger.warning(f"Could not process level 3 headers in concept markdown: {e}")
                        pass

                    markdown_content = self._clean_bold_headers(markdown_content)
                    write_markdown_file(markdown_path, markdown_content)

                    self.log_success(
                        "Concept data saved (1-concept.json, 2-concept_revised.json and 2-concept_revised.md)!"
                    )
                except Exception as e:
                    self.log_error(f"Failed to save concept data: {e}")

            self.log_success("Concept generation completed successfully!")

        except Exception as e:
            self.logger.exception("Error during concept generation")
            raise e

    def _build_simple_prompt(self, project_kb: ProjectKnowledgeBase) -> str:
        """Build a simple concept generation prompt to avoid content filtering."""
        return f"""Create a book concept for a {project_kb.genre} {project_kb.category}.
        Language: {project_kb.language}
        Description: {project_kb.description}

        Return JSON with title, logline, and description.

        ```json
        {{
            "title": "Book Title",
            "logline": "One sentence summary",
            "description": "Brief description"
        }}
        ```"""

    def _build_initial_prompt(self, project_kb: ProjectKnowledgeBase) -> str:
        """Build the initial concept generation prompt."""
        project_type = project_kb.project_type

        if project_type == "short_story":
            return f"""Generate a concise book concept for a {project_kb.genre} {project_kb.category} short story.
                The book should be written in {project_kb.language}.

                Initial ideas: {project_kb.description}.

                Return a JSON object within a Markdown code block. Include:
                - "title": A compelling title.
                - "logline": A one-sentence summary.
                - "description": A short description (around 100-150 words).

                ```json
                {{
                    "title": "...",
                    "logline": "...",
                    "description": "..."
                }}
                ```"""
        elif project_type == "novella":
            return f"""Generate a book concept for a {project_kb.genre} {project_kb.category} novella.
                The book should be written in {project_kb.language}.

                Initial ideas: {project_kb.description}.

                Return a JSON object within a Markdown code block. Include:
                - "title": A compelling title.
                - "logline": A one-sentence summary.
                - "description": A description (around 150-200 words).

                ```json
                {{
                    "title": "...",
                    "logline": "...",
                    "description": "..."
                }}
                ```"""
        elif project_type == "book":
            return f"""Generate a book concept for a {project_kb.genre} {project_kb.category} book (80-150 pages).
                The book should be written in {project_kb.language}.

                Initial ideas: {project_kb.description}.

                Return a JSON object within a Markdown code block. Include:
                - "title": A compelling title.
                - "logline": A one-sentence summary.
                - "description": A description (around 180-220 words).

                ```json
                {{
                    "title": "...",
                    "logline": "...",
                    "description": "..."
                }}
                ```"""
        elif project_type == "epic":
            return f"""Generate a book concept for a {project_kb.genre} {project_kb.category} epic novel.
                The book should be written in {project_kb.language}.

                Initial ideas: {project_kb.description}.

                Return a JSON object within a Markdown code block. Include:
                - "title": A compelling title.
                - "logline": A one-sentence summary.
                - "description": A detailed description (around 250-300 words).

                ```json
                {{
                    "title": "...",
                    "logline": "...",
                    "description": "..."
                }}
                ```"""
        else:  # novel (default)
            return f"""Generate a book concept for a {project_kb.genre} {project_kb.category} novel.
                The book should be written in {project_kb.language}.

                Initial ideas: {project_kb.description}.

                Return a JSON object within a Markdown code block. Include:
                - "title": A compelling title.
                - "logline": A one-sentence summary.
                - "description": A description (around 200-250 words).

                ```json
                {{
                    "title": "...",
                    "logline": "...",
                    "description": "..."
                }}
                ```"""

    def _build_critique_prompt(self, concept_json: dict[str, Any], project_kb: ProjectKnowledgeBase) -> str:
        """Build the concept critique prompt."""
        # Use safe JSON serialization
        safe_json = self._build_safe_json_string(concept_json)

        return f"""Critique the following book concept:

        ```json
        {safe_json}
        ```
        The book should be written in {project_kb.language}.

        Evaluate:
        - Strengths and weaknesses
        - Market potential
        - Originality
        - Clarity and coherence

        IMPORTANT: Write your critique entirely in {project_kb.language}.
        Start your response directly with the critique content. Do not include any introductory phrases like "Of course" or "Here is a detailed critique". Begin immediately with your analysis."""

    def _build_simple_critique_prompt(self, concept_json: dict[str, Any], project_kb: ProjectKnowledgeBase) -> str:
        """Build a simplified critique prompt to avoid content filtering."""
        # Use only essential information
        title = concept_json.get("title", "Unknown Title")
        logline = concept_json.get("logline", "Unknown Logline")

        return f"""Review this book concept:

        Title: {title}
        Summary: {logline}
        Language: {project_kb.language}

        Provide a brief evaluation in {project_kb.language} focusing on:
        - Main strengths
        - Areas for improvement
        - Overall potential

        Write directly in {project_kb.language} without introductions."""

    def _build_refine_prompt(
        self,
        initial_concept: dict[str, Any],
        critique: str,
        project_kb: ProjectKnowledgeBase,
    ) -> str:
        """Build the concept refinement prompt."""
        # Use safe JSON serialization
        safe_json = self._build_safe_json_string(initial_concept)

        return f"""Based on the following critique, refine this book concept:

        Original Concept:
        ```json
        {safe_json}
        ```

        Critique:
        {critique}

        The book should be written in {project_kb.language}.

        Return a refined JSON object within a Markdown code block with the same structure as the original."""

    def _build_simple_refine_prompt(
        self,
        initial_concept: dict[str, Any],
        critique: str,
        project_kb: ProjectKnowledgeBase,
    ) -> str:
        """Build a simplified refinement prompt to avoid content filtering."""
        title = initial_concept.get("title", "Unknown Title")
        logline = initial_concept.get("logline", "Unknown Logline")

        return f"""Improve this book concept based on the feedback:

        Title: {title}
        Summary: {logline}
        Language: {project_kb.language}
        Feedback: {critique[:500] if len(critique) > 500 else critique}

        Return a refined JSON with title, logline, and description in {project_kb.language}."""

    def _build_keywords_prompt(self, concept_json: dict[str, Any], project_kb: ProjectKnowledgeBase) -> str:
        """Build the keywords generation prompt."""
        # Use safe JSON serialization
        safe_json = self._build_safe_json_string(concept_json)

        return f"""Generate relevant keywords for this book concept:

        ```json
        {safe_json}
        ```

        The book should be written in {project_kb.language}.

        Return a JSON object with:
        - "primary_keywords": List of main themes/topics
        - "secondary_keywords": List of supporting themes
        - "genre_keywords": List of genre-specific terms

        ```json
        {{
            "primary_keywords": ["keyword1", "keyword2"],
            "secondary_keywords": ["keyword3", "keyword4"],
            "genre_keywords": ["keyword5", "keyword6"]
        }}
        ```"""

    def _build_simple_keywords_prompt(self, concept_json: dict[str, Any], project_kb: ProjectKnowledgeBase) -> str:
        """Build a simplified keywords prompt to avoid content filtering."""
        title = concept_json.get("title", "Unknown Title")
        description = concept_json.get("description", "Unknown Description")[:300]

        return f"""Extract keywords from this book concept:

        Title: {title}
        Description: {description}
        Language: {project_kb.language}

        Return JSON with primary_keywords, secondary_keywords, and genre_keywords lists."""

    def _generate_fallback_keywords(self, concept_json: dict[str, Any]) -> dict[str, Any]:
        """Generate basic keywords when LLM generation fails."""
        title = concept_json.get("title", "").lower()
        description = concept_json.get("description", "").lower()

        # Extract basic keywords from title and description
        words = re.findall(r"\b\w{4,}\b", f"{title} {description}")
        common_words = {
            "the",
            "and",
            "for",
            "with",
            "this",
            "that",
            "they",
            "have",
            "from",
            "their",
            "were",
            "been",
            "said",
            "each",
            "which",
            "she",
            "will",
            "more",
            "when",
            "there",
            "can",
            "an",
            "your",
            "all",
            "her",
            "would",
            "make",
            "about",
            "up",
            "out",
            "many",
            "them",
            "then",
            "these",
            "so",
            "some",
            "like",
            "into",
            "him",
            "time",
            "two",
            "go",
            "no",
            "way",
            "could",
            "my",
            "than",
            "first",
            "call",
            "who",
            "its",
            "now",
            "find",
            "long",
            "down",
            "day",
            "did",
            "get",
            "come",
            "made",
            "may",
            "part",
        }

        keywords = [word for word in words if word not in common_words and len(word) > 3][:10]

        return {
            "primary_keywords": keywords[:5],
            "secondary_keywords": keywords[5:8] if len(keywords) > 5 else [],
            "genre_keywords": keywords[8:] if len(keywords) > 8 else [],
        }

    def _format_concept_as_markdown(
        self,
        concept_json: dict[str, Any],
        keywords_json: dict[str, Any],
        critique_response: str,
    ) -> str:
        """Format the concept data as a readable Markdown file."""
        content = f"""# Book Concept
## Title
{concept_json.get("title", "N/A")}
## Logline
{concept_json.get("logline", "N/A")}
## Description
{concept_json.get("description", "N/A")}
## Keywords
"""

        # Add keywords if available
        if keywords_json and isinstance(keywords_json, dict):
            # Flatten all keywords into a single list
            all_keywords = []
            for _category, keywords in keywords_json.items():
                if isinstance(keywords, list):
                    all_keywords.extend(keywords)
                else:
                    all_keywords.append(str(keywords))

            # Add as simple bullet list
            for keyword in all_keywords:
                content += f"- {keyword}\n"

        content += f"## Critique\n{critique_response}"

        # Check if the "Generated by" notice should be hidden via Settings
        settings = Settings()
        if not settings.hide_generated_by:
            content += "\n\n---\n*Generated by LibriScribe2 Concept Generator*"

        return content

    def _update_knowledge_base(
        self,
        project_kb: ProjectKnowledgeBase,
        concept_json: dict[str, Any],
        keywords_json: dict[str, Any],
    ) -> None:
        """Update the knowledge base with the refined concept and keywords."""
        # Update concept fields
        project_kb.title = JSONProcessor.extract_string_from_json(concept_json, "title", project_kb.title)
        project_kb.logline = JSONProcessor.extract_string_from_json(concept_json, "logline", project_kb.logline)
        project_kb.description = JSONProcessor.extract_string_from_json(
            concept_json, "description", project_kb.description
        )

        # Update keywords
        primary_keywords = JSONProcessor.extract_list_from_json(keywords_json, "primary_keywords", [])
        secondary_keywords = JSONProcessor.extract_list_from_json(keywords_json, "secondary_keywords", [])
        genre_keywords = JSONProcessor.extract_list_from_json(keywords_json, "genre_keywords", [])

        project_kb.keywords = primary_keywords + secondary_keywords + genre_keywords

    def _clean_bold_headers(self, markdown_content: str) -> str:
        """Remove bold emphasis from markdown headers to ensure compliance."""
        # Pattern to match headers with bold text (e.g., #### **Text** -> #### Text)
        pattern = r"^(#{1,6})\s*\*\*(.+?)\*\*\s*$"

        lines = markdown_content.split("\n")
        cleaned_lines = []

        for line in lines:
            # Check if line matches header with bold pattern
            match = re.match(pattern, line)
            if match:
                header_level = match.group(1)
                header_text = match.group(2)
                cleaned_line = f"{header_level} {header_text}"
                cleaned_lines.append(cleaned_line)
            else:
                cleaned_lines.append(line)

        return "\n".join(cleaned_lines)

    def _format_keywords_response(self, keywords_md: str) -> tuple[dict[str, Any], str]:
        """Format the keywords response into a clean JSON structure.

        Args:
            keywords_md: The raw markdown response containing the keywords

        Returns:
            A tuple of (formatted_keywords, raw_keywords_text)
        """
        if not keywords_md:
            return {}, ""

        # Extract JSON content from markdown code blocks if present
        json_match = re.search(r"```(?:json\n)?(.*?)```", keywords_md, re.DOTALL)
        raw_keywords_text = json_match.group(1).strip() if json_match else keywords_md.strip()

        try:
            # Try to parse the raw JSON
            keywords_data = json.loads(raw_keywords_text)

            # Ensure we have the expected structure
            if not isinstance(keywords_data, dict):
                raise ValueError("Keywords data is not a dictionary")

            # Ensure all keyword lists exist and are lists
            for key in ["primary_keywords", "secondary_keywords", "genre_keywords"]:
                if key not in keywords_data:
                    keywords_data[key] = []
                elif not isinstance(keywords_data[key], list):
                    # Convert single values to a list
                    keywords_data[key] = [keywords_data[key]]

            return keywords_data, raw_keywords_text

        except ValueError as e:
            self.logger.warning(f"Failed to parse keywords JSON: {e}")
            # Return default empty keywords structure
            return {"primary_keywords": [], "secondary_keywords": [], "genre_keywords": []}, ""


def _format_keywords_response(self, keywords_md: str) -> tuple[dict[str, Any], str]:
    """Format the keywords response into a clean JSON structure.

    Args:
        keywords_md: The raw markdown response containing the keywords

    Returns:
        A tuple of (formatted_keywords, raw_keywords_text)
    """
    if not keywords_md:
        return {}, ""

    # Extract JSON content from markdown code blocks if present
    json_match = re.search(r"```(?:json\n)?(.*?)```", keywords_md, re.DOTALL)
    raw_keywords_text = json_match.group(1).strip() if json_match else keywords_md.strip()

    try:
        # Try to parse the raw JSON
        keywords_data = json.loads(raw_keywords_text)

        # Ensure we have the expected structure
        if not isinstance(keywords_data, dict):
            raise ValueError("Keywords data is not a dictionary")

        # Ensure all keyword lists exist and are lists
        for key in ["primary_keywords", "secondary_keywords", "genre_keywords"]:
            if key not in keywords_data:
                keywords_data[key] = []
            elif not isinstance(keywords_data[key], list):
                # Convert single values to a list
                keywords_data[key] = [keywords_data[key]]

        return keywords_data, raw_keywords_text

    except ValueError as e:
        self.logger.warning(f"Failed to parse keywords JSON: {e}")
        # Fallback to extracting any list-like structures
        keywords: dict[str, list[str]] = {"primary_keywords": [], "secondary_keywords": [], "genre_keywords": []}

        # Try to extract any list-like structures
        list_matches = re.findall(r"\[(.*?)\]", raw_keywords_text)
        if list_matches:
            # Use the first list found as primary keywords
            try:
                items = [item.strip("'\" ") for item in list_matches[0].split(",")]
                keywords["primary_keywords"] = [item for item in items if item]
            except Exception as e:
                self.logger.debug(f"Error extracting keywords from list: {e}", exc_info=True)

        return keywords, raw_keywords_text
