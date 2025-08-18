# Python Version Management

This document explains how to properly set up Python 3.12+ for this project and avoid common issues with pre-commit and linting tools.

## 🎯 Requirements

- Python 3.12 or higher
- uv (for dependency management)
- hatch (for project management)

## 🚀 Quick Setup

### 1. Install Python 3.12

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.12 python3.12-venv python3.12-pip
```

**macOS:**
```bash
brew install python@3.12
```

**Windows:**
Download from [python.org](https://www.python.org/downloads/)

### 2. Verify Python Installation

```bash
python3.12 --version
# Should output: Python 3.12.x
```

### 3. Set Up Project Environment

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create and activate virtual environment
uv venv
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows

# Install dependencies
uv pip install -e .
```

## 🔧 Linting and Code Quality

### Using Hatch Scripts (Recommended)

The project includes comprehensive linting scripts that work with the correct Python version:

```bash
# Check Python version first
hatch run check-python

# Run all linting checks
hatch run lint-all

# Fix formatting issues
hatch run lint-fix

# Run security checks
hatch run security

# Check for dead code
hatch run dead-code
```

### Using Pre-commit (Alternative)

If you prefer pre-commit hooks:

```bash
# Install pre-commit with Python 3.12
python3.12 -m pip install pre-commit

# Install the git hooks
pre-commit install

# Run on all files
pre-commit run --all-files
```

## 🚨 Common Issues and Solutions

### Issue: Pre-commit uses wrong Python version

**Symptoms:**
- Virtualenv creation errors
- Python 3.8 being used instead of 3.12

**Solutions:**
1. **Use hatch scripts instead** (recommended)
2. **Install pre-commit with Python 3.12:**
   ```bash
   python3.12 -m pip install pre-commit
   ```
3. **Set PYTHONPATH environment variable:**
   ```bash
   export PYTHONPATH=$(which python3.12)
   ```

### Issue: Virtualenv compatibility errors

**Symptoms:**
- `TypeError: canonicalize_version() got an unexpected keyword argument`
- Virtualenv creation fails

**Solutions:**
1. **Use the project's virtual environment:**
   ```bash
   source .venv/bin/activate
   pre-commit run --all-files
   ```
2. **Use hatch scripts** (they handle this automatically)

### Issue: Different Python versions on different systems

**Solution:** The `scripts/ensure_python_version.py` script automatically detects and uses the best available Python version.

## 📋 Best Practices

### ✅ Do's

- Use `hatch run` commands for consistent environment
- Run `hatch run check-python` before linting
- Keep Python 3.12+ as the minimum requirement
- Use uv for dependency management

### ❌ Don'ts

- Don't hardcode Python paths in configuration files
- Don't rely on system Python for development
- Don't use Python versions below 3.12
- Don't mix different Python version managers

## 🔄 Migration Guide

If you're coming from a different setup:

1. **Remove old virtual environments:**
   ```bash
   rm -rf venv/ .venv/ env/
   ```

2. **Install Python 3.12+**

3. **Set up with uv:**
   ```bash
   uv venv
   uv pip install -e .
   ```

4. **Test the setup:**
   ```bash
   hatch run check-python
   hatch run lint-all
   ```

## 🛠️ Troubleshooting

### Check Available Python Versions

```bash
python scripts/ensure_python_version.py
```

### Manual Python Version Check

```bash
python3.12 --version
python3.11 --version
python3.10 --version
python3 --version
```

### Reset Pre-commit Cache

```bash
pre-commit clean
rm -rf ~/.cache/pre-commit
```

### Verify Hatch Environment

```bash
hatch env show
```

## 📚 Additional Resources

- [Python 3.12 Documentation](https://docs.python.org/3.12/)
- [uv Documentation](https://docs.astral.sh/uv/)
- [hatch Documentation](https://hatch.pypa.io/)
- [Pre-commit Documentation](https://pre-commit.com/)
