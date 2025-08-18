import os
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import typer

# Import the functions to test
from libriscribe2.create_book_command import (
    EXIT_ENV_CONFIG_ERROR,
    EXIT_GENERAL_ERROR,
    EXIT_INVALID_ARGS,
    EXIT_LLM_INIT_ERROR,
    EXIT_NETWORK_ERROR,
    EXIT_SUCCESS,
    check_required_parameters,
    create_book,
    generate_unique_folder_name,
    validate_category,
    validate_chapters,
    validate_characters,
    validate_config_file,
    validate_default_model,
    validate_description,
    validate_env_file,
    validate_generation_flags,
    validate_genre,
    validate_language,
    validate_llm_provider,
    validate_log_file_path,
    validate_model_config,
    validate_output_dir,
    validate_title,
)


class TestValidationFunctions:
    def test_validate_title(self):
        # Valid title
        assert validate_title("My Book") == "My Book"
        assert validate_title("  My Book  ") == "My Book"

        # Invalid title
        with pytest.raises(ValueError):
            validate_title("")
        with pytest.raises(ValueError):
            validate_title("   ")

    def test_validate_output_dir(self):
        # None is valid
        assert validate_output_dir(None) is None

        # Existing directory
        with tempfile.TemporaryDirectory() as temp_dir:
            assert validate_output_dir(temp_dir) == temp_dir

        # Non-existent directory (should be created)
        with tempfile.TemporaryDirectory() as temp_dir:
            new_dir = os.path.join(temp_dir, "new_dir")
            assert validate_output_dir(new_dir) == new_dir
            assert os.path.exists(new_dir)

        # File instead of directory
        with tempfile.NamedTemporaryFile() as temp_file:
            with pytest.raises(ValueError):
                validate_output_dir(temp_file.name)

    def test_validate_category(self):
        # Standard categories
        assert validate_category("Fiction") == "Fiction"
        assert validate_category("Non-Fiction") == "Non-Fiction"
        assert validate_category("Business") == "Business"
        assert validate_category("Research Paper") == "Research Paper"

        # Non-standard category (should be accepted with warning)
        assert validate_category("Custom Category") == "Custom Category"

    def test_validate_genre(self):
        # Valid genre
        assert validate_genre("Fantasy") == "Fantasy"
        assert validate_genre("  Science Fiction  ") == "Science Fiction"

        # None should return "General"
        assert validate_genre(None) == "General"

    def test_validate_language(self):
        # Valid language
        assert validate_language("English") == "English"
        assert validate_language("  Spanish  ") == "Spanish"

        # Invalid language
        with pytest.raises(ValueError):
            validate_language("")
        with pytest.raises(ValueError):
            validate_language("   ")

    def test_validate_description(self):
        # Valid description
        assert validate_description("A great book") == "A great book"
        assert validate_description(None) is None

        # Invalid description
        with pytest.raises(ValueError):
            validate_description("")
        with pytest.raises(ValueError):
            validate_description("   ")

    def test_validate_chapters(self):
        # Valid chapters
        assert validate_chapters(10) == 10
        assert validate_chapters("10") == 10
        assert validate_chapters("8-12") == (8, 12)
        assert validate_chapters(None) is None

        # Invalid chapters
        with pytest.raises(ValueError):
            validate_chapters(0)
        with pytest.raises(ValueError):
            validate_chapters(-5)
        with pytest.raises(ValueError):
            validate_chapters("0")
        with pytest.raises(ValueError):
            validate_chapters("5-3")  # Invalid range
        with pytest.raises(ValueError):
            validate_chapters("invalid")

    def test_validate_characters(self):
        # Valid characters
        assert validate_characters(5) == 5
        assert validate_characters(0) == 0
        assert validate_characters(None) is None

        # Invalid characters
        with pytest.raises(ValueError):
            validate_characters(-1)

    def test_validate_env_file(self):
        # None is valid
        assert validate_env_file(None) is None

        # Existing file
        with tempfile.NamedTemporaryFile() as temp_file:
            assert validate_env_file(temp_file.name) == temp_file.name

        # Non-existent file
        with pytest.raises(ValueError):
            validate_env_file("/path/to/nonexistent/file.env")

    def test_validate_model_config(self):
        # None is valid
        assert validate_model_config(None) is None

        # Existing file
        with tempfile.NamedTemporaryFile() as temp_file:
            assert validate_model_config(temp_file.name) == temp_file.name

        # Non-existent file
        with pytest.raises(ValueError):
            validate_model_config("/path/to/nonexistent/config.json")

    def test_validate_config_file(self):
        # None is valid
        assert validate_config_file(None) is None

        # Existing file
        with tempfile.NamedTemporaryFile() as temp_file:
            assert validate_config_file(temp_file.name) == temp_file.name

        # Non-existent file
        with pytest.raises(ValueError):
            validate_config_file("/path/to/nonexistent/config.json")

    def test_validate_llm_provider(self):
        # None is valid
        assert validate_llm_provider(None) is None

        # Valid providers
        assert validate_llm_provider("openai") == "openai"
        assert validate_llm_provider("anthropic") == "anthropic"

        # Non-standard provider (should be accepted with warning)
        assert validate_llm_provider("custom_provider") == "custom_provider"

        # Empty provider
        with pytest.raises(ValueError):
            validate_llm_provider("")
        with pytest.raises(ValueError):
            validate_llm_provider("   ")

    def test_validate_default_model(self):
        # None is valid
        assert validate_default_model(None) is None

        # Valid model
        assert validate_default_model("gpt-4") == "gpt-4"

        # Empty model
        with pytest.raises(ValueError):
            validate_default_model("")
        with pytest.raises(ValueError):
            validate_default_model("   ")

    def test_validate_log_file_path(self):
        # None is valid
        assert validate_log_file_path(None) is None

        # Existing directory for log file
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "log.txt")
            assert validate_log_file_path(log_file) == log_file

        # Non-existent directory for log file (should be created)
        with tempfile.TemporaryDirectory() as temp_dir:
            new_dir = os.path.join(temp_dir, "new_dir")
            log_file = os.path.join(new_dir, "log.txt")
            assert validate_log_file_path(log_file) == log_file
            assert os.path.exists(new_dir)

    def test_validate_generation_flags(self):
        # Test with all=True
        flags = validate_generation_flags(True, generate_concept=False, generate_outline=False)
        assert flags["generate_concept"] is True
        assert flags["generate_outline"] is True
        assert flags["generate_characters"] is True
        assert flags["generate_worldbuilding"] is True
        assert flags["write_chapters"] is True
        assert flags["format_book"] is True

        # Test with all=False
        flags = validate_generation_flags(False, generate_concept=True, generate_outline=True)
        assert flags["generate_concept"] is True
        assert flags["generate_outline"] is True
        assert flags["generate_characters"] is False
        assert flags["generate_worldbuilding"] is False
        assert flags["write_chapters"] is False
        assert flags["format_book"] is False

    def test_generate_unique_folder_name(self):
        # Test basic functionality
        folder_name = generate_unique_folder_name("My Book Title")
        assert "my-book-title" in folder_name
        assert len(folder_name.split("-")[-1]) == 8  # Hash length

        # Test with special characters
        folder_name = generate_unique_folder_name("My Book: A Story!")
        assert "my-book-a-story" in folder_name

        # Test uniqueness - add small delay to ensure different timestamps
        import time

        folder_name1 = generate_unique_folder_name("Same Title")
        time.sleep(1)  # Small delay to ensure different timestamp
        folder_name2 = generate_unique_folder_name("Same Title")
        assert folder_name1 != folder_name2

    @patch("libriscribe2.create_book_command.typer.prompt")
    def test_check_required_parameters(self, mock_prompt):
        # Test with all required parameters
        params = {
            "title": "Test Book",
            "generate_characters": True,
            "characters": 5,
            "write_chapters": True,
            "chapters": 10,
        }
        result = check_required_parameters(params)
        assert result["title"] == "Test Book"
        assert result["characters"] == 5
        assert result["chapters"] == 10

        # Test with missing optional parameters - mock the prompts
        mock_prompt.side_effect = ["3", "5"]  # Return values for character and chapter prompts
        params = {
            "title": "Test Book",
            "generate_characters": True,
            "write_chapters": True,
        }
        result = check_required_parameters(params)
        assert result["title"] == "Test Book"
        assert result["characters"] == 3
        assert result["chapters"] == 5


