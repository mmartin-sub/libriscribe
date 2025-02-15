# src/libriscribe/main.py
import typer
from libriscribe.agents.project_manager import ProjectManagerAgent
from typing import Optional, List, Dict, Any
from libriscribe.utils.openai_client import OpenAIClient
import json
from rich.console import Console  # For colored output
from rich.prompt import Prompt  # For interactive prompts
from rich.panel import Panel
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

console = Console()
app = typer.Typer()
project_manager = ProjectManagerAgent()
openai_client = OpenAIClient()

# Set up logger with level
logger = logging.getLogger(__name__)


def introduction():
    """Prints a welcome message with color and emojis."""
    console.print(
        Panel(
            "[bold blue]📚✨ Welcome to Libriscribe! ✨📚[/bold blue]\n\n"
            "Libriscribe is an AI-powered open-source book creation system made by Lenxys. The system is designed to help you write your book, "
            "from initial concept to a polished manuscript. It uses a multi-agent approach, where "
            "specialized AI agents collaborate to handle different stages of the book creation process.\n\n"
            "This is version 0.2.0, a command-line interface (CLI) implementation. "
            "You can interact with Libriscribe through simple commands to guide the AI.\n\n"
            "Let's get started!",
            title="[bold blue]Libriscribe[/bold blue]",
            border_style="blue",
        )
    )


def select_from_list(
    prompt: str, options: List[str], allow_custom: bool = False
) -> str:
    """Presents options using rich.prompt.Prompt and returns the selection."""
    console.print(f"[bold]{prompt}[/bold]")
    for i, option in enumerate(options):
        console.print(f"[cyan]{i + 1}.[/cyan] {option}")
    if allow_custom:
        console.print(f"[cyan]{len(options) + 1}.[/cyan] Custom (enter your own)")

    while True:
        # Use Prompt.ask with choices parameter for interactive selection
        choices = [str(i) for i in range(1, len(options) + 1)]
        if allow_custom:
            choices.append(str(len(options) + 1))

        choice = Prompt.ask(
            "Enter the number of your choice", choices=choices, show_choices=False
        )
        try:
            choice_index = int(choice) - 1
            if 0 <= choice_index < len(options):
                return options[choice_index]
            elif allow_custom and choice_index == len(options):
                return Prompt.ask("Enter your custom value")
            else:
                console.print("[red]Invalid choice. Please try again.[/red]")
        except ValueError:
            console.print("[red]Invalid input. Please enter a number.[/red]")


def save_project_data():
    project_data_path = project_manager.project_dir / "project_data.json"
    from libriscribe.utils.file_utils import write_json_file  # Avoid circular imports

    write_json_file(str(project_data_path), project_manager.project_data)


def generate_questions_with_llm(category: str, genre: str) -> Dict[str, Any]:
    """Generates genre-specific questions using the OpenAI API."""
    prompt = f"""
    Generate a list of 5-7 KEY questions, in JSON format, that are highly specific to creating a {category} book in the {genre} genre.
    The questions should help define the book's unique aspects, target audience, and core elements.  Do NOT include generic questions
    like 'title' or 'description'. Focus on the nuances of THIS genre.  Output as a JSON object with question IDs as keys (e.g., "q1", "q2") and
    the questions themselves as values.

    Example for category='Fiction', genre='Fantasy':

    {{
        "q1": "What is the source and nature of magic in this world (if any)?",
        "q2": "What are the major races or species, and what are their relationships?",
        "q3": "What is the central conflict or quest driving the narrative?",
        "q4": "What are the key locations, and what makes them unique?",
        "q5": "Are there any specific cultural traditions or customs that shape the world?",
        "q6": "What kind of tone or atmosphere do you want to create (e.g., epic, dark, whimsical)?",
        "q7": "Which authors or works inspire you in this genre?"
    }}

    Now, generate questions for category='{category}', genre='{genre}'.
    """
    try:
        response = openai_client.generate_content(prompt, max_tokens=500)
        questions = json.loads(response)  # Parse JSON
        return questions
    except Exception as e:
        logger.error(f"Error generating questions with LLM: {e}")
        print(f"Error generating questions with LLM: {e}")  # Also print to console
        return {}
    except json.JSONDecodeError:
        logger.error("Error: Could not decode the answer from the LLM.")
        print("Error: Could not decode the answer from the LLM.")
        return {}


