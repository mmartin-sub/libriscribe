---
sidebar_position: 2
---

# Getting Started

This guide will walk you through the installation and setup of LibriScribe.

## Prerequisites

*   **Python 3.7 or later:** Check with `python --version` or `python3 --version`.
*   **pip:** Usually included with Python.
*   **OpenAI API Key:** Get one from [OpenAI website](https://platform.openai.com/).

## Installation Steps

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/guerra2fernando/libriscribe.git
    cd libriscribe
    ```

2.  **Install in editable mode:**

    ```bash
    pip install -e .
    ```
    This installs LibriScribe so that changes to the source code are reflected immediately.

3.  **Set up your OpenAI API Key:**
    *   Create a `.env` file in the *root* directory of the project.
    *   Add your key:

        ```
        OPENAI_API_KEY=your_openai_api_key_here
        ```
        Replace `your_openai_api_key_here`.  Make sure `.env` is in your `.gitignore`!

## Verifying the Installation

After installation, run:

```bash
libriscribe --help
```