class TestCreateBookCommand:
    @pytest.mark.asyncio
    @patch("libriscribe2.create_book_command.ProjectKnowledgeBase")
    @patch("libriscribe2.create_book_command.ProjectManagerAgent")
    @patch("libriscribe2.create_book_command.Settings")
    @patch("libriscribe2.create_book_command.console")
    @patch("libriscribe2.create_book_command.project_manager")
    async def test_create_book_success(
        self, mock_global_project_manager, mock_console, mock_settings, mock_project_manager, mock_project_kb
    ):
        # Setup mocks
        mock_project_manager_instance = AsyncMock()
        mock_project_manager.return_value = mock_project_manager_instance

        # Setup Settings mock properly
        mock_settings_instance = MagicMock()
        mock_settings_instance.default_llm = "openai"
        mock_settings_instance.openai_api_key = "test-key"
        mock_settings_instance.llm_timeout = 60
        mock_settings_instance.get_model_config.return_value = {"default": "gpt-4o-mini"}
        mock_settings.return_value = mock_settings_instance

        # Mock ProjectKnowledgeBase
        mock_kb_instance = MagicMock()
        mock_project_kb.return_value = mock_kb_instance
        mock_kb_instance.set = MagicMock()
        mock_kb_instance.get = MagicMock(return_value=0)  # For num_characters check

        # Mock the project manager methods
        mock_project_manager_instance.initialize_llm_client = MagicMock()
        mock_project_manager_instance.create_project_from_kb = MagicMock()
        mock_project_manager_instance.generate_concept = AsyncMock()
        mock_project_manager_instance.checkpoint = MagicMock()

        # Mock the global project_manager
        mock_global_project_manager.initialize_llm_client = MagicMock()
        mock_global_project_manager.create_project_from_kb = MagicMock()
        mock_global_project_manager.generate_concept = AsyncMock()
        mock_global_project_manager.checkpoint = MagicMock()
        mock_global_project_manager.project_dir = Path("/mock/project/dir")

        # Call the function with valid arguments
        result = await create_book(
            title="Test Book",
            category="Fiction",
            genre="Fantasy",
            generate_concept=True,
        )

        # Verify result
        assert result == EXIT_SUCCESS
        mock_console.print.assert_any_call("\n[green]🎉 Book creation process complete![/green]")

    @pytest.mark.asyncio
    @patch("libriscribe2.create_book_command.ProjectKnowledgeBase")
    @patch("libriscribe2.create_book_command.ProjectManagerAgent")
    @patch("libriscribe2.create_book_command.Settings")
    @patch("libriscribe2.create_book_command.console")
    @patch("libriscribe2.create_book_command.typer.prompt", return_value="Test Book")
    @patch("libriscribe2.create_book_command.project_manager")
    async def test_create_book_missing_title(
        self,
        mock_global_project_manager,
        mock_prompt,
        mock_console,
        mock_settings,
        mock_project_manager,
        mock_project_kb,
    ):
        # Setup mocks
        mock_project_manager_instance = AsyncMock()
        mock_project_manager.return_value = mock_project_manager_instance

        # Setup Settings mock properly
        mock_settings_instance = MagicMock()
        mock_settings_instance.default_llm = "openai"
        mock_settings_instance.openai_api_key = "test-key"
        mock_settings_instance.llm_timeout = 60
        mock_settings_instance.get_model_config.return_value = {"default": "gpt-4o-mini"}
        mock_settings.return_value = mock_settings_instance

        # Mock ProjectKnowledgeBase
        mock_kb_instance = MagicMock()
        mock_project_kb.return_value = mock_kb_instance
        mock_kb_instance.set = MagicMock()
        mock_kb_instance.get = MagicMock(return_value=0)  # For num_characters check

        # Mock the project manager methods
        mock_project_manager_instance.initialize_llm_client = MagicMock()
        mock_project_manager_instance.create_project_from_kb = MagicMock()
        mock_project_manager_instance.generate_concept = AsyncMock()
        mock_project_manager_instance.checkpoint = MagicMock()

        # Mock the global project_manager
        mock_global_project_manager.initialize_llm_client = MagicMock()
        mock_global_project_manager.create_project_from_kb = MagicMock()
        mock_global_project_manager.generate_concept = AsyncMock()
        mock_global_project_manager.checkpoint = MagicMock()
        mock_global_project_manager.project_dir = Path("/mock/project/dir")

        # Call the function with missing title
        result = await create_book(title=None)

        # Verify result
        assert result == EXIT_SUCCESS
        mock_prompt.assert_called_once_with("Book title")

    @pytest.mark.asyncio
    @patch("libriscribe2.create_book_command.console")
    @patch("libriscribe2.create_book_command.typer.prompt", side_effect=typer.Abort())
    async def test_create_book_abort_title_prompt(self, mock_prompt, mock_console):
        # Call the function with missing title and abort the prompt
        result = await create_book(title=None)

        # Verify result
        assert result == EXIT_INVALID_ARGS
        mock_console.print.assert_any_call("[red]Error: Book title is required[/red]")

    @pytest.mark.asyncio
    @patch("libriscribe2.create_book_command.console")
    async def test_create_book_invalid_chapters(self, mock_console):
        # Call the function with invalid chapters (zero is invalid)
        result = await create_book(title="Test Book", chapters="0")

        # Verify result
        assert result == EXIT_INVALID_ARGS
        # Check if the error message was printed - the actual error includes the format wrapper
        mock_console.print.assert_any_call(
            "[red]Error in command arguments: Invalid chapter format '0': Invalid chapter count: 0[/red]"
        )

    @pytest.mark.asyncio
    @patch("libriscribe2.create_book_command.Settings")
    @patch("libriscribe2.create_book_command.console")
    async def test_create_book_env_error(self, mock_console, mock_settings):
        # Setup mock to raise exception
        mock_settings.side_effect = Exception("Invalid environment configuration")

        # Call the function
        result = await create_book(title="Test Book")

        # Verify result
        assert result == EXIT_ENV_CONFIG_ERROR
        mock_console.print.assert_any_call(
            "[red]Error loading environment configuration: Invalid environment configuration[/red]"
        )

    @pytest.mark.asyncio
    @patch("libriscribe2.create_book_command.ProjectKnowledgeBase")
    @patch("libriscribe2.create_book_command.ProjectManagerAgent")
    @patch("libriscribe2.create_book_command.Settings")
    @patch("libriscribe2.create_book_command.console")
    @patch("libriscribe2.create_book_command.project_manager")
    async def test_create_book_llm_init_error(
        self, mock_global_project_manager, mock_console, mock_settings, mock_project_manager, mock_project_kb
    ):
        # Setup mocks
        mock_project_manager_instance = AsyncMock()
        mock_project_manager.return_value = mock_project_manager_instance
        mock_project_manager_instance.initialize_llm_client.side_effect = Exception("LLM initialization failed")

        # Setup Settings mock properly
        mock_settings_instance = MagicMock()
        mock_settings_instance.default_llm = "openai"
        mock_settings_instance.openai_api_key = "test-key"
        mock_settings_instance.llm_timeout = 60
        mock_settings_instance.get_model_config.return_value = {"default": "gpt-4o-mini"}
        mock_settings.return_value = mock_settings_instance

        # Mock ProjectKnowledgeBase
        mock_kb_instance = MagicMock()
        mock_project_kb.return_value = mock_kb_instance
        mock_kb_instance.set = MagicMock()
        mock_kb_instance.get = MagicMock(return_value=0)  # For num_characters check

        # Mock the global project_manager
        mock_global_project_manager.initialize_llm_client.side_effect = Exception("LLM initialization failed")

        # Call the function
        result = await create_book(title="Test Book")

        # Verify result
        assert result == EXIT_LLM_INIT_ERROR
        mock_console.print.assert_any_call("[red]Error initializing LLM client: LLM initialization failed[/red]")

    @pytest.mark.asyncio
    @patch("libriscribe2.create_book_command.ProjectKnowledgeBase")
    @patch("libriscribe2.create_book_command.ProjectManagerAgent")
    @patch("libriscribe2.create_book_command.Settings")
    @patch("libriscribe2.create_book_command.console")
    @patch("libriscribe2.create_book_command.project_manager")
    async def test_create_book_file_system_error(
        self, mock_global_project_manager, mock_console, mock_settings, mock_project_manager, mock_project_kb
    ):
        # Setup mocks
        mock_project_manager_instance = AsyncMock()
        mock_project_manager.return_value = mock_project_manager_instance
        mock_project_manager_instance.create_project_from_kb.side_effect = Exception("File system error")

        # Setup Settings mock properly
        mock_settings_instance = MagicMock()
        mock_settings_instance.default_llm = "openai"
        mock_settings_instance.openai_api_key = "test-key"
        mock_settings_instance.llm_timeout = 60
        mock_settings_instance.get_model_config.return_value = {"default": "gpt-4o-mini"}
        mock_settings.return_value = mock_settings_instance

        # Mock ProjectKnowledgeBase
        mock_kb_instance = MagicMock()
        mock_project_kb.return_value = mock_kb_instance
        mock_kb_instance.set = MagicMock()
        mock_kb_instance.get = MagicMock(return_value=0)  # For num_characters check

        # Mock the global project_manager
        mock_global_project_manager.create_project_from_kb.side_effect = Exception("File system error")

        # Call the function
        result = await create_book(title="Test Book")

        # Verify result
        assert result == EXIT_GENERAL_ERROR
        mock_console.print.assert_any_call("[red]ERROR: File system error[/red]")

    @pytest.mark.asyncio
    @patch("libriscribe2.create_book_command.ProjectKnowledgeBase")
    @patch("libriscribe2.create_book_command.ProjectManagerAgent")
    @patch("libriscribe2.create_book_command.Settings")
    @patch("libriscribe2.create_book_command.console")
    @patch("libriscribe2.create_book_command.project_manager")
    async def test_create_book_generation_error(
        self, mock_global_project_manager, mock_console, mock_settings, mock_project_manager, mock_project_kb
    ):
        # Setup mocks
        mock_project_manager_instance = AsyncMock()
        mock_project_manager.return_value = mock_project_manager_instance
        mock_project_manager_instance.generate_concept.side_effect = Exception("Generation error")

        # Setup Settings mock properly
        mock_settings_instance = MagicMock()
        mock_settings_instance.default_llm = "openai"
        mock_settings_instance.openai_api_key = "test-key"
        mock_settings_instance.llm_timeout = 60
        mock_settings_instance.get_model_config.return_value = {"default": "gpt-4o-mini"}
        mock_settings.return_value = mock_settings_instance

        # Mock ProjectKnowledgeBase
        mock_kb_instance = MagicMock()
        mock_project_kb.return_value = mock_kb_instance
        mock_kb_instance.set = MagicMock()
        mock_kb_instance.get = MagicMock(return_value=0)  # For num_characters check

        # Mock the global project_manager
        mock_global_project_manager.initialize_llm_client = MagicMock()
        mock_global_project_manager.create_project_from_kb = MagicMock()
        mock_global_project_manager.generate_concept.side_effect = Exception("Generation error")

        # Mock the project manager methods
        mock_project_manager_instance.initialize_llm_client = MagicMock()
        mock_project_manager_instance.create_project_from_kb = MagicMock()

        # Call the function
        result = await create_book(title="Test Book", generate_concept=True)

        # Verify result
        assert result == EXIT_GENERAL_ERROR
        mock_console.print.assert_any_call("[red]ERROR: Generation error[/red]")

    @pytest.mark.asyncio
    @patch("libriscribe2.create_book_command.ProjectKnowledgeBase")
    @patch("libriscribe2.create_book_command.ProjectManagerAgent")
    @patch("libriscribe2.create_book_command.Settings")
    @patch("libriscribe2.create_book_command.console")
    @patch("libriscribe2.create_book_command.project_manager")
    async def test_create_book_network_error(
        self, mock_global_project_manager, mock_console, mock_settings, mock_project_manager, mock_project_kb
    ):
        # Setup mocks
        mock_project_manager_instance = AsyncMock()
        mock_project_manager.return_value = mock_project_manager_instance
        mock_project_manager_instance.generate_concept.side_effect = ConnectionError("Network error")

        # Setup Settings mock properly
        mock_settings_instance = MagicMock()
        mock_settings_instance.default_llm = "openai"
        mock_settings_instance.openai_api_key = "test-key"
        mock_settings_instance.llm_timeout = 60
        mock_settings_instance.get_model_config.return_value = {"default": "gpt-4o-mini"}
        mock_settings.return_value = mock_settings_instance

        # Mock ProjectKnowledgeBase
        mock_kb_instance = MagicMock()
        mock_project_kb.return_value = mock_kb_instance
        mock_kb_instance.set = MagicMock()
        mock_kb_instance.get = MagicMock(return_value=0)  # For num_characters check

        # Mock the global project_manager
        mock_global_project_manager.initialize_llm_client = MagicMock()
        mock_global_project_manager.create_project_from_kb = MagicMock()
        mock_global_project_manager.generate_concept.side_effect = ConnectionError("Network error")

        # Mock the project manager methods
        mock_project_manager_instance.initialize_llm_client = MagicMock()
        mock_project_manager_instance.create_project_from_kb = MagicMock()

        # Call the function
        result = await create_book(title="Test Book", generate_concept=True)

        # Verify result
        assert result == EXIT_NETWORK_ERROR
        mock_console.print.assert_any_call("[red]Network error during book creation: Network error[/red]")

    @pytest.mark.asyncio
    @patch("libriscribe2.create_book_command.ProjectKnowledgeBase")
    @patch("libriscribe2.create_book_command.ProjectManagerAgent")
    @patch("libriscribe2.create_book_command.Settings")
    @patch("libriscribe2.create_book_command.console")
    @patch("libriscribe2.create_book_command.project_manager")
    async def test_create_book_with_all_validation_parameters(
        self, mock_global_project_manager, mock_console, mock_settings, mock_project_manager, mock_project_kb
    ):
        # Setup mocks
        mock_project_manager_instance = AsyncMock()
        mock_project_manager.return_value = mock_project_manager_instance
        mock_project_manager_instance.project_dir = Path("/mock/project/dir")

        # Setup Settings mock properly
        mock_settings_instance = MagicMock()
        mock_settings_instance.default_llm = "openai"
        mock_settings_instance.openai_api_key = "test-key"
        mock_settings_instance.llm_timeout = 60
        mock_settings_instance.get_model_config.return_value = {"default": "gpt-4o-mini"}
        mock_settings.return_value = mock_settings_instance

        # Mock ProjectKnowledgeBase
        mock_kb_instance = MagicMock()
        mock_project_kb.return_value = mock_kb_instance
        mock_kb_instance.set = MagicMock()
        mock_kb_instance.get = MagicMock(return_value=5)  # For num_characters check

        # Mock the global project_manager
        mock_global_project_manager.initialize_llm_client = MagicMock()
        mock_global_project_manager.create_project_from_kb = MagicMock()
        mock_global_project_manager.generate_concept = AsyncMock()
        mock_global_project_manager.generate_outline = AsyncMock()
        mock_global_project_manager.generate_characters = AsyncMock()
        mock_global_project_manager.generate_worldbuilding = AsyncMock()
        mock_global_project_manager.write_and_review_chapter = AsyncMock()
        mock_global_project_manager.format_book = AsyncMock()
        mock_global_project_manager.checkpoint = MagicMock()
        mock_global_project_manager.project_dir = Path("/mock/project/dir")

        # Mock the project manager methods
        mock_project_manager_instance.initialize_llm_client = MagicMock()
        mock_project_manager_instance.create_project_from_kb = MagicMock()
        mock_project_manager_instance.generate_concept = AsyncMock()
        mock_project_manager_instance.generate_outline = AsyncMock()
        mock_project_manager_instance.generate_characters = AsyncMock()
        mock_project_manager_instance.generate_worldbuilding = AsyncMock()
        mock_project_manager_instance.write_and_review_chapter = AsyncMock()
        mock_project_manager_instance.format_book = AsyncMock()
        mock_project_manager_instance.checkpoint = MagicMock()

        # Call the function with all validation parameters
        result = await create_book(
            title="Test Book",
            output_dir="/tmp/test",
            category="Fiction",
            genre="Fantasy",
            description="A test book",
            language="English",
            chapters="10",
            characters=5,
            worldbuilding=True,
            llm="openai",
            default_model="gpt-4",
            all=True,
        )

        # Verify result
        assert result == EXIT_SUCCESS
