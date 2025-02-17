# src/libriscribe/main.py
import typer
from libriscribe.agents.project_manager import ProjectManagerAgent
from typing import List, Dict, Any
from libriscribe.utils.llm_client import LLMClient
import json
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
import logging
#MODIFIED
from libriscribe.knowledge_base import ProjectKnowledgeBase, Chapter  # Import the new class
from libriscribe.settings import Settings
from rich.progress import track  # Import track

# Configure logging (same as before)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

console = Console()
app = typer.Typer()
#project_manager = ProjectManagerAgent()  # Initialize ProjectManager
project_manager = ProjectManagerAgent(llm_client=None)
logger = logging.getLogger(__name__)

def select_llm(project_knowledge_base: ProjectKnowledgeBase): #MODIFIED
    """Lets the user select an LLM provider."""
    available_llms = []
    settings = Settings()

    if settings.openai_api_key:
        available_llms.append("openai")
    if settings.claude_api_key:
        available_llms.append("claude")
    if settings.google_ai_studio_api_key:
        available_llms.append("google_ai_studio")
    if settings.deepseek_api_key:
        available_llms.append("deepseek")
    if settings.mistral_api_key:
        available_llms.append("mistral")

    if not available_llms:
        console.print("[red]No LLM API keys found in .env file.  Please add at least one.[/red]")
        raise typer.Exit(code=1)

    llm_choice = select_from_list("Select your preferred LLM provider:", available_llms)
    project_knowledge_base.set("llm_provider", llm_choice)  # Store the choice
    return llm_choice

def introduction():
    """Prints a welcome message (same as before)."""
    console.print(
        Panel(
            "[bold blue]📚✨ Welcome to Libriscribe! ✨📚[/bold blue]\n\n"
            "Libriscribe is an AI-powered open-source book creation system ... (rest of the message)",
            title="[bold blue]Libriscribe[/bold blue]",
            border_style="blue",
        )
    )

def select_from_list(prompt: str, options: List[str], allow_custom: bool = False) -> str:
    """Presents options and returns selection (same as before, but slightly improved)."""
    console.print(f"[bold]{prompt}[/bold]")
    for i, option in enumerate(options):
        console.print(f"[cyan]{i + 1}.[/cyan] {option}")
    if allow_custom:
        console.print(f"[cyan]{len(options) + 1}.[/cyan] Custom (enter your own)")

    choices = [str(i) for i in range(1, len(options) + (2 if allow_custom else 1))]
    choice = Prompt.ask("Enter the number of your choice", choices=choices, show_choices=False)

    try:
        choice_index = int(choice) - 1
        if 0 <= choice_index < len(options):
            return options[choice_index]
        elif allow_custom and choice_index == len(options):
            return Prompt.ask("Enter your custom value")
        else:
            console.print("[red]Invalid choice. Please try again.[/red]")
            return select_from_list(prompt, options, allow_custom)  # Recursive call
    except ValueError:
        console.print("[red]Invalid input. Please enter a number.[/red]")
        return select_from_list(prompt, options, allow_custom)


def save_project_data():
    """Saves project data (using new method)."""
    project_manager.save_project_data() # Now it's the same


def generate_questions_with_llm(category: str, genre: str) -> Dict[str, Any]:
    """Generates genre-specific questions (same as before, but using LLMClient)."""
    prompt = f"""
    Generate a list of 5-7 KEY questions ... (rest of the prompt)
    """
    llm_client = project_manager.llm_client
    if llm_client is None:
        console.print("[red] LLM is not selected[/red]")
        return {}

    try:
        response = llm_client.generate_content(prompt, max_tokens=500)
        questions = json.loads(response)
        return questions
    except (Exception, json.JSONDecodeError) as e:
        logger.error(f"Error generating questions: {e}")
        print(f"Error generating questions: {e}")
        return {}


# --- Helper functions for Simple Mode ---

def get_project_name_and_title():
    project_name = typer.prompt("Enter a project name (this will be the directory name)")
    title = typer.prompt("What is the title of your book?")
    return project_name, title

