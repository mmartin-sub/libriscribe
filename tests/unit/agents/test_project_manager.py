"""
Unit tests for ProjectManagerAgent.

This module tests the core functionality of the ProjectManagerAgent class,
including initialization, LLM client setup, project management, and agent execution.
"""

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from libriscribe2.agents.project_manager import ProjectManagerAgent
from libriscribe2.knowledge_base import ProjectKnowledgeBase
from libriscribe2.settings import Settings
from libriscribe2.utils.llm_client import LLMClient


class TestProjectManagerAgent:
    """Test cases for ProjectManagerAgent."""

    def test_initialization(self):
        """Test ProjectManagerAgent initialization."""
        # Arrange
        settings = Settings()

        # Act
        agent = ProjectManagerAgent(settings=settings)

        # Assert
        assert agent.settings == settings
        assert agent.model_config == {}
        assert agent.project_knowledge_base is None
        assert agent.project_dir is None
        assert agent.llm_client is None
        assert agent.agents == {}
        assert agent.use_autogen is False
        assert agent.autogen_service is None

    def test_initialization_with_llm_client(self):
        """Test ProjectManagerAgent initialization with LLM client."""
        # Arrange
        settings = Settings()
        llm_client = MagicMock(spec=LLMClient)
        model_config = {"default": "gpt-4o-mini"}

        # Act
        agent = ProjectManagerAgent(
            settings=settings, llm_client=llm_client, model_config=model_config, use_autogen=True
        )

        # Assert
        assert agent.settings == settings
        assert agent.llm_client == llm_client
        assert agent.model_config == model_config
        assert agent.use_autogen is True

    @patch("libriscribe2.agents.project_manager.LLMClient")
    @patch("libriscribe2.agents.project_manager.ContentReviewerAgent")
    @patch("libriscribe2.agents.project_manager.ConceptGeneratorAgent")
    @patch("libriscribe2.agents.project_manager.OutlinerAgent")
    @patch("libriscribe2.agents.project_manager.CharacterGeneratorAgent")
    @patch("libriscribe2.agents.project_manager.WorldbuildingAgent")
    @patch("libriscribe2.agents.project_manager.ChapterWriterAgent")
    @patch("libriscribe2.agents.project_manager.EditorAgent")
    @patch("libriscribe2.agents.project_manager.ResearcherAgent")
    @patch("libriscribe2.agents.project_manager.FormattingAgent")
    @patch("libriscribe2.agents.project_manager.StyleEditorAgent")
    @patch("libriscribe2.agents.project_manager.PlagiarismCheckerAgent")
    @patch("libriscribe2.agents.project_manager.FactCheckerAgent")
    def test_initialize_llm_client(
        self,
        mock_fact_checker,
        mock_plagiarism_checker,
        mock_style_editor,
        mock_formatting,
        mock_researcher,
        mock_editor,
        mock_chapter_writer,
        mock_worldbuilding,
        mock_character_generator,
        mock_outliner,
        mock_concept_generator,
        mock_content_reviewer,
        mock_llm_client,
    ):
        """Test LLM client initialization."""
        # Arrange
        settings = Settings()
        agent = ProjectManagerAgent(settings=settings)
        mock_llm_client.return_value = MagicMock()

        # Configure all agent mocks to return proper instances
        for mock_agent_class in [
            mock_fact_checker,
            mock_plagiarism_checker,
            mock_style_editor,
            mock_formatting,
            mock_researcher,
            mock_editor,
            mock_chapter_writer,
            mock_worldbuilding,
            mock_character_generator,
            mock_outliner,
            mock_concept_generator,
            mock_content_reviewer,
        ]:
            mock_instance = MagicMock()
            mock_agent_class.return_value = mock_instance

        # Act
        agent.initialize_llm_client("openai", "test_user")

        # Assert
        mock_llm_client.assert_called_once()
        assert len(agent.agents) == 12
        assert "content_reviewer" in agent.agents
        assert "concept_generator" in agent.agents
        assert "outliner" in agent.agents
        assert "character_generator" in agent.agents
        assert "worldbuilding" in agent.agents
        assert "chapter_writer" in agent.agents
        assert "editor" in agent.agents
        assert "researcher" in agent.agents
        assert "formatting" in agent.agents
        assert "style_editor" in agent.agents
        assert "plagiarism_checker" in agent.agents
        assert "fact_checker" in agent.agents

    @patch("libriscribe2.agents.project_manager.LLMClient")
    @patch("libriscribe2.agents.project_manager.AutoGenService")
    def test_initialize_llm_client_with_autogen(self, mock_autogen_service, mock_llm_client):
        """Test LLM client initialization with AutoGen enabled."""
        # Arrange
        settings = Settings()
        agent = ProjectManagerAgent(settings=settings, use_autogen=True)
        mock_llm_client.return_value = MagicMock()
        mock_autogen_service.return_value = MagicMock()

        # Act
        agent.initialize_llm_client("openai", "test_user")

        # Assert
        assert agent.autogen_service is not None
        mock_autogen_service.assert_called_once()

    def test_initialize_llm_client_with_project_knowledge_base(self):
        """Test LLM client initialization with project knowledge base."""
        # Arrange
        settings = Settings()
        agent = ProjectManagerAgent(settings=settings)
        project_kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")
        agent.project_knowledge_base = project_kb

        with patch("libriscribe2.agents.project_manager.LLMClient") as mock_llm_client:
            mock_llm_client.return_value = MagicMock()

            # Act
            agent.initialize_llm_client("openai", "test_user")

            # Assert
            mock_llm_client.assert_called_once()
            call_args = mock_llm_client.call_args
            assert call_args[1]["project_name"] == "test_project"

    def test_create_project_from_kb(self):
        """Test creating project from knowledge base."""
        # Arrange
        settings = Settings()
        agent = ProjectManagerAgent(settings=settings)
        project_kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")

        with tempfile.TemporaryDirectory() as temp_dir:
            # Act
            agent.create_project_from_kb(project_kb, temp_dir)

            # Assert
            assert agent.project_knowledge_base == project_kb
            assert agent.project_dir == Path(temp_dir)
            assert project_kb.project_dir == Path(temp_dir)

    def test_create_project_from_kb_without_output_path(self):
        """Test creating project from knowledge base without output path."""
        # Arrange
        settings = Settings()
        agent = ProjectManagerAgent(settings=settings)
        project_kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")

        with patch.object(Path, "mkdir") as mock_mkdir:
            with patch.object(agent, "save_project_data") as mock_save:
                # Act
                agent.create_project_from_kb(project_kb)

                # Assert
                assert agent.project_knowledge_base == project_kb
                mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
                mock_save.assert_called_once()

    @patch("libriscribe2.agents.project_manager.ProjectKnowledgeBase.save_to_file")
    def test_save_project_data(self, mock_save):
        """Test saving project data."""
        # Arrange
        settings = Settings()
        agent = ProjectManagerAgent(settings=settings)
        project_kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")
        agent.project_knowledge_base = project_kb
        agent.project_dir = Path("/test/path")

        # Act
        agent.save_project_data()

        # Assert
        mock_save.assert_called_once_with(f"/test/path/{settings.project_data_filename}")

    def test_save_project_data_no_project(self):
        """Test saving project data when no project is set."""
        # Arrange
        settings = Settings()
        agent = ProjectManagerAgent(settings=settings)

        # Act & Assert - should not raise exception
        agent.save_project_data()

    @patch("libriscribe2.agents.project_manager.ProjectKnowledgeBase.load_from_file")
    def test_load_project_data_success(self, mock_load):
        """Test loading project data successfully."""
        # Arrange
        settings = Settings()
        agent = ProjectManagerAgent(settings=settings)
        project_kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")
        mock_load.return_value = project_kb

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create project directory and data file
            project_dir = Path(temp_dir) / "test_project"
            project_dir.mkdir(parents=True, exist_ok=True)
            project_data_file = project_dir / settings.project_data_filename
            project_data_file.write_text('{"project_name": "test_project"}')

            # Mock settings to use temp directory
            settings.projects_dir = temp_dir

            # Act
            agent.load_project_data("test_project")

            # Assert
            assert agent.project_knowledge_base is not None
            assert agent.project_knowledge_base == project_kb
            assert agent.project_dir == project_dir
            assert agent.project_knowledge_base.project_dir == project_dir
            mock_load.assert_called_once_with(str(project_data_file))

    def test_load_project_data_project_not_found(self):
        """Test loading project data when project directory doesn't exist."""
        # Arrange
        settings = Settings()
        agent = ProjectManagerAgent(settings=settings)

        with tempfile.TemporaryDirectory() as temp_dir:
            settings.projects_dir = temp_dir

            # Act & Assert
            with pytest.raises(FileNotFoundError, match="Project directory 'nonexistent_project' not found"):
                agent.load_project_data("nonexistent_project")

    def test_load_project_data_file_not_found(self):
        """Test loading project data when project_data.json doesn't exist."""
        # Arrange
        settings = Settings()
        agent = ProjectManagerAgent(settings=settings)

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create project directory but no data file
            project_dir = Path(temp_dir) / "test_project"
            project_dir.mkdir(parents=True, exist_ok=True)
            settings.projects_dir = temp_dir

            # Act & Assert
            with pytest.raises(FileNotFoundError, match="Project data file not found"):
                agent.load_project_data("test_project")

    @patch("libriscribe2.agents.project_manager.ProjectKnowledgeBase.load_from_file")
    def test_load_project_data_corrupted_file(self, mock_load):
        """Test loading project data when file is corrupted."""
        # Arrange
        settings = Settings()
        agent = ProjectManagerAgent(settings=settings)
        mock_load.side_effect = Exception("Corrupted JSON")

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create project directory and data file
            project_dir = Path(temp_dir) / "test_project"
            project_dir.mkdir(parents=True, exist_ok=True)
            project_data_file = project_dir / settings.project_data_filename
            project_data_file.write_text("invalid json")
            settings.projects_dir = temp_dir

            # Act & Assert
            with pytest.raises(ValueError, match="Corrupted project data"):
                agent.load_project_data("test_project")

    @patch("libriscribe2.agents.project_manager.ProjectKnowledgeBase.load_from_file")
    def test_load_project_data_load_returns_none(self, mock_load):
        """Test loading project data when load_from_file returns None."""
        # Arrange
        settings = Settings()
        agent = ProjectManagerAgent(settings=settings)
        mock_load.return_value = None

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create project directory and data file
            project_dir = Path(temp_dir) / "test_project"
            project_dir.mkdir(parents=True, exist_ok=True)
            project_data_file = project_dir / settings.project_data_filename
            project_data_file.write_text('{"project_name": "test_project"}')
            settings.projects_dir = temp_dir

            # Act & Assert
            with pytest.raises(ValueError, match="Failed to load project data"):
                agent.load_project_data("test_project")

    @pytest.mark.asyncio
    async def test_run_agent_success(self):
        """Test running an agent successfully."""
        # Arrange
        settings = Settings()
        agent = ProjectManagerAgent(settings=settings)
        project_kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")
        agent.project_knowledge_base = project_kb

        mock_agent = AsyncMock()
        agent.agents = {"test_agent": mock_agent}

        with patch.object(agent, "save_project_data") as mock_save:
            # Act
            await agent.run_agent("test_agent", test_param="value")

            # Assert
            mock_agent.execute.assert_called_once_with(project_kb, test_param="value")
            mock_save.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_agent_not_found(self):
        """Test running an agent that doesn't exist."""
        # Arrange
        settings = Settings()
        agent = ProjectManagerAgent(settings=settings)
        agent.agents = {}

        # Act & Assert
        with pytest.raises(ValueError, match="Agent nonexistent_agent not found"):
            await agent.run_agent("nonexistent_agent")

    @pytest.mark.asyncio
    async def test_run_agent_no_project_kb(self):
        """Test running an agent without project knowledge base."""
        # Arrange
        settings = Settings()
        agent = ProjectManagerAgent(settings=settings)
        agent.project_knowledge_base = None
        agent.agents = {"test_agent": AsyncMock()}

        # Act & Assert
        with pytest.raises(ValueError, match="Project knowledge base not initialized"):
            await agent.run_agent("test_agent")

    @pytest.mark.asyncio
    async def test_run_agent_exception(self):
        """Test running an agent that raises an exception."""
        # Arrange
        settings = Settings()
        agent = ProjectManagerAgent(settings=settings)
        project_kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")
        agent.project_knowledge_base = project_kb

        mock_agent = AsyncMock()
        mock_agent.execute.side_effect = Exception("Test error")
        agent.agents = {"test_agent": mock_agent}

        # Act & Assert
        with pytest.raises(Exception, match="Test error"):
            await agent.run_agent("test_agent")

    @pytest.mark.asyncio
    async def test_run_autogen_workflow_success(self):
        """Test running AutoGen workflow successfully."""
        # Arrange
        settings = Settings()
        agent = ProjectManagerAgent(settings=settings, use_autogen=True)
        project_kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")
        agent.project_knowledge_base = project_kb

        mock_autogen_service = AsyncMock()
        mock_autogen_service.create_book.return_value = True
        agent.autogen_service = mock_autogen_service

        with patch.object(agent, "save_project_data") as mock_save:
            # Act
            result = await agent.run_autogen_workflow()

            # Assert
            assert result is True
            mock_autogen_service.create_book.assert_called_once_with(project_kb)
            mock_save.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_autogen_workflow_no_service(self):
        """Test running AutoGen workflow without service."""
        # Arrange
        settings = Settings()
        agent = ProjectManagerAgent(settings=settings, use_autogen=False)

        # Act
        result = await agent.run_autogen_workflow()

        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_run_autogen_workflow_no_project_kb(self):
        """Test running AutoGen workflow without project knowledge base."""
        # Arrange
        settings = Settings()
        agent = ProjectManagerAgent(settings=settings, use_autogen=True)
        agent.project_knowledge_base = None

        mock_autogen_service = AsyncMock()
        agent.autogen_service = mock_autogen_service

        # Act
        result = await agent.run_autogen_workflow()

        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_run_autogen_workflow_failure(self):
        """Test running AutoGen workflow with failure."""
        # Arrange
        settings = Settings()
        agent = ProjectManagerAgent(settings=settings, use_autogen=True)
        project_kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")
        agent.project_knowledge_base = project_kb

        mock_autogen_service = AsyncMock()
        mock_autogen_service.create_book.return_value = False
        agent.autogen_service = mock_autogen_service

        # Act
        result = await agent.run_autogen_workflow()

        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_run_autogen_workflow_exception(self):
        """Test running AutoGen workflow with exception."""
        # Arrange
        settings = Settings()
        agent = ProjectManagerAgent(settings=settings, use_autogen=True)
        project_kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")
        agent.project_knowledge_base = project_kb

        mock_autogen_service = AsyncMock()
        mock_autogen_service.create_book.side_effect = Exception("Test error")
        agent.autogen_service = mock_autogen_service

        # Act
        result = await agent.run_autogen_workflow()

        # Assert
        assert result is False

    def test_initialize_project_with_data(self):
        """Test initializing project with data."""
        # Arrange
        settings = Settings()
        agent = ProjectManagerAgent(settings=settings)
        project_kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")

        with patch.object(Path, "mkdir") as mock_mkdir:
            with patch.object(agent, "save_project_data") as mock_save:
                # Act
                agent.initialize_project_with_data(project_kb)

                # Assert
                assert agent.project_knowledge_base == project_kb
                mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
                mock_save.assert_called_once()

    def test_agents_access(self):
        """Test accessing agents dictionary."""
        # Arrange
        settings = Settings()
        agent = ProjectManagerAgent(settings=settings)
        mock_agent = MagicMock()
        agent.agents = {"test_agent": mock_agent}

        # Act & Assert
        assert "test_agent" in agent.agents
        assert agent.agents["test_agent"] == mock_agent
        assert "nonexistent_agent" not in agent.agents

    @patch("libriscribe2.agents.project_manager.ProjectKnowledgeBase.load_from_file")
    def test_load_project_data_with_existing_project_dir(self, mock_load):
        """Test loading project data when project_dir is already set."""
        # Arrange
        settings = Settings()
        agent = ProjectManagerAgent(settings=settings)
        project_kb = ProjectKnowledgeBase(project_name="test_project", title="Test Book")
        mock_load.return_value = project_kb

        # Set existing project_dir
        agent.project_dir = Path("/old/path")

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create project directory and data file
            project_dir = Path(temp_dir) / "test_project"
            project_dir.mkdir(parents=True, exist_ok=True)
            project_data_file = project_dir / "project_data.json"
            project_data_file.write_text('{"project_name": "test_project"}')
            settings.projects_dir = temp_dir

            # Act
            agent.load_project_data("test_project")

            # Assert - project_dir should be updated to new path
            assert agent.project_dir == project_dir
            assert agent.project_knowledge_base is not None
            assert agent.project_knowledge_base == project_kb
            assert agent.project_knowledge_base.project_dir == project_dir

    @patch("libriscribe2.agents.project_manager.ProjectKnowledgeBase.load_from_file")
    def test_load_project_data_preserves_file_not_found_error(self, mock_load):
        """Test that FileNotFoundError from load_from_file is preserved."""
        # Arrange
        settings = Settings()
        agent = ProjectManagerAgent(settings=settings)
        mock_load.side_effect = FileNotFoundError("File not found")

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create project directory and data file
            project_dir = Path(temp_dir) / "test_project"
            project_dir.mkdir(parents=True, exist_ok=True)
            project_data_file = project_dir / "project_data.json"
            project_data_file.write_text('{"project_name": "test_project"}')
            settings.projects_dir = temp_dir

            # Act & Assert - FileNotFoundError should be re-raised as-is
            with pytest.raises(FileNotFoundError, match="File not found"):
                agent.load_project_data("test_project")

    @patch("libriscribe2.agents.project_manager.ProjectKnowledgeBase.load_from_file")
    def test_load_project_data_preserves_value_error(self, mock_load):
        """Test that ValueError from load_from_file is preserved."""
        # Arrange
        settings = Settings()
        agent = ProjectManagerAgent(settings=settings)
        mock_load.side_effect = ValueError("Invalid data")

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create project directory and data file
            project_dir = Path(temp_dir) / "test_project"
            project_dir.mkdir(parents=True, exist_ok=True)
            project_data_file = project_dir / "project_data.json"
            project_data_file.write_text('{"project_name": "test_project"}')
            settings.projects_dir = temp_dir

            # Act & Assert - ValueError should be re-raised as-is
            with pytest.raises(ValueError, match="Invalid data"):
                agent.load_project_data("test_project")

    def test_load_project_data_integration_with_settings(self):
        """Test that load_project_data correctly uses settings.projects_dir."""
        # Arrange
        settings = Settings()
        agent = ProjectManagerAgent(settings=settings)

        with tempfile.TemporaryDirectory() as temp_dir:
            # Set custom projects directory
            custom_projects_dir = Path(temp_dir) / "custom_projects"
            custom_projects_dir.mkdir(parents=True, exist_ok=True)
            settings.projects_dir = str(custom_projects_dir)

            # Create project directory in custom location
            project_dir = custom_projects_dir / "test_project"
            project_dir.mkdir(parents=True, exist_ok=True)

            # Act & Assert - should look in custom projects directory
            with pytest.raises(FileNotFoundError, match="Project data file not found"):
                agent.load_project_data("test_project")

            # Verify it's looking in the right place
            expected_path = custom_projects_dir / "test_project" / "project_data.json"
            assert not expected_path.exists()  # Confirms it's looking in the right place
