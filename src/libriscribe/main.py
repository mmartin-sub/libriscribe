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
from libriscribe.project_data import ProjectData  # Import the new class
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

def select_llm(project_data: ProjectData):
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
    project_data.set("llm_provider", llm_choice)  # Store the choice
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
    if project_manager.project_dir:  # Check if project_dir is initialized
        project_data_path = project_manager.project_dir / "project_data.json"
        project_manager.save_project_data(str(project_data_path))
    else:
        logger.warning("Project directory not initialized. Cannot save project data.")


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

def get_category_and_genre(project_data: ProjectData):
    category = select_from_list(
        "Select the category of your book:",
        ["Fiction", "Non-Fiction", "Business", "Research Paper"],
        allow_custom=True,
    )
    project_data.set("category", category)

    if category == "Fiction":
        genre_options = ["Fantasy", "Science Fiction", "Romance", "Thriller", "Mystery", "Historical Fiction", "Horror", "Young Adult", "Contemporary"]
    elif category == "Non-Fiction":
        genre_options = ["Biography", "History", "Science", "Self-Help", "Travel", "True Crime", "Cookbook"]
    elif category == "Business":
        genre_options = ["Marketing", "Management", "Finance", "Entrepreneurship", "Leadership", "Sales", "Productivity"]
    elif category == "Research Paper":
        genre = typer.prompt("Enter the field of study for your research paper:")
        project_data.set("genre", genre)
        return
    else:
        genre_options = []  # Should not happen, but for safety

    if genre_options:
        genre = select_from_list(f"Select the genre/subject of your {category} book:", genre_options, allow_custom=True)
        project_data.set("genre", genre)



def get_book_length(project_data: ProjectData):
    book_length = select_from_list(
        "Select the desired book length:",
        ["Short Story", "Novella", "Novel", "Full Book (Non-Fiction)"],
        allow_custom=False,
    )
    project_data.set("book_length", book_length)

def get_fiction_details(project_data: ProjectData):
    if project_data.category == "Fiction":
        num_characters = typer.prompt("How many main characters do you envision?", type=int)
        project_data.set("num_characters", num_characters)
        worldbuilding_needed = typer.confirm("Does this book require extensive worldbuilding?")
        project_data.set("worldbuilding_needed", worldbuilding_needed)
    else:
        project_data.set("num_characters", 0)
        project_data.set("worldbuilding_needed", False)

def get_review_preference(project_data: ProjectData):
    review_preference = select_from_list("How would you like the book to be reviewed?", ["Human", "AI"])
    project_data.set("review_preference", review_preference)

def get_description(project_data: ProjectData):
    description = typer.prompt("Provide a brief description of your book")
    project_data.set("description", description)

def generate_and_review_concept(project_data: ProjectData):
    print("\nGenerating a detailed book concept...")
    project_manager.generate_concept()
    project_manager.checkpoint() # Checkpoint
    print(f"\nConcept generated. Here's the refined information:")
    print(f"  Title: {project_data.get('title', 'Untitled')}")
    print(f"  Logline: {project_data.get('logline', 'No logline available')}")
    print(f"  Description:\n{project_data.get('description', 'No description available')}")
    return typer.confirm("Do you want to proceed with generating an outline based on this concept?")


def generate_and_edit_outline(project_data: ProjectData):
    print("\nGenerating outline...")
    project_manager.generate_outline()
    project_manager.checkpoint()  # Checkpoint after outline
    print(f"\nOutline generated! Check the file: {project_manager.project_dir}/outline.md")

    if typer.confirm("Do you want to review and edit the outline now?"):
        typer.edit(filename=str(project_manager.project_dir / "outline.md"))
        print("\nChanges saved.")


def generate_characters_if_needed(project_data: ProjectData):
     if project_data.get("num_characters", 0) > 0:  # Use get with default
        if typer.confirm("Do you want to generate character profiles?"):
            print("\nGenerating characters...")
            project_manager.generate_characters()
            project_manager.checkpoint() # Checkpoint
            print(f"\nCharacter profiles generated! Check the file: {project_manager.project_dir}/characters.json")

def generate_worldbuilding_if_needed(project_data: ProjectData):
    if project_data.get("worldbuilding_needed", False):  # Use get with default
        if typer.confirm("Do you want to generate worldbuilding details?"):
            print("\nGenerating worldbuilding...")
            project_manager.generate_worldbuilding()
            project_manager.checkpoint() # Checkpoint
            print(f"\nWorldbuilding details generated! Check the file: {project_manager.project_dir}/world.json")