def get_category_and_genre(project_knowledge_base: ProjectKnowledgeBase): #MODIFIED
    category = select_from_list(
        "Select the category of your book:",
        ["Fiction", "Non-Fiction", "Business", "Research Paper"],
        allow_custom=True,
    )
    project_knowledge_base.set("category", category)

    if category == "Fiction":
        genre_options = ["Fantasy", "Science Fiction", "Romance", "Thriller", "Mystery", "Historical Fiction", "Horror", "Young Adult", "Contemporary"]
    elif category == "Non-Fiction":
        genre_options = ["Biography", "History", "Science", "Self-Help", "Travel", "True Crime", "Cookbook"]
    elif category == "Business":
        genre_options = ["Marketing", "Management", "Finance", "Entrepreneurship", "Leadership", "Sales", "Productivity"]
    elif category == "Research Paper":
        genre = typer.prompt("Enter the field of study for your research paper:")
        project_knowledge_base.set("genre", genre)
        return
    else:
        genre_options = []  # Should not happen, but for safety

    if genre_options:
        genre = select_from_list(f"Select the genre/subject of your {category} book:", genre_options, allow_custom=True)
        project_knowledge_base.set("genre", genre)



def get_book_length(project_knowledge_base: ProjectKnowledgeBase): #MODIFIED
    book_length = select_from_list(
        "Select the desired book length:",
        ["Short Story", "Novella", "Novel", "Full Book (Non-Fiction)"],
        allow_custom=False,
    )
    project_knowledge_base.set("book_length", book_length)

def get_fiction_details(project_knowledge_base: ProjectKnowledgeBase): #MODIFIED
    if project_knowledge_base.category == "Fiction":
        num_characters = typer.prompt("How many main characters do you envision?", type=int)
        project_knowledge_base.set("num_characters", num_characters)
        worldbuilding_needed = typer.confirm("Does this book require extensive worldbuilding?")
        project_knowledge_base.set("worldbuilding_needed", worldbuilding_needed)

def get_review_preference(project_knowledge_base: ProjectKnowledgeBase): #MODIFIED
    review_preference = select_from_list("How would you like the book to be reviewed?", ["Human", "AI"])
    project_knowledge_base.set("review_preference", review_preference)

def get_description(project_knowledge_base: ProjectKnowledgeBase): #MODIFIED
    description = typer.prompt("Provide a brief description of your book")
    project_knowledge_base.set("description", description)

def generate_and_review_concept(project_knowledge_base: ProjectKnowledgeBase): #MODIFIED
    project_manager.generate_concept()
    project_manager.checkpoint() # Checkpoint
    print(f"\nRefined Concept:") # Clarified Output
    print(f"  Title: {project_knowledge_base.title}")  # Use direct attributes
    print(f"  Logline: {project_knowledge_base.logline}")
    print(f"  Description:\n{project_knowledge_base.description}")
    return typer.confirm("Do you want to proceed with generating an outline based on this concept?")

def generate_and_edit_outline(project_knowledge_base: ProjectKnowledgeBase): #MODIFIED
    project_manager.generate_outline()
    project_manager.checkpoint()  # Checkpoint after outline
    print(f"\nOutline generated! Check the file: {project_manager.project_dir}/outline.md")

    if typer.confirm("Do you want to review and edit the outline now?"):
        typer.edit(filename=str(project_manager.project_dir / "outline.md"))
        print("\nChanges saved.")


def generate_characters_if_needed(project_knowledge_base: ProjectKnowledgeBase): #MODIFIED
     if project_knowledge_base.get("num_characters", 0) > 0:  # Use get with default
        if typer.confirm("Do you want to generate character profiles?"):
            print("\nGenerating characters...")
            project_manager.generate_characters()
            project_manager.checkpoint() # Checkpoint
            print(f"\nCharacter profiles generated! Check the file: {project_manager.project_dir}/characters.json")