@app.command()
def start():
    """Starts the interactive book creation process."""
    introduction()

    mode = select_from_list("Choose a mode:", ["Simple", "Advanced"])

    if mode == "Simple":
        simple_mode()  # Call directly, no asyncio.run()
    elif mode == "Advanced":
        advanced_mode()  # Call directly, no asyncio.run()


def simple_mode():
    """The original simple mode, now with sequential execution."""
    from pathlib import Path
    print("\nStarting in Simple Mode...\n")
    project_name = typer.prompt("Enter a project name (this will be the directory name)")
    title = typer.prompt("What is the title of your book?")
    # --- Category Selection ---
    category = select_from_list(
        "Select the category of your book:",
        ["Fiction", "Non-Fiction", "Business", "Research Paper"],
        allow_custom=True,
    )
    project_manager.project_data["category"] = category
    # --- Genre/Subject Selection (Conditional) ---
    if category == "Fiction":
        genre = select_from_list(
            "Select the genre of your fiction book:",
            [
                "Fantasy",
                "Science Fiction",
                "Romance",
                "Thriller",
                "Mystery",
                "Historical Fiction",
                "Horror",
                "Young Adult",
                "Contemporary",
            ],
            allow_custom=True,
        )
    elif category == "Non-Fiction":
        genre = select_from_list(
            "Select the subject of your non-fiction book:",
            [
                "Biography",
                "History",
                "Science",
                "Self-Help",
                "Travel",
                "True Crime",
                "Cookbook",
            ],
            allow_custom=True,
        )
    elif category == "Business":
        genre = select_from_list(
            "Select the subject of your business book:",
            [
                "Marketing",
                "Management",
                "Finance",
                "Entrepreneurship",
                "Leadership",
                "Sales",
                "Productivity",
            ],
            allow_custom=True,
        )
    elif category == "Research Paper":
        genre = typer.prompt("Enter the field of study for your research paper:")

    project_manager.project_data["genre"] = genre
    # --- Book Length Selection (Simple) ---
    book_length = select_from_list(
        "Select the desired book length:",
        ["Short Story", "Novella", "Novel", "Full Book (Non-Fiction)"],
        allow_custom=False,
    )
    project_manager.project_data["book_length"] = book_length

    if category.lower() == "fiction":
        num_characters = typer.prompt(
            "How many main characters do you envision?", type=int
        )
        worldbuilding_needed = typer.confirm(
            "Does this book require extensive worldbuilding?"
        )
    else:
        num_characters = 0
        worldbuilding_needed = False

    project_manager.project_data["num_characters"] = num_characters
    project_manager.project_data["worldbuilding_needed"] = worldbuilding_needed

    review_preference = select_from_list(
        "How would you like the book to be reviewed?", ["Human", "AI"]
    )
    project_manager.project_data["review_preference"] = review_preference

    description = typer.prompt("Provide a brief description of your book")
    project_manager.project_data["description"] = description

    # --- Create and Initialize Project ---
    project_manager.create_project(
        project_name,
        title,
        genre,
        description,
        category,
        num_characters,
        worldbuilding_needed,
    )
    save_project_data()

    # --- Generate Concept ---
    print("\nGenerating a detailed book concept...")
    project_manager.generate_concept()
    print(f"\nConcept generated. Here's the refined information:")
    print(f"  Title: {project_manager.project_data.get('title', 'Untitled')}")
    print(f"  Logline: {project_manager.project_data.get('logline', 'No logline available')}")
    print(f"  Description:\n{project_manager.project_data.get('description', 'No description available')}")

    # --- Generate Outline ---
    if not typer.confirm("Do you want to proceed with generating an outline based on this concept?"):
        print("Exiting.")
        return  # Exit if user doesn't want to continue

    print("\nGenerating outline...")
    project_manager.generate_outline()
    print(f"\nOutline generated! Check the file: {project_manager.project_dir}/outline.md")

    if typer.confirm("Do you want to review and edit the outline now?"):
        typer.edit(filename=str(project_manager.project_dir / "outline.md"))
        print("\nChanges saved.")

    # --- Generate Characters (Conditional) ---
    if num_characters > 0:
        if not typer.confirm("Do you want to generate character profiles?"):
            print("Skipping character generation.")
        else:
            print("\nGenerating characters...")
            project_manager.generate_characters()
            print(f"\nCharacter profiles generated! Check the file: {project_manager.project_dir}/characters.json")

    # --- Generate Worldbuilding (Conditional) ---
    if worldbuilding_needed:
        if not typer.confirm("Do you want to generate worldbuilding details?"):
            print("Skipping worldbuilding.")
        else:
            print("\nGenerating worldbuilding...")
            project_manager.generate_worldbuilding()
            print(f"\nWorldbuilding details generated! Check the file: {project_manager.project_dir}/world.json")
    
    # --- Determine Number of Chapters to Write ---
    if 'num_chapters' in project_manager.project_data:
        if isinstance(project_manager.project_data['num_chapters'], tuple):
            num_chapters = project_manager.project_data['num_chapters'][1] #Max value
        else:
            num_chapters = project_manager.project_data['num_chapters']
    else:
      num_chapters = 1 # Default

    # --- Write Chapters (Sequentially) ---
    for i in range(1, num_chapters + 1):
        chapter_path = str(project_manager.project_dir / f"chapter_{i}.md")

        # Option 1: Remove the existence check (always overwrite)
        # if Path(chapter_path).exists():
        #     print(f"Chapter {i} already exists. Skipping writing.")
        #     continue  # Skip to the next chapter

        # Option 2: Ask the user if they want to overwrite (more user-friendly)
        if Path(chapter_path).exists():
            overwrite = typer.confirm(f"Chapter {i} already exists. Overwrite?")
            if not overwrite:
                print(f"Skipping chapter {i}.")
                continue

        project_manager.write_chapter(i)
        project_manager.review_content(i)

        if project_manager.project_data.get("review_preference") == "AI":
            project_manager.edit_chapter(i)
        elif project_manager.project_data.get("review_preference") == "Human":
            print(f"\nChapter {i} written to: {chapter_path}")
            review = typer.confirm("Do you want to review and edit this chapter now?")
            if review:
                typer.edit(filename=chapter_path)
                print("\nChanges saved.")
        project_manager.edit_style(i) 
    # --- Format Book ---
    if typer.confirm("Do you want to format the book now?"):
         output_format = select_from_list("Choose output format:", ["Markdown (.md)", "PDF (.pdf)"])
         if output_format == "Markdown (.md)":
             output_path = str(project_manager.project_dir / "manuscript.md")
         else:
             output_path = str(project_manager.project_dir / "manuscript.pdf")
         project_manager.format_book(output_path)  # Pass output_path here
         print(f"\nBook formatted and saved to: {output_path}")
    print("\nBook creation process complete (Simple Mode).")


