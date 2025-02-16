# src/libriscribe/agents/chapter_writer.py

import logging
from pathlib import Path

from libriscribe.agents.agent_base import Agent
from libriscribe.utils import prompts_context as prompts
from libriscribe.utils.file_utils import read_markdown_file, read_json_file, write_markdown_file
from libriscribe.knowledge_base import ProjectKnowledgeBase, Chapter, Scene
from libriscribe.utils.llm_client import LLMClient
import json


logger = logging.getLogger(__name__)

class ChapterWriterAgent(Agent):
    """Writes chapters."""

    def __init__(self, llm_client: LLMClient):
        super().__init__("ChapterWriterAgent", llm_client)


    def execute(self, project_knowledge_base: ProjectKnowledgeBase, chapter_number: int, output_path: Optional[str] = None) -> None:
        """Writes a chapter with paragraph planning."""
        try:
            chapter = project_knowledge_base.get_chapter(chapter_number)
            if not chapter:
                print(f"ERROR: Chapter {chapter_number} not found in knowledge base.")
                return

            # --- Step 1: Generate Paragraph Plan ---
            paragraph_plan_prompt = prompts.PARAGRAPH_PLAN_PROMPT.format(
                chapter_title=chapter.title,
                chapter_summary=chapter.summary,
                scenes=[scene.model_dump() for scene in chapter.scenes],
                characters=json.dumps(project_knowledge_base.characters),  # Pass characters as JSON
                worldbuilding=json.dumps(project_knowledge_base.worldbuilding.model_dump()) #pass worldbuilding as JSON
            )

            paragraph_plan_str = self.llm_client.generate_content(paragraph_plan_prompt, max_tokens=2000)
            if not paragraph_plan_str:
                logger.error(f"Failed to generate paragraph plan for chapter {chapter_number}.")
                return

            paragraph_plan = self.process_paragraph_plan(paragraph_plan_str)
            #Store paragraph plan in scene
            self.store_paragraph_plan(chapter, paragraph_plan)

            # --- Step 2: Generate Full Chapter (using paragraph plan) ---
            full_chapter_prompt = prompts.CHAPTER_PROMPT.format(
                chapter_number=chapter_number,
                chapter_title=chapter.title,
                book_title=project_knowledge_base.title,
                genre=project_knowledge_base.genre,
                category=project_knowledge_base.category,
                chapter_summary = chapter.summary,
                scenes=[scene.model_dump() for scene in chapter.scenes],
                characters=json.dumps(project_knowledge_base.characters),
                worldbuilding=json.dumps(project_knowledge_base.worldbuilding.model_dump()),
                paragraph_plan=json.dumps(paragraph_plan),
                outline = project_knowledge_base.outline #Pass the entire outline

            )


            chapter_content = self.llm_client.generate_content(full_chapter_prompt, max_tokens=5000) #Increased tokens
            if not chapter_content:
                 self.logger.error(f"Failed to generate chapter {chapter_number}.")
                 return

            # --- Step 3: Save Chapter ---
            if output_path is None:
                output_path = str(Path(project_knowledge_base.project_name).parent / f"chapter_{chapter_number}.md")
            write_markdown_file(output_path, chapter_content)



        except Exception as e:
            self.logger.exception(f"Error writing chapter {chapter_number}: {e}")
            print(f"ERROR: Failed to write chapter {chapter_number}. See log.")

    def process_paragraph_plan(self, paragraph_plan_str: str) -> List[Dict[str, str]]:
        """Parses the paragraph plan (assumes it's returned as a JSON array)."""
        try:
            plan = json.loads(paragraph_plan_str)
            if not isinstance(plan, list):
                logger.warning("Paragraph plan is not a list.")
                return []
            return plan
        except json.JSONDecodeError:
            logger.error("Invalid JSON in paragraph plan.")
            return []
        except Exception as e:
            logger.exception(f"Error processing paragraph plan: {e}")
            return []

    def store_paragraph_plan(self, chapter: Chapter, paragraph_plan: List[Dict[str, str]]):
        """Stores paragraph plan, grouping by scene."""
        current_scene = None

        for plan_item in paragraph_plan:
            if "scene_number" in plan_item:
                try:
                    scene_num = int(plan_item["scene_number"])
                    current_scene = next((s for s in chapter.scenes if s.scene_number == scene_num), None)
                except (ValueError, TypeError):
                    logger.warning(f"Invalid scene number in paragraph plan: {plan_item.get('scene_number')}")
                    current_scene = None

            if current_scene:
                try:
                    paragraph_number = int(plan_item["paragraph_number"])
                    current_scene.paragraph_plan.append({
                        "paragraph_number": paragraph_number,
                        "summary": plan_item.get("summary", "")
                    })
                except (ValueError, TypeError):
                    logger.warning(f"Invalid paragraph number in paragraph plan: {plan_item.get('paragraph_number')}")
                    # Don't add if invalid

            #No scene number, just ignore

        #Sort the paragraphs
        for scene in chapter.scenes:
            scene.paragraph_plan.sort(key=lambda x: x["paragraph_number"])