def generate_worldbuilding_if_needed(project_knowledge_base: ProjectKnowledgeBase): #MODIFIED
    if project_knowledge_base.get("worldbuilding_needed", False):  # Use get with default
        if typer.confirm("Do you want to generate worldbuilding details?"):
            print("\nGenerating worldbuilding...")
            project_manager.generate_worldbuilding()
            project_manager.checkpoint() # Checkpoint
            print(f"\nWorldbuilding details generated! Check the file: {project_manager.project_dir}/world.json")

def write_and_review_chapters(project_knowledge_base: ProjectKnowledgeBase):
    """Write and review chapters with better progress tracking and error handling."""
    num_chapters = project_knowledge_base.get("num_chapters", 1)
    if isinstance(num_chapters, tuple):
        num_chapters = num_chapters[1]

    console.print(f"\n[bold]Starting chapter writing process. Total chapters: {num_chapters}[/bold]")

    for i in range(1, num_chapters + 1):
        chapter = project_knowledge_base.get_chapter(i)
        if chapter is None:
            console.print(f"[yellow]WARNING: Chapter {i} not found in outline. Creating basic structure...[/yellow]")
            chapter = Chapter(
                chapter_number=i,
                title=f"Chapter {i}",
                summary="To be written"
            )
            project_knowledge_base.add_chapter(chapter)  # Add to knowledge base!

        console.print(f"\n[bold cyan]Writing Chapter {i}: {chapter.title}[/bold cyan]")

        if project_manager.does_chapter_exist(i):
            if not typer.confirm(f"Chapter {i} already exists. Overwrite?"):
                console.print(f"[yellow]Skipping chapter {i}...[/yellow]")
                continue

        try:
            project_manager.write_and_review_chapter(i)
            project_manager.checkpoint()
            console.print(f"[green]✓ Chapter {i} completed successfully[/green]")
        except Exception as e:
            console.print(f"[red]ERROR writing chapter {i}: {str(e)}[/red]")
            logger.exception(f"Error writing chapter {i}")
            if not typer.confirm("Continue with next chapter?"):
                break

        if i < num_chapters:
            if not typer.confirm("\nContinue to next chapter?"):
                break

    console.print("\n[bold green]Chapter writing process completed![/bold green]")




def format_book(project_knowledge_base: ProjectKnowledgeBase): #MODIFIED
    if typer.confirm("Do you want to format the book now?"):
        output_format = select_from_list("Choose output format:", ["Markdown (.md)", "PDF (.pdf)"])
        if output_format == "Markdown (.md)":
            output_path = str(project_manager.project_dir / "manuscript.md")
        else:
            output_path = str(project_manager.project_dir / "manuscript.pdf")
        project_manager.format_book(output_path)
        print(f"\nBook formatted and saved to: {output_path}")

# --- Simple Mode (Refactored) ---
def simple_mode():
    print("\nStarting in Simple Mode...\n")

    project_name, title = get_project_name_and_title()
    project_knowledge_base = ProjectKnowledgeBase(project_name=project_name, title=title)

    llm_choice = select_llm(project_knowledge_base)
    project_manager.initialize_llm_client(llm_choice)

    get_category_and_genre(project_knowledge_base)
    get_book_length(project_knowledge_base)
    get_fiction_details(project_knowledge_base)
    get_review_preference(project_knowledge_base)
    get_description(project_knowledge_base)

    project_manager.initialize_project_with_data(project_knowledge_base)

    if generate_and_review_concept(project_knowledge_base):
        generate_and_edit_outline(project_knowledge_base)
        generate_characters_if_needed(project_knowledge_base)
        generate_worldbuilding_if_needed(project_knowledge_base)

        project_manager.checkpoint() 
        # Ensure chapters are written
        num_chapters = project_knowledge_base.get("num_chapters", 1)
        if isinstance(num_chapters, tuple):
            num_chapters = num_chapters[1]

        print(f"\nPreparing to write {num_chapters} chapters...")
        for chapter_num in range(1, num_chapters + 1):
            if not typer.confirm(f"\nWrite chapter {chapter_num}?"):
                break
            project_manager.write_and_review_chapter(chapter_num)
            project_manager.checkpoint()

        # Only format after chapters are written
        if typer.confirm("\nDo you want to format the book now?"):
            format_book(project_knowledge_base)
    else:
        print("Exiting.")
        return

    print("\nBook creation process complete (Simple Mode).")