def advanced_mode():
    """The more comprehensive, interactive mode."""
    # ... (All the existing information gathering code) ...
    console.print("\n[bold green]Starting in Advanced Mode...[/bold green]\n")

    project_name = typer.prompt("Enter a project name (this will be the directory name)")

    # --- Category Selection ---
    category = select_from_list(
        "Select the category of your book:",
        ["Fiction", "Non-Fiction", "Business", "Research Paper"],
        allow_custom=True,
    )
    project_manager.project_data["category"] = category

    # --- Genre/Subject Selection (Conditional) ---
    if category == "Fiction":
        genre = select_from_list(
            "Select the genre of your fiction book:",
            [
                "Fantasy",
                "Science Fiction",
                "Romance",
                "Thriller",
                "Mystery",
                "Historical Fiction",
                "Horror",
                "Young Adult",
                "Contemporary",
            ],
            allow_custom=True,
        )
        # --- Precise Character Count (Advanced) ---
        num_characters_str = typer.prompt(
            "How many main characters do you envision (e.g., 3, 2-4, 5+)?", default="2-3"
        )
        project_manager.project_data[
            "num_characters_str"
        ] = num_characters_str  # Store string representation

        # Parse the character count (handle ranges and +)
        if "-" in num_characters_str:
            try:
                num_characters_min, num_characters_max = map(
                    int, num_characters_str.split("-")
                )
                num_characters = (
                    num_characters_min,
                    num_characters_max,
                )  # Tuple for range
            except ValueError:
                num_characters = 2  # Default value on parsing error
                logger.warning(
                    f"Invalid character count input: {num_characters_str}. Using default value of 2"
                )

        elif "+" in num_characters_str:
            try:
                num_characters = int(num_characters_str.replace("+", ""))
            except ValueError:
                num_characters = 5  # Default value
                logger.warning(
                    f"Invalid character count input: {num_characters_str}. Using default of 5"
                )
        else:
            try:
                num_characters = int(num_characters_str)
            except ValueError:
                num_characters = 2
                logger.warning(
                    f"Invalid character count input: {num_characters_str}. Using default of 2"
                )
        project_manager.project_data["num_characters"] = num_characters
        worldbuilding_needed = typer.confirm(
            "Does this book require extensive worldbuilding?"
        )
        project_manager.project_data["worldbuilding_needed"] = worldbuilding_needed
        tone = select_from_list(
            "Select Tone", ["Serious", "Funny", "Romantic", "Informative", "Persuasive"]
        )
        project_manager.project_data["tone"] = tone
        target_audience = select_from_list(
            "Select Target Audience", ["Children", "Teens", "Young Adult", "Adults"]
        )
        project_manager.project_data["target_audience"] = target_audience
        # --- Book Length Selection (Advanced) ---
        book_length = select_from_list(
            "Select the desired book length:",
            ["Short Story", "Novella", "Novel", "Full Book (Non-Fiction)"],
            allow_custom=False,
        )
        project_manager.project_data["book_length"] = book_length

        # --- Precise Chapter Count (Advanced) ---
        num_chapters_str = typer.prompt(
            "Approximately how many chapters do you want (e.g., 10, 8-12, 20+)?",
            default="8-12",
        )
        project_manager.project_data[
            "num_chapters_str"
        ] = num_chapters_str  # Store String representation

        # Parse the chapter count. Very similar to the character parsing.
        if "-" in num_chapters_str:
            try:
                num_chapters_min, num_chapters_max = map(
                    int, num_chapters_str.split("-")
                )
                num_chapters = (
                    num_chapters_min,
                    num_chapters_max,
                )  # Store as a tuple
            except ValueError:
                num_chapters = 10
                logger.warning(
                    f"Invalid chapter count input: {num_chapters_str}. Using default of 10."
                )

        elif "+" in num_chapters_str:
            try:
                num_chapters = int(num_chapters_str.replace("+", ""))
            except ValueError:
                num_chapters = 20
                logger.warning(
                    f"Invalid chapter count input: {num_chapters_str}. Using default of 20"
                )
        else:
            try:
                num_chapters = int(num_chapters_str)
            except ValueError:
                num_chapters = 10
                logger.warning(
                    f"Invalid chapter count input: {num_chapters_str}. Using default of 10"
                )

        project_manager.project_data["num_chapters"] = num_chapters

        inspired_by = typer.prompt(
            "Are there any authors, books, or series that inspire you? (Optional)"
        )
        project_manager.project_data["inspired_by"] = inspired_by

    elif category == "Non-Fiction":
        genre = select_from_list(
            "Select the subject of your non-fiction book:",
            [
                "Biography",
                "History",
                "Science",
                "Self-Help",
                "Travel",
                "True Crime",
                "Cookbook",
            ],
            allow_custom=True,
        )
        num_characters = 0  # Typically, non-fiction focuses on topics, not characters
        num_chapters = 0
        worldbuilding_needed = False
        tone = select_from_list(
            "Select Tone", ["Serious", "Funny", "Romantic", "Informative", "Persuasive"]
        )
        project_manager.project_data["tone"] = tone
        target_audience = select_from_list(
            "Select Target Audience",
            ["Children", "Teens", "Young Adult", "Adults", "Professional/Expert"],
        )
        project_manager.project_data["target_audience"] = target_audience

        book_length = select_from_list(
            "Select the desired book length:",
            ["Article", "Essay", "Full Book"],
            allow_custom=False,
        )
        project_manager.project_data["book_length"] = book_length
        author_experience = typer.prompt(
            "What is your experience or expertise in this subject?"
        )
        project_manager.project_data["author_experience"] = author_experience

    elif category == "Business":
        genre = select_from_list(
            "Select the subject of your business book:",
            [
                "Marketing",
                "Management",
                "Finance",
                "Entrepreneurship",
                "Leadership",
                "Sales",
                "Productivity",
            ],
            allow_custom=True,
        )
        num_characters = 0
        num_chapters = 0
        worldbuilding_needed = False
        tone = select_from_list("Select Tone", ["Informative", "Motivational", "Instructive"])
        project_manager.project_data["tone"] = tone

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
        project_manager.project_data["target_audience"] = target_audience

        book_length = select_from_list(
            "Select the desired book length:",
            ["Pamphlet", "Guidebook", "Full Book"],
            allow_custom=False,
        )
        project_manager.project_data["book_length"] = book_length

        # --- Business-Specific Questions ---
        key_takeaways = typer.prompt("What are the key takeaways you want readers to gain?")
        project_manager.project_data["key_takeaways"] = key_takeaways
        case_studies = typer.confirm("Will you include case studies?")
        project_manager.project_data["case_studies"] = case_studies
        actionable_advice = typer.confirm("Will you provide actionable advice/exercises?")
        project_manager.project_data["actionable_advice"] = actionable_advice

        # --- Further Business Sub-Genre Questions ---
        if genre == "Marketing":
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
            project_manager.project_data[
                "marketing_focus"
            ] = marketing_focus  # Store it

        elif genre == "Sales":
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
            project_manager.project_data["sales_focus"] = sales_focus

    elif category == "Research Paper":
        genre = typer.prompt("Enter the field of study for your research paper:")
        project_manager.project_data["genre"] = genre
        num_characters = 0
        num_chapters = 0
        worldbuilding_needed = False
        tone = "Formal and Objective"
        project_manager.project_data["tone"] = tone
        target_audience = select_from_list(
            "Select Target Audience",
            ["Academic Community", "Researchers", "Students", "General Public (if applicable)"],
        )
        project_manager.project_data["target_audience"] = target_audience
        book_length = "Academic Article"
        project_manager.project_data["book_length"] = book_length

        # --- Research Paper-Specific Questions ---
        research_question = typer.prompt("What is your primary research question?")
        project_manager.project_data["research_question"] = research_question
        hypothesis = typer.prompt("What is your hypothesis (if applicable)?")
        project_manager.project_data["hypothesis"] = hypothesis
        methodology = select_from_list(
            "Select your research methodology:",
            ["Quantitative", "Qualitative", "Mixed Methods"],
            allow_custom=True,
        )
        project_manager.project_data["methodology"] = methodology

    # --- General Questions (Apply to all categories) ---
    title = typer.prompt("What is the title of your book/paper?")
    project_manager.project_data["title"] = title
    description = typer.prompt("Provide a brief description:")
    project_manager.project_data["description"] = description

    # --- Review Preference ---
    review_preference = select_from_list(
        "How would you like the book to be reviewed?", ["Human", "AI"]
    )
    project_manager.project_data["review_preference"] = review_preference

    # --- Create Project ---
    project_manager.create_project(
        project_name,
        title,
        genre,
        description,
        category,
        num_characters,
        worldbuilding_needed,
    )
    save_project_data()

    # --- Generate and Ask Genre-Specific Questions ---
    print("\nNow, let's dive into some genre-specific questions...")
    dynamic_questions = generate_questions_with_llm(category, genre)

    for q_id, question in dynamic_questions.items():
        answer = typer.prompt(question)
        project_manager.project_data[q_id] = answer  # Store answers with question IDs
        save_project_data()

    # --- Concept Generation ---
    print("\nGenerating a detailed book concept...")
    project_manager.generate_concept()
    print(f"\nConcept generated. Here's the refined information:")
    print(
        f"  Title: {project_manager.project_data.get('title', 'Untitled')}"
    )  # Use .get()
    print(
        f"  Logline: {project_manager.project_data.get('logline', 'No logline available')}"
    )  # Use .get()
    print(
        f"  Description:\n{project_manager.project_data.get('description', 'No description available')}"
    )  # Use .get()

    # --- Next Steps (Outline, Characters, Worldbuilding) ---

    if typer.confirm(
        "Do you want to proceed with generating an outline based on this concept?"
    ):
        print("\nGenerating outline...")
        project_manager.generate_outline()
        print(
            f"\nOutline generated!  Check the file: {project_manager.project_dir}/outline.md"
        )
        # Confirmation to edit outline
        if typer.confirm("Do you want to review and edit the outline now?"):
            typer.edit(filename=str(project_manager.project_dir / "outline.md"))
            print("\nChanges saved.")

    if (
        "num_characters" in project_manager.project_data
        and project_manager.project_data["num_characters"] > 0
        and typer.confirm("Do you want to generate character profiles?")
    ):
        print("\nGenerating characters...")
        project_manager.generate_characters()
        print(
            f"\nCharacter profiles generated! Check the file: {project_manager.project_dir}/characters.json"
        )

    if worldbuilding_needed and typer.confirm(
        "Do you want to generate worldbuilding details?"
    ):
        print("\nGenerating worldbuilding...")
        project_manager.generate_worldbuilding()
        print(
            f"\nWorldbuilding details generated!  Check the file:{project_manager.project_dir}/world.json"
        )
     # --- Determine Number of Chapters to Write ---
    if 'num_chapters' in project_manager.project_data:
        if isinstance(project_manager.project_data['num_chapters'], tuple):
            num_chapters = project_manager.project_data['num_chapters'][1] #Max value
        else:
            num_chapters = project_manager.project_data['num_chapters']
    else:
      num_chapters = 1 # Default

    # --- Chapter Writing and Refinement Loop (Advanced Mode) ---
    for i in range(1, num_chapters + 1):
        chapter_path = str(project_manager.project_dir / f"chapter_{i}.md")

        # Optional Overwrite Check (consistent with simple_mode)
        if Path(chapter_path).exists():
            overwrite = typer.confirm(f"Chapter {i} already exists. Overwrite?")
            if not overwrite:
                print(f"Skipping chapter {i}.")
                continue

        project_manager.write_chapter(i)
        project_manager.review_content(i)  # Content review comes first

        if project_manager.project_data.get("review_preference") == "AI":
            project_manager.edit_chapter(i)
        elif project_manager.project_data.get("review_preference") == "Human":
            print(f"\nChapter {i} written to: {chapter_path}")
            review = typer.confirm("Do you want to review and edit this chapter now?")
            if review:
                typer.edit(filename=chapter_path)
                print("\nChanges saved.")

        project_manager.edit_style(i)

        # Optional Plagiarism/Fact-Checking (you can make this conditional)
        if project_manager.project_data.get("category") in ["non-fiction", "research paper"]:
            project_manager.check_plagiarism(i)
            project_manager.check_facts(i)
    
    # --- Formatting ---
    if typer.confirm("Do you want to format the book now?"):
        output_format = select_from_list("Choose output format:", ["Markdown (.md)", "PDF (.pdf)"])
        if output_format == "Markdown (.md)":
             output_path = str(project_manager.project_dir / "manuscript.md")
        else:
             output_path = str(project_manager.project_dir / "manuscript.pdf")

        project_manager.format_book(output_path)
        print(f"\nBook formatted and saved to: {output_path}")

    print("\nInitial setup complete. You can now use other commands like 'write', 'edit', 'research', and 'format'.")
    print("\nBook creation process complete (Advanced Mode).") # Indicate completion


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
    project_manager.create_project(
        project_name,
        title,
        genre,
        description,
        category,
        num_characters,
        worldbuilding_needed,
    )
    # For the non-interactive version, default to AI review.
    project_manager.project_data["review_preference"] = "AI"
    # Add a default book length
    project_manager.project_data["book_length"] = (
        "Novel" if category == "fiction" else "Full Book"
    )

    project_data_path = project_manager.project_dir / "project_data.json"
    from libriscribe.utils.file_utils import write_json_file

    write_json_file(str(project_data_path), project_manager.project_data)


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
    logger.info(
        f"📝 Agent {project_manager.agents['chapter_writer'].name} writing chapter {chapter_number}..."
    )  # type: ignore
    project_manager.write_chapter(chapter_number)
    logger.info(f"✅ Chapter {chapter_number} complete.")

    if project_manager.project_data.get("review_preference") == "Human":
        chapter_path = str(project_manager.project_dir / f"chapter_{chapter_number}.md")
        print(f"\nChapter {chapter_number} written to: {chapter_path}")
        review = typer.confirm("Do you want to review and edit this chapter now?")
        if review:
            typer.edit(
                filename=chapter_path
            )  # Opens the file in the default editor.
            print("\nChanges saved.")

    elif project_manager.project_data.get("review_preference") == "AI":
        logger.info(
            f"🧐 Agent {project_manager.agents['editor'].name} reviewing chapter {chapter_number}..."
        )  # type: ignore
        project_manager.edit_chapter(chapter_number)  # AI review
        logger.info(f"👍 Chapter {chapter_number} reviewed and edited by AI.")


@app.command()
def edit(chapter_number: int = typer.Option(..., prompt="Chapter number to edit")):
    """Edits and refines a specific chapter"""
    project_manager.edit_chapter(chapter_number)


@app.command()
def format():
    """Formats the entire book into a single Markdown or PDF file."""
    project_manager.format_book()


@app.command()
def research(query: str = typer.Option(..., prompt="Research query")):
    """Performs web research on a given query."""
    project_manager.research(query)


if __name__ == "__main__":
    app()