# LibriScribe2 Installation Guide

This guide provides detailed installation instructions for LibriScribe2, including all prerequisites and development setup.

## Prerequisites

### System Requirements

- **Operating System:** Linux, macOS, or Windows
- **Python:** 3.12 or higher
- **Memory:** 4GB RAM minimum, 8GB recommended
- **Storage:** 1GB free space

### Required Tools

LibriScribe2 uses modern Python tooling for optimal development experience:

1. **uv** - Ultra-fast Python package installer and resolver
2. **hatch** - Modern Python project manager and build system

## Step-by-Step Installation

### 1. Install Python

Ensure you have Python 3.12 or higher:

```bash
# Check current version
python --version

# If you need to install Python:
# Ubuntu/Debian
sudo apt update && sudo apt install python3.12 python3.12-venv python3.12-pip

# macOS (using Homebrew)
brew install python@3.12

# Windows: Download from https://python.org
```

### 2. Install uv (Python Package Manager)

uv is a fast Python package installer that replaces pip:

#### Linux/macOS

```bash
# Recommended: Official installer
curl -LsSf https://astral.sh/uv/install.sh | sh

# Alternative: Using pip
pip install uv

# Alternative: Using Homebrew (macOS)
brew install uv
```

#### Windows

```bash
# PowerShell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Alternative: Using pip
pip install uv

# Alternative: Using Scoop
scoop install uv
```

#### Verify Installation

```bash
uv --version
```

### 3. Install hatch (Project Manager)

hatch provides modern Python project management:

```bash
# Using uv (recommended)
uv tool install hatch

# Alternative: Using pip
pip install hatch

# Alternative: Using pipx
pipx install hatch
```

#### Verify Installation

```bash
hatch --version
```

### 4. Clone and Install LibriScribe2

#### For End Users

```bash
# Clone the repository
git clone https://github.com/guerra2fernando/libriscribe2.git
cd libriscribe2

# Install using uv (fastest)
uv pip install -e .

# Alternative: Install using pip
pip install -e .

# Verify installation
libriscribe2 --help
```

#### For Developers

```bash
# Clone the repository
git clone https://github.com/guerra2fernando/libriscribe2.git
cd libriscribe2

# Create development environment with hatch
hatch env create

# Alternative: Install all dependencies manually
uv pip install -e ".[all]"

# Verify development setup
hatch run test
```

### 5. Optional: Font Dependencies

For enhanced PDF generation capabilities:

#### Ubuntu/Debian

```bash
sudo apt update
sudo apt install \
    fonts-firacode \
    fonts-ebgaramond \
    fonts-noto \
    fonts-texgyre \
    fonts-noto-color-emoji \
    texlive-luatex \
    texlive-lang-french

# Update font cache
luaotfload-tool -f -u
```

#### macOS

```bash
# Using Homebrew
brew install font-fira-code font-eb-garamond

# Or install manually from Google Fonts
```

#### Windows

Download and install fonts manually from:

- [Google Fonts](https://fonts.google.com/)
- [Font Squirrel](https://www.fontsquirrel.com/)

## Configuration

### 1. API Keys

Create a `.env` file in the project root:

```bash
# Choose one or more LLM providers
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GOOGLE_API_KEY=your_google_key_here
DEEPSEEK_API_KEY=your_deepseek_key_here
MISTRAL_API_KEY=your_mistral_key_here
```

### 2. Environment Variables

Optional configuration:

```bash
# Default project directory
LIBRISCRIBE2_PROJECT_DIR=/path/to/your/projects

# Default LLM provider
LIBRISCRIBE2_DEFAULT_LLM=openai

# Log level
LIBRISCRIBE2_LOG_LEVEL=INFO
```

## Development Setup

### Environment Management

```bash
# List available environments
hatch env show

# Create specific environment
hatch env create lint

# Remove environment
hatch env remove default

# Run commands in environment
hatch run test
hatch run lint:style
```

### Pre-commit Hooks (Optional)

For contributors:

```bash
# Install pre-commit
uv pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## Verification

### Test Installation

```bash
# Basic functionality test
libriscribe2 --version
libriscribe2 --help

# Run test suite (developers)
hatch run test

# Check code quality (developers)
hatch run lint:style
hatch run lint:lint
hatch run lint:typing
```

### Create Test Project

```bash
# Create a simple test project
libriscribe2 concept --project-name test_book

# Check if files were created
ls -la test_book/
```

## Troubleshooting

### Common Issues

#### 1. Command not found: uv

```bash
# Add to PATH (Linux/macOS)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Windows: Add to system PATH through System Properties
```

#### 2. Command not found: hatch

```bash
# Reinstall hatch
uv tool install hatch --force

# Check installation location
uv tool list
```

#### 3. Python version issues

```bash
# Install specific Python version with uv
uv python install 3.11

# Create venv with specific version
uv venv --python 3.11
```

#### 4. Permission errors

```bash
# Linux/macOS: Fix permissions
chmod +x ~/.local/bin/uv
chmod +x ~/.local/bin/hatch

# Windows: Run as administrator
```

#### 5. SSL/Certificate errors

```bash
# Update certificates
pip install --upgrade certifi

# Use trusted hosts (temporary fix)
uv pip install --trusted-host pypi.org --trusted-host pypi.python.org -e .
```

### Getting Help

If you encounter issues:

1. Check the [GitHub Issues](https://github.com/guerra2fernando/libriscribe2/issues)
2. Create a new issue with:
   - Your operating system
   - Python version (`python --version`)
   - uv version (`uv --version`)
   - hatch version (`hatch --version`)
   - Full error message

## Performance Tips

### Speed up installations

```bash
# Use uv for faster package installation
export UV_SYSTEM_PYTHON=1

# Use parallel builds
export MAKEFLAGS="-j$(nproc)"

# Cache dependencies
uv pip install --cache-dir ~/.cache/uv -e .
```

### Development workflow optimization

```bash
# Use hatch for isolated environments
hatch run test  # Faster than activating venv

# Use uv for dependency updates
uv pip compile requirements.in

# Use pre-commit for faster feedback
pre-commit run --files changed_file.py
```

## Next Steps

After successful installation:

1. Read the [User Guide](../README.md#quickstart)
2. Check out [Examples](../examples/)
3. Review [API Documentation](validation_interfaces_api.md)
4. Join our [Community](https://github.com/guerra2fernando/libriscribe2/discussions)

---

**Need help?** Open an issue on [GitHub](https://github.com/guerra2fernando/libriscribe2/issues) or check our [Documentation](https://guerra2fernando.github.io/libriscribe2/).