# --- Helper Functions for Advanced Mode ---

def get_advanced_fiction_details(project_knowledge_base: ProjectKnowledgeBase): #MODIFIED
     num_characters_str = typer.prompt(
            "How many main characters do you envision (e.g., 3, 2-4, 5+)?", default="2-3"
        )
     project_knowledge_base.set("num_characters_str",num_characters_str)
     project_knowledge_base.set("num_characters", num_characters_str)

     worldbuilding_needed = typer.confirm("Does this book require extensive worldbuilding?")
     project_knowledge_base.set("worldbuilding_needed", worldbuilding_needed)

     tone = select_from_list("Select Tone", ["Serious", "Funny", "Romantic", "Informative", "Persuasive"])
     project_knowledge_base.set("tone", tone)

     target_audience = select_from_list("Select Target Audience", ["Children", "Teens", "Young Adult", "Adults"])
     project_knowledge_base.set("target_audience", target_audience)

     book_length = select_from_list(
         "Select the desired book length:",
         ["Short Story", "Novella", "Novel", "Full Book (Non-Fiction)"],
         allow_custom=False,
     )
     project_knowledge_base.set("book_length",book_length)

     num_chapters_str = typer.prompt(
        "Approximately how many chapters do you want (e.g., 10, 8-12, 20+)?",
        default="8-12",)
     project_knowledge_base.set("num_chapters_str", num_chapters_str)
     project_knowledge_base.set("num_chapters", num_chapters_str)
     inspired_by = typer.prompt("Are there any authors, books, or series that inspire you? (Optional)")
     project_knowledge_base.set("inspired_by",inspired_by)

def get_advanced_nonfiction_details(project_knowledge_base: ProjectKnowledgeBase): #MODIFIED
    project_knowledge_base.set("num_characters", 0)
    project_knowledge_base.set("num_chapters",0)
    project_knowledge_base.set("worldbuilding_needed",False)

    tone = select_from_list("Select Tone", ["Serious", "Funny", "Romantic", "Informative", "Persuasive"])
    project_knowledge_base.set("tone", tone)

    target_audience = select_from_list(
        "Select Target Audience",
        ["Children", "Teens", "Young Adult", "Adults", "Professional/Expert"],
    )
    project_knowledge_base.set("target_audience", target_audience)

    book_length = select_from_list(
        "Select the desired book length:",
        ["Article", "Essay", "Full Book"],
        allow_custom=False,
    )
    project_knowledge_base.set("book_length", book_length)

    author_experience = typer.prompt("What is your experience or expertise in this subject?")
    project_knowledge_base.set("author_experience",author_experience)

def get_advanced_business_details(project_knowledge_base: ProjectKnowledgeBase): #MODIFIED
    project_knowledge_base.set("num_characters",0)
    project_knowledge_base.set("num_chapters",0)
    project_knowledge_base.set("worldbuilding_needed",False)

    tone = select_from_list("Select Tone", ["Informative", "Motivational", "Instructive"])
    project_knowledge_base.set("tone", tone)

    target_audience = select_from_list(
        "Select Target Audience",
        [
            "Entrepreneurs",
            "Managers",
            "Employees",
            "Students",
            "General Business Readers",
        ],
    )
    project_knowledge_base.set("target_audience", target_audience)

    book_length = select_from_list(
        "Select the desired book length:",
        ["Pamphlet", "Guidebook", "Full Book"],
        allow_custom=False,
    )
    project_knowledge_base.set("book_length", book_length)

    key_takeaways = typer.prompt("What are the key takeaways you want readers to gain?")
    project_knowledge_base.set("key_takeaways",key_takeaways)

    case_studies = typer.confirm("Will you include case studies?")
    project_knowledge_base.set("case_studies", case_studies)

    actionable_advice = typer.confirm("Will you provide actionable advice/exercises?")
    project_knowledge_base.set("actionable_advice",actionable_advice)

    if project_knowledge_base.get("genre") == "Marketing":
        marketing_focus = select_from_list(
            "What is the primary focus of your marketing book?",
            [
                "SEO",
                "Performance Marketing",
                "Data Analytics",
                "Offline Marketing",
                "Content Marketing",
                "Social Media Marketing",
                "Branding",
            ],
            allow_custom=True,
        )
        project_knowledge_base.set("marketing_focus",marketing_focus)

    elif project_knowledge_base.get("genre") == "Sales":
        sales_focus = select_from_list(
            "What is the primary focus of your sales book?",
            [
                "Sales Techniques",
                "Pitching",
                "Negotiation",
                "Building Relationships",
                "Sales Management",
            ],
            allow_custom=True,
        )
        project_knowledge_base.set("sales_focus", sales_focus)