def write_and_review_chapters(project_data: ProjectData):
    num_chapters = project_data.get("num_chapters", 1)
    if isinstance(num_chapters, tuple):
        num_chapters = num_chapters[1]

    for i in range(1, num_chapters + 1):
        chapter_path = str(project_manager.project_dir / f"chapter_{i}.md")

        if project_manager.does_chapter_exist(i):
            overwrite = typer.confirm(f"Chapter {i} already exists. Overwrite?")
            if not overwrite:
                print(f"Skipping chapter {i}.")
                continue
        for step in track(range(100), description=f"Writing Chapter {i}..."): # Added progress bar
            project_manager.write_and_review_chapter(i)
        project_manager.checkpoint() #Checkpoint

def format_book(project_data: ProjectData):
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
    """The original simple mode, now with sequential execution and broken down into functions."""
    print("\nStarting in Simple Mode...\n")

    project_name, title = get_project_name_and_title()
    project_data = ProjectData(project_name=project_name, title=title)

    # LLM Selection after project name
    llm_choice = select_llm(project_data)
    project_manager.initialize_llm_client(llm_choice) # Initialize here

    get_category_and_genre(project_data)
    get_book_length(project_data)
    get_fiction_details(project_data)  # Only called if category is Fiction
    get_review_preference(project_data)
    get_description(project_data)

    project_manager.initialize_project_with_data(project_data) # Initialize

    if generate_and_review_concept(project_data):
        generate_and_edit_outline(project_data)
        generate_characters_if_needed(project_data)
        generate_worldbuilding_if_needed(project_data)
        write_and_review_chapters(project_data)
        format_book(project_data)
    else:
        print("Exiting.")
        return

    print("\nBook creation process complete (Simple Mode).")

# --- Helper Functions for Advanced Mode ---

def get_advanced_fiction_details(project_data: ProjectData):
     num_characters_str = typer.prompt(
            "How many main characters do you envision (e.g., 3, 2-4, 5+)?", default="2-3"
        )
     project_data.set("num_characters_str",num_characters_str)
     project_data.set("num_characters", num_characters_str)

     worldbuilding_needed = typer.confirm("Does this book require extensive worldbuilding?")
     project_data.set("worldbuilding_needed", worldbuilding_needed)

     tone = select_from_list("Select Tone", ["Serious", "Funny", "Romantic", "Informative", "Persuasive"])
     project_data.set("tone", tone)

     target_audience = select_from_list("Select Target Audience", ["Children", "Teens", "Young Adult", "Adults"])
     project_data.set("target_audience", target_audience)

     book_length = select_from_list(
         "Select the desired book length:",
         ["Short Story", "Novella", "Novel", "Full Book (Non-Fiction)"],
         allow_custom=False,
     )
     project_data.set("book_length",book_length)

     num_chapters_str = typer.prompt(
        "Approximately how many chapters do you want (e.g., 10, 8-12, 20+)?",
        default="8-12",)
     project_data.set("num_chapters_str", num_chapters_str)
     project_data.set("num_chapters", num_chapters_str)
     inspired_by = typer.prompt("Are there any authors, books, or series that inspire you? (Optional)")
     project_data.set("inspired_by",inspired_by)

def get_advanced_nonfiction_details(project_data: ProjectData):
    project_data.set("num_characters", 0)
    project_data.set("num_chapters",0)
    project_data.set("worldbuilding_needed",False)

    tone = select_from_list("Select Tone", ["Serious", "Funny", "Romantic", "Informative", "Persuasive"])
    project_data.set("tone", tone)

    target_audience = select_from_list(
        "Select Target Audience",
        ["Children", "Teens", "Young Adult", "Adults", "Professional/Expert"],
    )
    project_data.set("target_audience", target_audience)

    book_length = select_from_list(
        "Select the desired book length:",
        ["Article", "Essay", "Full Book"],
        allow_custom=False,
    )
    project_data.set("book_length", book_length)

    author_experience = typer.prompt("What is your experience or expertise in this subject?")
    project_data.set("author_experience",author_experience)

