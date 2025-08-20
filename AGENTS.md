# Instructions for Jules - Google Agent

To set up the development environment for this project, please follow these steps:

1. **Install Hatch:**
    Hatch is used for project management.

    ```bash
    pip install hatch
    ```

2. **Create Environment and Install Dependencies:**
    This command creates a virtual environment and installs all the required dependencies, including those for development and testing.

    ```bash
    hatch env create
    uv sync --extra all
    ```

3. **Running Tests:**
    To run the test suite, use the following command:

    ```bash
    hatch run pytest
    ```

4. **Code Quality and Linting:**
    This project uses `pre-commit` to enforce code quality. To run all the checks on all files, use:

    ```bash
    hatch run pre-commit run --all-files
    ```

    It is recommended to install the `pre-commit` hooks to run the checks automatically before each commit:

    ```bash
    hatch run pre-commit install
    ```

This will ensure that you have all the necessary dependencies and that your code adheres to the project's quality standards.