def get_advanced_research_details(project_knowledge_base: ProjectKnowledgeBase): #MODIFIED
    project_knowledge_base.set("num_characters",0)
    project_knowledge_base.set("num_chapters",0)
    project_knowledge_base.set("worldbuilding_needed",False)
    project_knowledge_base.set("tone","Formal and Objective")

    target_audience = select_from_list(
        "Select Target Audience",
        ["Academic Community", "Researchers", "Students", "General Public (if applicable)"],
    )
    project_knowledge_base.set("target_audience", target_audience)

    project_knowledge_base.set("book_length","Academic Article")

    research_question = typer.prompt("What is your primary research question?")
    project_knowledge_base.set("research_question",research_question)

    hypothesis = typer.prompt("What is your hypothesis (if applicable)?")
    project_knowledge_base.set("hypothesis", hypothesis)

    methodology = select_from_list(
        "Select your research methodology:",
        ["Quantitative", "Qualitative", "Mixed Methods"],
        allow_custom=True,
    )
    project_knowledge_base.set("methodology", methodology)

def get_dynamic_questions(project_knowledge_base: ProjectKnowledgeBase): #MODIFIED
    print("\nNow, let's dive into some genre-specific questions...")
    dynamic_questions = generate_questions_with_llm(project_knowledge_base.get("category"), project_knowledge_base.get("genre"))

    for q_id, question in dynamic_questions.items():
        answer = typer.prompt(question)
        project_knowledge_base.dynamic_questions[q_id] = answer
        save_project_data()

# --- Advanced Mode (Refactored) ---

def advanced_mode():
    console.print("\n[bold green]Starting in Advanced Mode...[/bold green]\n")

    project_name, title = get_project_name_and_title()
    project_knowledge_base = ProjectKnowledgeBase(project_name=project_name, title=title) #MODIFIED
    #LLM selection
    llm_choice = select_llm(project_knowledge_base) #MODIFIED
    project_manager.initialize_llm_client(llm_choice)

    get_category_and_genre(project_knowledge_base) #MODIFIED

    if project_knowledge_base.get("category") == "Fiction":
        get_advanced_fiction_details(project_knowledge_base) #MODIFIED
    elif project_knowledge_base.get("category") == "Non-Fiction":
        get_advanced_nonfiction_details(project_knowledge_base) #MODIFIED
    elif project_knowledge_base.get("category") == "Business":
        get_advanced_business_details(project_knowledge_base) #MODIFIED
    elif project_knowledge_base.get("category") == "Research Paper":
        get_advanced_research_details(project_knowledge_base) #MODIFIED

    get_review_preference(project_knowledge_base) #MODIFIED
    get_description(project_knowledge_base) #MODIFIED

    project_manager.initialize_project_with_data(project_knowledge_base)  # Initialize #MODIFIED

    get_dynamic_questions(project_knowledge_base) #MODIFIED

    if generate_and_review_concept(project_knowledge_base): #MODIFIED
        generate_and_edit_outline(project_knowledge_base) #MODIFIED
        generate_characters_if_needed(project_knowledge_base) #MODIFIED
        generate_worldbuilding_if_needed(project_knowledge_base) #MODIFIED
        write_and_review_chapters(project_knowledge_base)
        format_book(project_knowledge_base)
    else:
        print("Exiting.")
        return

    print("\nBook creation process complete (Advanced Mode).")


