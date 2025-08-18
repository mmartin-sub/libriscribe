import json
import logging
from typing import Any

import typer
from rich.console import Console

from libriscribe2.knowledge_base import ProjectKnowledgeBase
from libriscribe2.settings import Settings
from libriscribe2.utils.llm_client import LLMClient

console = Console()
logger = logging.getLogger(__name__)


def select_llm(project_knowledge_base: ProjectKnowledgeBase, mock_mode: bool = False) -> str:
    """Lets the user select an LLM provider."""
    available_llms = []
    settings = Settings()

    if mock_mode:
        console.print("[yellow]Mock mode enabled. Using MockLLMClient.[/yellow]")
        return "mock"

    if settings.openai_api_key:
        available_llms.append("openai")

    if not available_llms:
        console.print("[red]❌ No LLM API keys found in .env file. Please add at least one.[/red]")
        raise typer.Exit(code=1)

    console.print("")
    llm_choice = select_from_list("🤖 Select your preferred AI model:", available_llms)

    # Convert display name back to API identifier - we only have openai available

    # Note: We only support OpenAI now, so llm_choice is always "openai"
    return llm_choice


def select_from_list(prompt: str, options: list[str], allow_custom: bool = False) -> str:
    """Presents options and returns selection with improved formatting."""
    console.print(f"[bold]{prompt}[/bold]")

    # Display options with numbers
    for i, option in enumerate(options):
        console.print(f"[cyan]{i + 1}.[/cyan] {option}")

    if allow_custom:
        console.print(f"[cyan]{len(options) + 1}.[/cyan]Custom (enter your own)")

    # Get user selection with error handling
    result: str = ""
    while result == "":
        try:
            choice = typer.prompt("Enter your choice", show_choices=False)
            choice_idx = int(choice) - 1

            if 0 <= choice_idx < len(options):
                result = str(options[choice_idx])  # Return original option without emoji
            elif allow_custom and choice_idx == len(options):
                custom_value = typer.prompt("Enter your custom value")
                result = str(custom_value)
            else:
                console.print("[red]Invalid choice. Please try again.[/red]")
        except ValueError:
            console.print("[red]Please enter a number.[/red]")

    return result


async def generate_questions_with_llm(category: str, genre: str, llm_client: LLMClient | None) -> dict[str, Any]:
    """Generates genre-specific questions with improved error handling."""
    prompt = f"""
    Generate a list of 5-7 KEY questions that would help develop a {category} {genre} book.
    Format your response as a JSON object where keys are question IDs and values are the questions.

    For example:
    {{
        "q1": "What is the central conflict of your story?",
        "q2": "Who is the main antagonist?",
        "q3": "What is the world's primary magic system?"
    }}

    Return ONLY valid JSON, nothing else.
    """

    if llm_client is None:
        console.print("[red]LLM is not selected[/red]")
        return {}

    try:
        response = await llm_client.generate_content(prompt, prompt_type="questions")

        # Clean the response - find JSON content
        response = response.strip()
        # Look for JSON between curly braces if there's other text
        if "{" in response and "}" in response:
            start = response.find("{")
            end = response.rfind("}") + 1
            json_str = response[start:end]
        else:
            json_str = response

        try:
            questions = json.loads(json_str)
            return questions if isinstance(questions, dict) else {}
        except json.JSONDecodeError:
            # If it fails, create a minimal set of questions as fallback
            console.print("[yellow]Could not parse LLM response. Using default questions.[/yellow]")
            return {
                "q1": f"What key themes do you want to explore in your {genre} story?",
                "q2": "Who is your favorite character and why?",
                "q3": "What makes your story unique compared to similar works?",
            }
    except Exception as e:
        logger.error(f"Error generating questions: {e}")
        console.print("[yellow]Error generating custom questions. Using defaults.[/yellow]")
        return {
            "q1": f"What key themes do you want to explore in your {genre} story?",
            "q2": "Who is your favorite character and why?",
            "q3": "What makes your story unique compared to similar works?",
        }
