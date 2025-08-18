"""Content exporters for characters and worldbuilding to markdown format."""

from pathlib import Path

from ..knowledge_base import Character, Worldbuilding


def export_characters_to_markdown(characters: dict[str, Character], output_path: str) -> None:
    """Export characters to a markdown file."""
    content = "# Characters\n\n"

    for character in characters.values():
        content += f"## {character.name}\n\n"

        if character.age:
            content += f"**Age:** {character.age}\n\n"
        if character.physical_description:
            content += f"**Physical Description:** {character.physical_description}\n\n"
        if character.personality_traits:
            content += f"**Personality:** {character.personality_traits}\n\n"
        if character.background:
            content += f"**Background:** {character.background}\n\n"
        if character.motivations:
            content += f"**Motivations:** {character.motivations}\n\n"
        if character.role:
            content += f"**Role:** {character.role}\n\n"
        if character.internal_conflicts:
            content += f"**Internal Conflicts:** {character.internal_conflicts}\n\n"
        if character.external_conflicts:
            content += f"**External Conflicts:** {character.external_conflicts}\n\n"
        if character.character_arc:
            content += f"**Character Arc:** {character.character_arc}\n\n"

        content += "---\n\n"

    Path(output_path).write_text(content, encoding="utf-8")


def export_worldbuilding_to_markdown(worldbuilding: Worldbuilding | None, output_path: str) -> None:
    """Export worldbuilding to a markdown file.

    Writes the file only if there is at least one non-empty field.
    Safely handles a missing (None) worldbuilding object.
    """
    if worldbuilding is None:
        return

    # Dump to dict to iterate actual declared fields
    worldbuilding_dict = worldbuilding.model_dump()

    # Collect non-empty string fields
    non_empty_items: list[tuple[str, str]] = []
    for key, value in worldbuilding_dict.items():
        if isinstance(value, str) and value.strip():
            non_empty_items.append((key, value.strip()))

    # Do not write a file if nothing to write
    if not non_empty_items:
        return

    # Build markdown content
    content_lines: list[str] = ["# Worldbuilding", ""]
    for key, value in non_empty_items:
        # Convert snake_case to Title Case with spaces
        title = key.replace("_", " ").title()
        content_lines.append(f"## {title}")
        content_lines.append("")
        content_lines.append(value)
        content_lines.append("")

    Path(output_path).write_text("\n".join(content_lines), encoding="utf-8")