@app.command()
def start():
    """Starts the interactive book creation process."""
    introduction()
    mode = select_from_list("Choose a mode:", ["Simple", "Advanced"])
    if mode == "Simple":
        simple_mode()
    elif mode == "Advanced":
        advanced_mode()


# Removed the create command

@app.command()
def outline():
    """Generates a book outline."""
    project_manager.generate_outline()

@app.command()
def characters():
    """Generates character profiles."""
    project_manager.generate_characters()

@app.command()
def worldbuilding():
    """Generates worldbuilding details."""
    project_manager.generate_worldbuilding()

@app.command()
def write(chapter_number: int = typer.Option(..., prompt="Chapter number")):
    """Writes a specific chapter, with review process."""
    logger.info(f"📝 Agent {project_manager.agents['chapter_writer'].name} writing chapter {chapter_number}...") # type: ignore
    project_manager.write_and_review_chapter(chapter_number)
    logger.info(f"✅ Chapter {chapter_number} complete.")



@app.command()
def edit(chapter_number: int = typer.Option(..., prompt="Chapter number to edit")):
    """Edits and refines a specific chapter"""
    project_manager.edit_chapter(chapter_number)


@app.command()
def format():
    """Formats the entire book into a single Markdown or PDF file."""
    output_format = select_from_list("Choose output format:", ["Markdown (.md)", "PDF (.pdf)"])
    if output_format == "Markdown (.md)":
        output_path = str(project_manager.project_dir / "manuscript.md")
    else:
        output_path = str(project_manager.project_dir / "manuscript.pdf")
    project_manager.format_book(output_path)  # Pass output_path here
    print(f"\nBook formatted and saved to: {output_path}")

@app.command()
def research(query: str = typer.Option(..., prompt="Research query")):
    """Performs web research on a given query."""
    project_manager.research(query)

@app.command()
def resume(project_name: str = typer.Option(..., prompt="Project name to resume")):
    """Resumes a project from the last checkpoint."""
    try:
        project_manager.load_project_data(project_name)
        print(f"Project '{project_name}' loaded. Resuming...")

        # Determine where to resume from.  This logic is simplified for now
        # and assumes you'll mostly resume chapter writing. A more robust
        # solution would inspect more files.

        if not project_manager.project_knowledge_base: #MODIFIED
            print("ERROR resuming project")
            return

        if project_manager.project_dir and (project_manager.project_dir / "outline.md").exists():
            # Find the last written chapter
            last_chapter = 0
            num_chapters = project_manager.project_knowledge_base.get("num_chapters",1) #MODIFIED
            if isinstance(num_chapters, tuple):
                num_chapters = num_chapters[1]

            for i in range(1, num_chapters + 1):  # Iterate in order
                if (project_manager.project_dir / f"chapter_{i}.md").exists():
                    last_chapter = i
                else:
                    break  # Stop at the first missing chapter

            print(f"Last written chapter: {last_chapter}")

            # Check the project data and files to determine next steps
            for i in range(last_chapter + 1, num_chapters + 1):
                 project_manager.write_and_review_chapter(i)
            if typer.confirm("Do you want to format now the book?"):
                format()

        elif project_manager.project_knowledge_base:  # Project data exists, but no outline #MODIFIED
            # Resume from outline generation (this is a simplification)
            print("Resuming from outline generation...")
            project_manager.generate_outline()
            # ... (rest of the logic, similar to simple/advanced mode)

        else:
            print("No checkpoint found to resume from.")


    except FileNotFoundError:
        print(f"Project '{project_name}' not found.")
    except ValueError as e:
        print(f"Error loading project data: {e}")



if __name__ == "__main__":
    app()