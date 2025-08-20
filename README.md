# LibriScribe2 📚✨

<div align="center">

<img src="https://guerra2fernando.github.io/libriscribe2/img/logo.png" alt="LibriScribe2 Logo" width="30%">

Your AI-Powered Book Writing Assistant

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Documentation](https://img.shields.io/badge/docs-visit%20now-green.svg)](https://guerra2fernando.github.io/libriscribe2/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/downloads/)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Support-yellow.svg?style=flat&logo=buy-me-a-coffee)](https://buymeacoffee.com/guerra2fernando)

</div>

## 🌟 Overview

**LibriScribe2** is a modern, enhanced version of the original LibriScribe project. This project builds upon Fernando Guerra's foundational work with significant architectural improvements, enhanced capabilities, and a redesigned interface. LibriScribe2 harnesses the power of AI to revolutionize your book writing journey using a sophisticated multi-agent system, where each agent specializes in specific tasks, assisting you from initial concept to final manuscript.

> **Note**: This project is distinct from the original LibriScribe project. Fernando Guerra maintains control over the original project's release and development. LibriScribe2 represents a significant evolution with new capabilities and interfaces.

![Libriscribe2 Demo](https://github.com/guerra2fernando/libriscribe2/blob/main/docs/static/img/libriscribe2.gif?raw=true)

## ✨ Features

### Creative Assistance 🎨

- **Concept Generation:** Transform your ideas into detailed book concepts
- **Automated Outlining:** Create comprehensive chapter-by-chapter outlines
- **Character Generation:** Develop rich, multidimensional character profiles
- **Worldbuilding:** Craft detailed universes with rich history, culture, and geography

### Writing & Editing 📝

- **Chapter Writing:** Generate chapter drafts based on your outline
- **Content Review:** Catch inconsistencies and plot holes
- **Style Editing:** Polish your writing style for your target audience
- **Fact-Checking:** Verify factual claims (for non-fiction)

### Quality Assurance 🔍

- **Comprehensive Validation System:** Multi-stage content and code validation
- **AI Mock Testing:** Test validation components without consuming AI resources
- **Validation Utilities:** Resource management, health monitoring, and usage tracking
- **Plagiarism Detection:** Ensure content originality
- **Research Assistant:** Access comprehensive topic research
- **Manuscript Formatting:** Export to polished Markdown or PDF

### Technical Standards 🏗️

- **ISO 8601-2:2019 UTC Timestamps:** Consistent, international timestamp format for all data
- **Standardized Data Storage:** Uniform JSON structure with proper timezone handling
- **Performance Monitoring:** High-precision timing for optimization and debugging
- **Cross-Platform Compatibility:** Consistent behavior across different operating systems
- **Python 3.12 Optimizations:** Enhanced performance with slots, improved async operations, and memory efficiency

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.12+**
- **uv** (a fast Python package installer)
- **hatch** (a modern Python project manager)

### Installation

We provide separate installation guides for users and developers:

- **[Installation Guide for Users](docs/user-guide/installation.md)**
- **[Installation Guide for Developers](docs/development/installation.md)**

### Configuration

For detailed configuration options, see our [Configuration Guide](docs/user-guide/configuration.md) for model selection, advanced settings, and customization options.

### 3. Launch LibriScribe2

#### Using the CLI Command

```bash
hatch run python -m libriscribe2.main --help
```

#### Quick Commands

```bash
# Create a complete book with all steps
hatch run python -m libriscribe2.main create-book --title="My Book" --all

# Create with custom project name
hatch run python -m libriscribe2.main create-book --title="My Book" --project-name=my-custom-project --all

# Create with character range
hatch run python -m libriscribe2.main create-book --title="My Book" --characters=3-7 --generate-characters

# Create with custom configuration
hatch run python -m libriscribe2.main create-book --title="My Book" --config-file=config-example.json --all

# View book statistics
hatch run python -m libriscribe2.main book-stats --project-name my_book
```

Choose between:

- 🟢 **NON-INTERACTIVE (RECOMMENDED):** Well-maintained commands with full functionality
- 🟡 **INTERACTIVE (ADVANCED):** Not fully supported, may have limited functionality

## ⚙️ Configuration

Before using LibriScribe, set up your configuration:

```bash
# Copy the example configuration file
cp config-example.json config.json

# Edit config.json with your API keys and preferences
# See docs/user-guide/configuration.md for details
```

## 🛠️ Development Workflow

LibriScribe2 uses **hatch** for modern Python project management. Here are the key commands:

### Environment Management

```bash
# Create development environment
hatch env remove # only required if there is an existing one.
pip install --upgrade hatch packaging
hatch env create

# Show available environments
hatch env show

# Remove environment
hatch env remove default
```

### Testing

```bash
# Run tests
hatch run test

# Run tests with coverage
hatch run test-cov

# Run specific test file
hatch run test tests/test_validation_engine.py
```

### Code Quality

```bash
# Check code style
hatch run lint:style

# Run linting
hatch run lint:lint

# Run type checking
hatch run lint:typing

# Auto-format code
hatch run black .

# Auto-fix linting issues
hatch run ruff check --fix .
```

### Building and Publishing

```bash
# Build the package
hatch build

# Publish to PyPI (maintainers only)
hatch publish
```

### Alternative: Using uv directly

If you prefer using uv directly:

```bash
# Install dependencies
uv pip install -e ".[all]"

# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=term-missing
```

## 🔐 Security and Secrets Management

### Adding New Test Secrets

When adding new test secrets or handling false positives with detect-secrets, follow these steps:

1. **Scan for secrets in the codebase:**

   ```bash
   hatch run detect-secrets-scan
   ```

2. **Audit the detected secrets to identify false positives:**

   ```bash
   hatch run detect-secrets-audit
   ```

3. **Commit the updated baseline file:**

   ```bash
   git add .secrets.baseline
   git commit -m "Update secrets baseline"
   ```

### For Developers: Adding New Test Secrets

If you're a developer adding new test secrets to avoid false positives, follow these steps:

1. **Run the baseline scan:**

   ```bash
   detect-secrets scan --baseline .secrets.baseline
   ```

2. **Audit and mark false positives:**

   ```bash
   detect-secrets audit .secrets.baseline
   ```

   - This opens an interactive session where you can mark legitimate test data as false positives
   - Use `a` to accept (mark as false positive)
   - Use `r` to reject (keep as potential secret)
   - Use `q` to quit

3. **Commit the updated baseline:**

   ```bash
   git add .secrets.baseline
   git commit -m "Update secrets baseline with new test data"
   ```

### Best Practices

- **False Positives**: Use the audit command to mark legitimate test data as false positives
- **Real Secrets**: Never commit actual API keys or sensitive credentials
- **Test Data**: Use clearly marked test data (e.g., `test_api_key_12345`) for testing
- **Baseline Updates**: Always update the baseline file when adding new test secrets

### Detect-Secrets Configuration

The project uses detect-secrets to scan for potential security issues. The baseline file (`.secrets.baseline`) contains:

- Known false positives
- Test data that should be ignored
- Configuration for different secret types

## 💻 Advanced Usage

### Current CLI Commands

The main commands available are:

**🟢 NON-INTERACTIVE (RECOMMENDED):**

- `create-book` - Create books with command-line arguments
- `book-stats` - View book statistics
- `format` - Format existing books

**🟡 INTERACTIVE (ADVANCED):**

- `start` - Interactive book creation (not implemented)
- `concept` - Generate concept for existing project (not implemented)
- `outline` - Generate outline for existing project (not implemented)
- `characters` - Generate characters for existing project (not implemented)
- `worldbuilding` - Generate worldbuilding for existing project (not implemented)
- `write` - Write specific chapter (not implemented)
- `edit` - Edit specific chapter (not implemented)
- `research` - Research functionality (not implemented)
- `resume` - Resume existing project (not implemented)

### Project Creation

```bash
# Create a complete book with all steps
hatch run python -m libriscribe2.main create-book \
    --title="My Awesome Book" \
    --genre=fantasy \
    --description="A tale of epic proportions." \
    --category=fiction \
    --characters=3 \
    --worldbuilding \
    --all

# Create with custom project name
hatch run python -m libriscribe2.main create-book \
    --title="My Awesome Book" \
    --project-name=my-custom-project \
    --genre=fantasy \
    --characters=3 \
    --worldbuilding \
    --all

# Create with character range
hatch run python -m libriscribe2.main create-book \
    --title="My Awesome Book" \
    --genre=fantasy \
    --characters=3-7 \
    --generate-characters

### Key create-book Options

**Required:**
- `--title` - Book title (required)

**Book Details:**
- `--project-name` - Custom project folder name (spaces allowed)
- `--category` - Book category [default: Fiction]
- `--genre` - Book genre (e.g., fantasy, mystery, romance)
- `--description` - Book description or synopsis
- `--language` - Book language [default: English]
- `--chapters` - Number of chapters to generate
- `--characters` - Number of characters to create (e.g., 5, 3-7, 5+)
- `--worldbuilding` - Enable worldbuilding for the book

**Configuration:**
- `--config-file` - Path to configuration file (.env, .yaml, .yml, or .json)
- `--mock` - Use mock LLM provider for testing

**Generation Steps:**
- `--generate-concept` - Generate book concept
- `--generate-outline` - Generate book outline
- `--generate-characters` - Generate character profiles
- `--generate-worldbuilding` - Generate worldbuilding details (requires --worldbuilding)
- `--write-chapters` - Write all chapters
- `--format-book` - Format the book into final output
- `--all` - Perform all generation steps

### Core Commands

```bash
# Create a complete book (RECOMMENDED)
hatch run python -m libriscribe2.main create-book --title "My Book" --all

# Create with specific steps
hatch run python -m libriscribe2.main create-book \
    --title "My Book" \
    --generate-concept \
    --generate-outline \
    --generate-characters \
    --generate-worldbuilding \
    --write-chapters \
    --format-book

# View book statistics (non-interactive)
hatch run python -m libriscribe2.main book-stats --project-name my_book

# View book statistics with recent log entries
hatch run python -m libriscribe2.main book-stats --project-name my_book --show-logs

# Format existing book
hatch run python -m libriscribe2.main format --project-name my_book

# Resume or continue existing project
hatch run python -m libriscribe2.main resume --project-name my_book
```

### Alternative: Direct Python Execution

```bash
# If you prefer using Python directly
python -m libriscribe2.main create-book --title "My Book" --all
python -m libriscribe2.main book-stats --project-name my_book
python -m libriscribe2.main book-stats --project-name my_book --show-logs
# ... etc
```

## 📁 Project Structure

```
projects/
└── your-project-name/
    ├── project_data.json    # Project metadata
    ├── outline.md          # Book outline
    ├── characters.md       # Character profiles
    ├── worldbuilding.md    # Worldbuilding details
    ├── chapter_1.md       # Generated chapters
    ├── chapter_2.md
    ├── manuscript.md       # Final formatted book
    └── book_creation.log  # Creation process logs
```

## 🔧 Troubleshooting

### Installation Issues

#### uv not found

```bash
# Make sure uv is in your PATH
echo $PATH

# Restart your terminal or source your shell profile
source ~/.bashrc  # or ~/.zshrc
```

#### hatch not found

```bash
# Install hatch globally
uv tool install hatch

# Or add to PATH if installed locally
export PATH="$HOME/.local/bin:$PATH"
```

#### Python version issues

```bash
# Check Python version
python --version

# Use specific Python version with uv
uv python install 3.12
uv venv --python 3.12
```

#### Permission errors

```bash
# On Linux/macOS, you might need to make scripts executable
chmod +x ~/.local/bin/hatch
chmod +x ~/.local/bin/uv
```

### Development Issues

#### Tests failing

```bash
# Clean environment and reinstall
hatch env remove default
hatch env create
hatch run test
```

#### Import errors

```bash
# Make sure you're in the project root and installed in editable mode
pip install -e .
# or
uv pip install -e .
```

#### Timestamp Standards

LibriScribe2 uses **ISO 8601-2:2019 UTC** as the standard timestamp format for all data storage and API responses. This ensures consistency, international compatibility, and proper timezone handling.

**Key Benefits:**

- **Consistency**: Uniform timestamp format across all components
- **Internationalization**: UTC timezone eliminates local timezone confusion
- **Standards Compliance**: Follows international ISO 8601 standard
- **Debugging**: Human-readable timestamps for easier troubleshooting

**Usage:**

```python
from libriscribe2.utils.timestamp_utils import get_iso8601_utc_timestamp

# Generate ISO 8601-2:2019 UTC timestamp
timestamp = get_iso8601_utc_timestamp()
# Returns: "2024-01-15T10:30:45.123456Z"
```

For detailed information, see [Timestamp Standards Documentation](docs/development/timestamp-standards.md).

## ⚠️ Important Notes

- **API Costs:** Monitor your LLM API usage and spending limits
- **Content Quality:** Generated content serves as a starting point, not final copy
- **Review Process:** Always review and edit the AI-generated content
- **Python Version:** Requires Python 3.12 or higher
- **Dependencies:** Some features require additional system fonts for PDF generation

## 🔗 Quick Links

- [📚 Documentation](https://guerra2fernando.github.io/libriscribe2/)
- [🚀 Installation Guide for Users](docs/user-guide/installation.md)
- [🚀 Installation Guide for Developers](docs/development/installation.md)
- [⚙️ Configuration Guide](docs/user-guide/configuration.md)
- [🖥️ CLI API Documentation](docs/api/cli-api.md)
- [📝 CLI Function Signatures](docs/api/cli-signatures.md)
- [🔧 CLI Complete Function Signatures](docs/api/cli-function-signatures.md)
- [📋 CLI Comprehensive Documentation](docs/api/cli-comprehensive.md)
- [💻 CLI Usage Examples](examples/cli_usage_examples.md)
- [🔍 Validation System](docs/api/validation-system.md)
- [⚙️ Validation Interfaces API](docs/api/validation-interfaces-api.md)
- [🛠️ Validation Utils API](docs/api/validation-utils-api.md)
- [🤖 LLM Client API](docs/api/llm-client-api.md)
- [🎭 Mock LLM Client API](docs/api/mock-llm-client-api.md)
- [📝 LLM Client Signatures](docs/api/llm-client-signatures.md)
- [🧪 AI Mock System](docs/api/ai-mock-system.md)
- [⚡ Performance Improvements API](docs/api/performance-improvements-api.md)
- [📊 Performance Improvements Signatures](docs/api/performance-improvements-signatures.md)
- [✅ AI Testing Best Practices](docs/development/ai-testing-best-practices.md)
- [📋 ProjectManager API](docs/api/project-manager-api.md)
- [📝 ProjectManager Signatures](docs/api/project-manager-signatures.md)
- [📊 ProjectManager Summary](docs/api/project-manager-summary.md)
- [📈 Book Stats Command](docs/cli/book-stats-command.md)
- [🐛 Issue Tracker](https://github.com/guerra2fernando/libriscribe2/issues)
- [💡 Feature Requests](https://github.com/guerra2fernando/libriscribe2/issues/new)
- [📖 Wiki](https://github.com/guerra2fernando/libriscribe2/wiki)

## 🤝 Contributing

We welcome contributions! Check out our [Contributing Guidelines](CONTRIBUTING.md) to get started.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🗺️ LibriScribe2 Development Roadmap

### 🤖 LLM Integration & Support

- [X] **OpenAI Integration**: GPT-4o and GPT-4o-mini models fully supported
- [X] **Mock LLM Provider**: Comprehensive testing framework with deterministic responses
- [ ] **Multi-LLM Support**: Anthropic Claude Models, Google Gemini Models, Deepseek Models, Mistral Models
- [ ] **Model Performance Benchmarking**
- [ ] **Automatic Model Fallback System**
- [ ] **Custom Model Fine-tuning Support**
- [ ] **Cost Optimization Engine**
- [ ] **Response Quality Monitoring**

### 🔍 Vector Store & Search Enhancement

- [ ] **Multi-Vector Database Support**: ChromaDB Integration, MongoDB Vector Search, Pinecone Integration, Weaviate Implementation
- [ ] **Advanced Search Features**: Semantic Search, Hybrid Search (Keywords + Semantic), Cross-Reference Search, Contextual Query Understanding
- [ ] **Embedding Models Integration**: Multiple Embedding Model Support, Custom Embedding Training, Embedding Optimization

### 🔐 Authentication & Authorization

- [ ] **Cerbos Implementation**: Role-Based Access Control (RBAC), Attribute-Based Access Control (ABAC), Custom Policy Definitions, Policy Testing Framework
- [ ] **User Management System**: User Registration & Authentication, Social Auth Integration, Multi-Factor Authentication, Session Management
- [ ] **Security Features**: Audit Logging, Rate Limiting, API Key Management, Security Headers Implementation

### 🌐 API Development

- [ ] **Core API Features**: RESTful Endpoints, GraphQL Interface, WebSocket Support, API Documentation (OpenAPI/Swagger)
- [ ] **API Management**: Version Control, Rate Limiting, Usage Monitoring, Error Handling
- [ ] **Integration Features**: Webhook Support, Event System, Batch Processing, Export/Import Functionality

### 🎨 Frontend Application

- [ ] **Dashboard Development**: Modern React Interface, Real-time Updates, Progressive Web App Support, Responsive Design
- [ ] **Editor Features**: Rich Text Editor, Markdown Support, Real-time Collaboration, Version History
- [ ] **Visualization Tools**: Character Relationship Graphs, Plot Timeline Visualization, World Map Generation, Story Arc Visualization

<div align="center">

Made with ❤️ by Fernando Guerra and Lenxys

**LibriScribe2** builds upon Fernando Guerra's original LibriScribe project with significant enhancements and architectural improvements.

[⭐ Star us on GitHub](https://github.com/guerra2fernando/libriscribe2)

If LibriScribe2 has been helpful for your projects, consider buying me a coffee:

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Support-yellow.svg?style=flat&logo=buy-me-a-coffee)](https://buymeacoffee.com/guerra2fernando)

</div>
