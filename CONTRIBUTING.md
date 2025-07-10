# Contributing to LibriScribe

We welcome contributions from the community!  Here's how you can help improve LibriScribe:

## Ways to Contribute

*   **Bug Reports:**  If you find a bug, please open an issue on GitHub, providing a detailed description of the problem, steps to reproduce it, and your operating system/environment.
*   **Feature Requests:**  If you have an idea for a new feature or improvement, open an issue and describe your suggestion.
*   **Code Contributions:**  We welcome pull requests for bug fixes, new features, and improvements to existing code.  Please follow the guidelines below.
*   **Documentation Improvements:**  Help us improve the documentation by fixing typos, clarifying explanations, or adding new content.
*   **Testing:**  Help us test the software and report any issues you encounter.

## Code Contribution Guidelines
1.  **Set up your environment:**
    *   Fork the repository and clone it locally.
    *   It's highly recommended to use a Python virtual environment.
      ```bash
      # Navigate to the project root
      cd libriscribe
      # Create a virtual environment
      python3 -m venv .venv
      # Activate it
      source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
      ```
    *   Install the project in editable mode along with development tools.
      ```bash
      # Install project dependencies
      pip install -e .
      # Install development tools
      pip install ruff
      ```
    *   If you plan to work with `.tex` files, you will need a TeX distribution like TeX Live. You can install `latexindent` using its package manager:
      ```bash
      tlmgr install latexindent
      ```
2.  **Create a branch:** Create a new branch for your changes:
    ```bash
    git checkout -b my-feature-branch
    ```
    Use a descriptive branch name (e.g., `fix-bug-123`, `add-new-agent`).
3.  **Make your changes:**  Write your code, following the project's code style.
4.  **Format your code:** Before committing, please run the formatters.
    ```bash
    # Format Python files
    ruff format .

    # Check for Python linting issues and auto-fix
    ruff check --fix .

    # Format a .tex file (run on each one you change)
    latexindent.pl path/to/your/file.tex
    ```
5.  **Write tests:**  If you're adding a new feature or fixing a bug, write unit tests to ensure your code works correctly.
6.  **Run tests:**  Make sure all tests pass before submitting your pull request.
7.  **Commit your changes:**
    ```bash
    git commit -m "A descriptive commit message"
    ```
8.  **Push your branch:**
    ```bash
    git push origin my-feature-branch
    ```
9.  **Create a pull request:**  Create a pull request from your branch to the `main` branch of the LibriScribe repository. Provide a clear description of your changes and any relevant information.
10. **Address feedback:** Be prepared to address feedback provided.

## Code Style

*   We use Ruff for Python and `latexindent.pl` for LaTeX to ensure consistent code style.
*   Configuration is in `pyproject.toml` for Ruff and `.latexindent.yaml` for LaTeX. Please adhere to these styles.
*   Use clear and descriptive variable and function names.
*   Add docstrings to your functions and classes.
*   Keep your code well-organized and easy to understand.

## Reporting Issues

When reporting issues, please include:

*   A clear and concise title.
*   A detailed description of the issue.
*   Steps to reproduce the issue (if applicable).
*   Expected behavior.
*   Actual behavior.
*   Your operating system and Python version.
*   Any relevant error messages or screenshots.

Thank you for contributing to LibriScribe!