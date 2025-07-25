# LibriScribe 📚✨

<div align="center">

<img src="https://guerra2fernando.github.io/libriscribe/img/logo.png" alt="LibriScribe Logo" width="30%">

Your AI-Powered Book Writing Assistant


[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Documentation](https://img.shields.io/badge/docs-visit%20now-green.svg)](https://guerra2fernando.github.io/libriscribe/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Support-yellow.svg?style=flat&logo=buy-me-a-coffee)](https://buymeacoffee.com/guerra2fernando)

</div>

## 🌟 Overview

LibriScribe harnesses the power of AI to revolutionize your book writing journey. Using a sophisticated multi-agent system, where each agent specializes in specific tasks, LibriScribe assists you from initial concept to final manuscript.

![Libriscribe Demo](https://github.com/guerra2fernando/libriscribe/blob/main/docs/static/img/libriscribe.gif?raw=true)

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
- **Plagiarism Detection:** Ensure content originality
- **Research Assistant:** Access comprehensive topic research
- **Manuscript Formatting:** Export to polished Markdown or PDF

## 🚀 Quickstart

> 📖 **Need detailed installation instructions?** See our comprehensive [Installation Guide](docs/INSTALLATION.md)

### Prerequisites

LibriScribe uses modern Python tooling for development and dependency management. You'll need:

- **Python 3.9+**
- **uv** (fast Python package installer)
- **hatch** (modern Python project manager)

### 1. Install Required Tools

#### Install uv (Fast Python Package Manager)

```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Alternative: using pip
pip install uv
```

#### Install hatch (Python Project Manager)

```bash
# Using uv (recommended)
uv tool install hatch

# Alternative: using pip
pip install hatch
```

### 2. Project Installation

#### Quick Installation (End Users)

```bash
git clone https://github.com/guerra2fernando/libriscribe.git
cd libriscribe

# Install with uv (fastest)
uv pip install -e .

# Or install with pip
pip install -e .
```

#### Development Installation

For contributors and developers:

```bash
git clone https://github.com/guerra2fernando/libriscribe.git
cd libriscribe

# Install all development dependencies using hatch
hatch env create

# Or manually with uv
uv pip install -e ".[all]"
```

#### Font Dependencies (Optional)

For enhanced PDF generation:

```bash
# Ubuntu/Debian
sudo apt install fonts-firacode fonts-ebgaramond fonts-noto fonts-texgyre fonts-noto-color-emoji texlive-luatex texlive-lang-french
luaotfload-tool -f -u

# macOS
brew install font-fira-code font-eb-garamond

# Windows
# Download and install fonts manually from Google Fonts
```

### 2. Configuration

*   **LLM API Key:** Get an API key from one of the following services:

    - **OpenAI:** [Get API Key](https://platform.openai.com/signup/)
    - **Anthropic:** [Get API Key](https://console.anthropic.com/)
    - **DeepSeek:** [Get API Key](https://platform.deepseek.com/)
    - **Google AI Studio (Gemini):** [Get API Key](https://aistudio.google.com/)
    - **Mistral AI:** [Get API Key](https://console.mistral.ai/)

Create a `.env` file in the root directory and fill the api key of the LLM that you want to use:
```bash
OPENAI_API_KEY=your_api_key_here
```


### 3. Launch LibriScribe

#### Using the CLI Command

```bash
libriscribe start
```

#### Direct Python Execution

```bash
python src/libriscribe/main.py
```

#### Quick Commands

```bash
# Generate concept
libriscribe concept --project-name my_book

# Create characters
libriscribe characters --project-name my_book

# Build world
libriscribe worldbuilding --project-name my_book

# Write chapter
libriscribe write --project-name my_book --chapter-number 1

# Edit chapter
libriscribe edit --project-name my_book --chapter-number 1

# Resume project
libriscribe resume --project-name my_book
```

Choose between:
- 🎯 **Simple Mode:** Quick, streamlined book creation
- 🎛️ **Advanced Mode:** Fine-grained control over each step

## 🛠️ Development Workflow

LibriScribe uses **hatch** for modern Python project management. Here are the key commands:

### Environment Management

```bash
# Create development environment
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

## 💻 Advanced Usage

### Project Creation
```bash
python src/libriscribe/main.py start \
    --project-name my_book \
    --title "My Awesome Book" \
    --genre fantasy \
    --description "A tale of epic proportions." \
    --category fiction \
    --num-characters 3 \
    --worldbuilding-needed True
```

### Core Commands

```bash
# Generate book concept
libriscribe concept --project-name my_book

# Create outline
libriscribe outline --project-name my_book

# Generate characters
libriscribe characters --project-name my_book

# Build world
libriscribe worldbuilding --project-name my_book

# Write chapter
libriscribe write-chapter --project-name my_book --chapter-number 1

# Edit chapter
libriscribe edit-chapter --project-name my_book --chapter-number 1

# Format book
libriscribe format --project-name my_book

# Validate project
libriscribe validate --project-name my_book
```

### Alternative: Direct Python Execution

```bash
# If you prefer using Python directly
python -m libriscribe.main concept --project-name my_book
python -m libriscribe.main outline --project-name my_book
# ... etc
```

## 📁 Project Structure

```
your_project/
├── project_data.json    # Project metadata
├── outline.md          # Book outline
├── characters.json     # Character profiles
├── world.json         # Worldbuilding details
├── chapter_1.md       # Generated chapters
├── chapter_2.md
└── research_results.md # Research findings
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
uv python install 3.11
uv venv --python 3.11
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

## ⚠️ Important Notes

- **API Costs:** Monitor your LLM API usage and spending limits
- **Content Quality:** Generated content serves as a starting point, not final copy
- **Review Process:** Always review and edit the AI-generated content
- **Python Version:** Requires Python 3.9 or higher
- **Dependencies:** Some features require additional system fonts for PDF generation


## 🔗 Quick Links

- [📚 Documentation](https://guerra2fernando.github.io/libriscribe/)
- [🚀 Installation Guide](docs/INSTALLATION.md)
- [🔍 Validation System](docs/validation_system.md)
- [⚙️ Validation Interfaces API](docs/validation_interfaces_api.md)
- [🧪 AI Mock System](docs/ai_mock_system.md)
- [✅ AI Testing Best Practices](docs/ai_testing_best_practices.md)
- [🐛 Issue Tracker](https://github.com/guerra2fernando/libriscribe/issues)
- [💡 Feature Requests](https://github.com/guerra2fernando/libriscribe/issues/new)
- [📖 Wiki](https://github.com/guerra2fernando/libriscribe/wiki)

## 🤝 Contributing

We welcome contributions! Check out our [Contributing Guidelines](CONTRIBUTING.md) to get started.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🗺️ LibriScribe Development Roadmap

### 🤖 LLM Integration & Support
- [X] **Multi-LLM Support Implementation**: Anthropic Claude Models - Google Gemini Models - - Deepseek Models - Mistral Models
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

[⭐ Star us on GitHub](https://github.com/guerra2fernando/libriscribe)

If LibriScribe has been helpful for your projects, consider buying me a coffee:

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Support-yellow.svg?style=flat&logo=buy-me-a-coffee)](https://buymeacoffee.com/guerra2fernando)

</div>
