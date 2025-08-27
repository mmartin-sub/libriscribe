# Installation for Developers

This section is for developers who want to contribute to LibriScribe2.

### 1. Prerequisites

- **Python:** 3.12 or higher
- **Git:** Required for cloning the repository

### 2. Set Up the Development Environment

```bash
# Clone the repository
git clone https://github.com/guerra2fernando/libriscribe2.git
cd libriscribe2

# Install hatch
pip install hatch

# Create the development environment and install all dependencies
hatch env create
uv sync --extra all
```

### 3. Verify Development Setup

Run the test suite to ensure everything is set up correctly:

```bash
hatch run test
```

### 4. Development Workflow

- **Run tests:** `hatch run test`
- **Check code style:** `hatch run lint:style`
- **Run linting:** `hatch run lint:lint`
- **Run type checking:** `hatch run lint:typing`
- **Auto-format code:** `hatch run format`

### 5. Pre-commit Hooks (Optional but Recommended)

```bash
# Install pre-commit
uv pip install pre-commit

# Install the hooks
pre-commit install
```
