---
sidebar_position: 3
---

# Usage Guide

This guide explains how to use libriscribe2.

## Running LibriScribe2

After installation, simply run:

```bash
libriscribe start
```

This will start the LibriScribe2 CLI.

## Simple vs. Advanced Mode

LibriScribe2 offers two modes:

- **Simple Mode**: This mode guides you through a streamlined process with fewer prompts, making it ideal for quickly generating a basic draft. You'll be asked for essential information (genre, description, etc.), and LibriScribe2 will handle most of the agent interactions automatically.
- **Advanced Mode**: This mode gives you full control over each step of the book creation process. You'll be able to interact with each agent individually, providing custom parameters and reviewing the output at each stage. This is recommended for users who want fine-grained control and are comfortable working with the CLI.

The CLI will ask you to choose a mode at the beginning.

## Step-by-Step (Simple Mode)

If you choose **Simple Mode**, the CLI will guide you through these steps (with fewer individual commands than Advanced Mode):

1. **Project Initialization**: You'll provide basic information about your book.
2. **Concept Generation**: LibriScribe2 will help refine your initial idea.
3. **Outline Generation**: An outline will be created automatically.
4. **Character Generation**: Characters will be created.
5. **Worldbuilding (if applicable)**: World details will be generated.
6. **Chapter Writing**: LibriScribe2 will write all chapters based on the generated outline, characters, and worldbuilding.
7. **Formatting**: You'll be prompted for an output format (Markdown or PDF).

## Step-by-Step (Advanced Mode)

Advanced Mode gives you granular control. Here's a breakdown of the commands you'll use (similar to the original README, but initiated through the `libriscribe` command and interactive prompts):

- `create`: Initialize a new project (you will still be prompted for project details).
- `concept`: Generate a detailed book concept.
- `outline`: Generate a book outline.
- `characters`: Generate character profiles.
- `worldbuilding`: Generate worldbuilding details.
- `write-chapter`: Write a specific chapter (you'll be prompted for the chapter number).
- `edit-chapter`: Edit a specific chapter.
- `style-edit`: Refine the writing style of a chapter.
- `fact-check`: Check factual claims in a chapter (primarily for non-fiction).
- `plagiarism-check`: Check for potential plagiarism.
- `review-chapter`: Review a chapter.
- `research`: Conduct web research on a topic.
- `format`: Format the book into Markdown or PDF.

In **Advanced Mode**, you'll run these commands interactively through the main `libriscribe` command, and you'll be prompted for any necessary arguments (like chapter numbers, file paths, etc.).

## Non-Interactive Commands

LibriScribe2 also provides non-interactive commands for scripting and automation.

### `create-book`

The `create-book` command allows you to create a book with a single command.

**--skip-error**

By default, the `create-book` command will exit if it encounters an error (e.g., a file cannot be written). You can use the `--skip-error` flag to force the command to continue even if an error occurs.

Example:
```bash
libriscribe2 create-book --title "My Book" --all --skip-error
```
