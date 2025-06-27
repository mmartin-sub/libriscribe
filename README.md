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
- **Plagiarism Detection:** Ensure content originality
- **Research Assistant:** Access comprehensive topic research
- **Manuscript Formatting:** Export to polished Markdown or PDF

## 🚀 Quickstart

### 1. Installation

```bash
git clone ...
cd libriscribe
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements.txt
sudo apt install fonts-firacode fonts-ebgaramond
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
GOOGLE_AI_STUDIO_API_KEY=your_api_key_here
CLAUDE_API_KEY=your_api_key_here
DEEPSEEK_API_KEY=your_api_key_here
MISTRAL_API_KEY=your_api_key_here
```


### 3. Launch LibriScribe

```bash
source .venv/bin/activate
libriscribe start
```

```bash
source .venv/bin/activate
python src/libriscribe/main.py
concept --project-name my_book
characters --project-name my_book
worldbuilding  --project-name my_book
write --project-name my_book --chapter-number 1
edit --project-name my_book --chapter-number 1
Resume --project-name my_book
```

Choose between:
- 🎯 **Simple Mode:** Quick, streamlined book creation
- 🎛️ **Advanced Mode:** Fine-grained control over each step

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
python src/libriscribe/main.py concept

# Create outline
python src/libriscribe/main.py outline

# Generate characters
python src/libriscribe/main.py characters

# Build world
python src/libriscribe/main.py worldbuilding

# Write chapter
python src/libriscribe/main.py write-chapter --chapter-number 1

# Edit chapter
python src/libriscribe/main.py edit-chapter --chapter-number 1

# Format book
python src/libriscribe/main.py format
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

## ⚠️ Important Notes

- **API Costs:** Monitor your LLM API usage and spending limits
- **Content Quality:** Generated content serves as a starting point, not final copy
- **Review Process:** Always review and edit the AI-generated content


## 🔗 Quick Links

- [📚 Documentation](https://guerra2fernando.github.io/libriscribe/)
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