def get_advanced_business_details(project_data: ProjectData):
    project_data.set("num_characters",0)
    project_data.set("num_chapters",0)
    project_data.set("worldbuilding_needed",False)

    tone = select_from_list("Select Tone", ["Informative", "Motivational", "Instructive"])
    project_data.set("tone", tone)

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
    project_data.set("target_audience", target_audience)

    book_length = select_from_list(
        "Select the desired book length:",
        ["Pamphlet", "Guidebook", "Full Book"],
        allow_custom=False,
    )
    project_data.set("book_length", book_length)

    key_takeaways = typer.prompt("What are the key takeaways you want readers to gain?")
    project_data.set("key_takeaways",key_takeaways)

    case_studies = typer.confirm("Will you include case studies?")
    project_data.set("case_studies", case_studies)

    actionable_advice = typer.confirm("Will you provide actionable advice/exercises?")
    project_data.set("actionable_advice",actionable_advice)

    if project_data.get("genre") == "Marketing":
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
        project_data.set("marketing_focus",marketing_focus)

    elif project_data.get("genre") == "Sales":
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
        project_data.set("sales_focus", sales_focus)

def get_advanced_research_details(project_data: ProjectData):
    project_data.set("num_characters",0)
    project_data.set("num_chapters",0)
    project_data.set("worldbuilding_needed",False)
    project_data.set("tone","Formal and Objective")

    target_audience = select_from_list(
        "Select Target Audience",
        ["Academic Community", "Researchers", "Students", "General Public (if applicable)"],
    )
    project_data.set("target_audience", target_audience)

    project_data.set("book_length","Academic Article")

    research_question = typer.prompt("What is your primary research question?")
    project_data.set("research_question",research_question)

    hypothesis = typer.prompt("What is your hypothesis (if applicable)?")
    project_data.set("hypothesis", hypothesis)

    methodology = select_from_list(
        "Select your research methodology:",
        ["Quantitative", "Qualitative", "Mixed Methods"],
        allow_custom=True,
    )
    project_data.set("methodology", methodology)

def get_dynamic_questions(project_data: ProjectData):
    print("\nNow, let's dive into some genre-specific questions...")
    dynamic_questions = generate_questions_with_llm(project_data.get("category"), project_data.get("genre"))

    for q_id, question in dynamic_questions.items():
        answer = typer.prompt(question)
        project_data.dynamic_questions[q_id] = answer
        save_project_data()

# --- Advanced Mode (Refactored) ---

def advanced_mode():
    console.print("\n[bold green]Starting in Advanced Mode...[/bold green]\n")

    project_name, title = get_project_name_and_title()
    project_data = ProjectData(project_name=project_name, title=title)
    #LLM selection
    llm_choice = select_llm(project_data)
    project_manager.initialize_llm_client(llm_choice)

    get_category_and_genre(project_data)

    if project_data.get("category") == "Fiction":
        get_advanced_fiction_details(project_data)
    elif project_data.get("category") == "Non-Fiction":
        get_advanced_nonfiction_details(project_data)
    elif project_data.get("category") == "Business":
        get_advanced_business_details(project_data)
    elif project_data.get("category") == "Research Paper":
        get_advanced_research_details(project_data)

    get_review_preference(project_data)
    get_description(project_data)

    project_manager.initialize_project_with_data(project_data)  # Initialize

    get_dynamic_questions(project_data)

    if generate_and_review_concept(project_data):
        generate_and_edit_outline(project_data)
        generate_characters_if_needed(project_data)
        generate_worldbuilding_if_needed(project_data)
        write_and_review_chapters(project_data)
        format_book(project_data)

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


@app.command()
def create(
    project_name: str = typer.Option(..., prompt="Project name"),
    title: str = typer.Option(..., prompt="Book title"),
    genre: str = typer.Option(..., prompt="Genre"),
    description: str = typer.Option(..., prompt="Brief description"),
    category: str = typer.Option(
        ..., prompt="Category (fiction, non-fiction, business, research paper)"
    ),
    num_characters: int = typer.Option(0, prompt="Number of main characters (if fiction)"),
    worldbuilding_needed: bool = typer.Option(
        False, prompt="Extensive worldbuilding needed? (if fiction)"
    ),
):
    """Creates a new book project (non-interactive version)."""
    project_data = ProjectData(
        project_name=project_name,
        title=title,
        genre=genre,
        description=description,
        category=category,
        num_characters=num_characters,
        worldbuilding_needed=worldbuilding_needed,
        review_preference="AI",  # Default to AI review
        book_length="Novel" if category == "fiction" else "Full Book",  # Default book length
    )
    project_manager.initialize_project_with_data(project_data)



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

        if not project_manager.project_data:
            print("ERROR resuming project")
            return

        if project_manager.project_dir and (project_manager.project_dir / "outline.md").exists():
            # Find the last written chapter
            last_chapter = 0
            num_chapters = project_manager.project_data.get("num_chapters",1)
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

        elif project_manager.project_data:  # Project data exists, but no outline
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