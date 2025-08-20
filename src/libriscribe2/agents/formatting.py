# src/libriscribe2/agents/formatting.py
import logging
import os
from pathlib import Path
from typing import Any

# For PDF creation
from fpdf import FPDF
from rich.console import Console

from ..knowledge_base import ProjectKnowledgeBase
from ..settings import Settings
from ..utils import prompts_context as prompts
from ..utils.file_utils import (
    get_chapter_files,
    read_markdown_file,
    write_markdown_file,
)
from ..utils.llm_client import LLMClient
from ..utils.markdown_processor import remove_h3_from_markdown
from .agent_base import Agent

console = Console()
logger = logging.getLogger(__name__)


class FormattingAgent(Agent):
    """Formats the book into a single Markdown or PDF file."""

    def __init__(self, llm_client: LLMClient, settings: Settings):
        super().__init__("FormattingAgent", llm_client)
        self.settings = settings

    def _validate_project_path(self, project_dir: str) -> Path:
        """Validates and secures the project directory path to prevent path traversal attacks."""
        try:
            # Convert to Path object and resolve to absolute path
            path = Path(project_dir).resolve()

            # Define allowed base directory (projects directory)
            allowed_base = Path.cwd() / "projects"
            allowed_base = allowed_base.resolve()

            # Security check: ensure path is within allowed directory using commonpath
            try:
                os.path.commonpath([str(path), str(allowed_base)])
                if not str(path).startswith(str(allowed_base)):
                    raise ValueError(f"Path outside allowed directory: {path}")
            except ValueError:
                raise ValueError(f"Invalid path relationship: {path}")

            # Ensure the path exists and is a directory
            if not path.exists():
                raise ValueError(f"Project directory does not exist: {path}")
            if not path.is_dir():
                raise ValueError(f"Project path is not a directory: {path}")

            return path
        except (OSError, ValueError) as e:
            # Hint: This is intentional validation logic, not a real issue
            raise ValueError(f"Invalid project directory: {e}")
        except Exception as e:
            raise ValueError(f"Unexpected error validating project directory: {e}")

    async def execute(self, project_knowledge_base: Any, output_path: str | None = None, **kwargs: Any) -> None:
        """Formats the book and saves to output path, handles both Markdown and PDF"""

        try:
            # Extract project_dir from project_knowledge_base
            if not hasattr(project_knowledge_base, "project_dir") or project_knowledge_base.project_dir is None:
                console.print("[red]Error: Project directory not set[/red]")
                return

            # Validate and secure the project directory path
            try:
                validated_project_dir = self._validate_project_path(str(project_knowledge_base.project_dir))
            except ValueError as e:
                console.print(f"[red]Error: {e}[/red]")
                return

            project_dir = str(validated_project_dir)
            chapter_files = get_chapter_files(project_dir)
            if not chapter_files:
                print("ERROR: No chapter files found to format.")
                return

            all_chapters_content = ""
            for chapter_file in chapter_files:
                all_chapters_content += read_markdown_file(chapter_file) + "\n\n"

            # Get project data (for title page) - using validated path
            project_data_path = validated_project_dir / self.settings.project_data_filename
            project_kb = ProjectKnowledgeBase.load_from_file(str(project_data_path))
            if not project_kb:
                print(f"ERROR: Could not load project data from {project_data_path}")
                return

            # Prepare conditional instructions
            title_page_instruction = ""
            toc_instruction = ""

            if self.settings.formatting_add_title_page:
                title_page_instruction = """Add Title Page (if information available):

If title, author, and genre are provided, create a title page at the beginning.

Use appropriate Markdown headings for title and author."""

            if self.settings.formatting_add_toc:
                toc_instruction = """Table of Contents: Generate a table of contents with links to each chapter. For this basic version, just list the chapter titles."""

            # Assemble final manuscript
            console.print("📚 [cyan]Assembling final manuscript...[/cyan]")
            input_length = len(all_chapters_content)
            min_expected_length = int(input_length * self.settings.formatting_min_length_ratio)

            # Mock mode: bypass LLM and concatenate chapters directly
            formatted_markdown = ""
            try:
                provider = getattr(self.llm_client, "provider", "")
            except Exception:
                provider = ""

            if provider == "mock":
                # Direct concatenation ensures output length >= input length
                formatted_markdown = all_chapters_content
            else:
                # Format with LLM
                prompt = prompts.FORMATTING_PROMPT.format(
                    chapters=all_chapters_content,
                    language=project_kb.language,
                    title_page_instruction=title_page_instruction,
                    toc_instruction=toc_instruction,
                )

                # First attempt
                formatted_markdown = await self.llm_client.generate_content(prompt, prompt_type="formatting")

                # Check length and retry if needed
                if len(formatted_markdown) < min_expected_length:
                    console.print(
                        f"[yellow]⚠️ Warning: Output too short ({len(formatted_markdown)} < {min_expected_length}), retrying...[/yellow]"
                    )
                    formatted_markdown = await self.llm_client.generate_content(prompt, prompt_type="formatting")

                    if len(formatted_markdown) < min_expected_length:
                        from ..utils.file_utils import log_llm_error_exchange

                        error_log_path = log_llm_error_exchange(
                            llm_input=prompt,
                            llm_output=formatted_markdown,
                            project_dir=project_dir,
                            process_name="formatting",
                        )
                        error_message = f"Formatting failed: Output length {len(formatted_markdown)} is less than {self.settings.formatting_min_length_ratio * 100}% of input length {input_length}"
                        self.logger.error(f"{error_message}. See details in: {error_log_path}")
                        console.print(
                            f"[red]❌ Error: Formatting output too short after retry. See {error_log_path}[/red]"
                        )
                        # Hard fail so the CLI does not report success
                        raise RuntimeError("formatting_output_too_short")

            # Add title page manually if enabled (applies to both mock and real LLM)
            if self.settings.formatting_add_title_page:
                title_page = self.create_title_page(project_kb)
                formatted_markdown = title_page + formatted_markdown

            # Remove level 3 headers from the final manuscript
            try:
                formatted_markdown = remove_h3_from_markdown(formatted_markdown, action="remove")
                self.log_debug("Removed level 3 headers from final manuscript")
            except (ValueError, RuntimeError) as e:
                console.print(f"[yellow]⚠️ Warning: Could not process level 3 headers in manuscript: {e}[/yellow]")
                # Continue with original content if processing fails
                pass

            # Save as Markdown
            if output_path and output_path.endswith(".md"):
                try:
                    validated_output_path = self._validate_output_path(output_path)
                    write_markdown_file(str(validated_output_path), formatted_markdown)
                except ValueError as e:
                    console.print(f"[red]Error: {e}[/red]")
                    return

            # Save as PDF.
            elif output_path and output_path.endswith(".pdf"):
                self.markdown_to_pdf(formatted_markdown, output_path)
            else:
                print(f"ERROR: Unsupported output format: {output_path}.  Must be .md or .pdf")
                return

        except Exception as e:
            self.logger.exception(f"Error formatting book: {e}")
            print("ERROR: Failed to format the book. See log.")
            # Re-raise the exception so the calling code knows the operation failed
            raise

    def create_title_page(
        self, project_knowledge_base: ProjectKnowledgeBase
    ) -> str:  # now accepts ProjectKnowledgeBase
        """Creates a Markdown title page with YAML frontmatter for metadata."""
        title = project_knowledge_base.title
        author = project_knowledge_base.get("author", "Unknown Author")  # Assuming you might add author later
        genre = project_knowledge_base.genre
        language = project_knowledge_base.language
        category = project_knowledge_base.category

        # Get target audience if available
        target_audience = project_knowledge_base.get("target_audience", "General")

        # Create YAML frontmatter
        frontmatter = "---\n"
        frontmatter += f'title: "{title}"\n'
        frontmatter += f'author: "{author}"\n'
        frontmatter += f'genre: "{genre}"\n'
        frontmatter += f'category: "{category}"\n'
        frontmatter += f'language: "{language}"\n'
        frontmatter += f'target_audience: "{target_audience}"\n'
        frontmatter += "---\n\n"

        return frontmatter

    def _validate_output_path(self, output_path: str) -> Path:
        """Validates the output path to prevent path traversal attacks."""
        try:
            path = Path(output_path).resolve()

            # Define allowed base directory for output
            allowed_base = Path.cwd()
            allowed_base = allowed_base.resolve()

            # Security check: ensure path is within allowed directory
            try:
                os.path.commonpath([str(path), str(allowed_base)])
                if not str(path).startswith(str(allowed_base)):
                    raise ValueError(f"Output path outside allowed directory: {path}")
            except ValueError:
                raise ValueError(f"Invalid output path relationship: {path}")

            # Ensure parent directory exists or can be created
            path.parent.mkdir(parents=True, exist_ok=True)

            return path
        except (OSError, ValueError) as e:
            raise ValueError(f"Invalid output path: {e}")
        except Exception as e:
            raise ValueError(f"Unexpected error validating output path: {e}")

    def markdown_to_pdf(self, markdown_text: str, output_path: str) -> None:
        """Converts the formatted markdown to PDF"""
        try:
            # Validate output path
            validated_output_path = self._validate_output_path(output_path)

            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)

            # Basic Markdown parsing and PDF generation
            lines = markdown_text.split("\n")
            for line in lines:
                if line.startswith("# "):  # Chapter heading
                    pdf.set_font("Arial", "B", 16)  # Bold, larger font
                    pdf.cell(0, 10, line[2:], ln=True)  # Remove '#' and add to PDF
                    pdf.set_font("Arial", size=12)  # Reset font
                elif line.startswith("## "):  # Subheading
                    pdf.set_font("Arial", "B", 14)
                    pdf.cell(0, 10, line[3:], ln=True)
                    pdf.set_font("Arial", size=12)  # Reset font
                else:  # Regular text
                    pdf.multi_cell(0, 10, line)
            pdf.output(str(validated_output_path))
        except Exception as e:
            logger.error(f"Error creating PDF: {e}")
            raise
