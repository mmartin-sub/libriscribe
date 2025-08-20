# Installation for Users

This section is for users who want to install and use LibriScribe2.

### 1. Prerequisites

- **Operating System:** Linux, macOS, or Windows
- **Python:** 3.12 or higher

### 2. Install Core Tools

You will need `uv` and `hatch` to install and run LibriScribe2.

### Install uv (Python Package Manager)

```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Install hatch (Project Manager)

```bash
# Recommended
uv tool install hatch
```

### 3. Install LibriScribe2

```bash
# Clone the repository
git clone https://github.com/guerra2fernando/libriscribe2.git
cd libriscribe2

# Install the application
uv pip install -e .
```

### 4. Configuration

Create a `.env` file in the project root for your API keys:

```bash
# Example .env file
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
# Add other keys as needed
```

### 5. Verify Installation

```bash
libriscribe2 --help
```

---

## Optional: Font Dependencies

For enhanced PDF generation capabilities, you may need to install additional fonts.

### Ubuntu/Debian

```bash
sudo apt update
sudo apt install fonts-firacode fonts-ebgaramond fonts-noto fonts-texgyre fonts-noto-color-emoji texlive-luatex texlive-lang-french
luaotfload-tool -f -u
```

### macOS (using Homebrew)

```bash
brew install font-fira-code font-eb-garamond
```

### Windows

Download and install fonts manually from [Google Fonts](https://fonts.google.com/) or [Font Squirrel](https://www.fontsquirrel.com/).

---

## Troubleshooting

If you encounter issues, refer to the [Troubleshooting Guide](../../README.md#troubleshooting) in the main README.
