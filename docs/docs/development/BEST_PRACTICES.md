# Best Practices

This document outlines best practices for development in the LibriScribe2 project.

## Git Commit Messages

We follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification for our commit messages. This provides a clear and consistent commit history, and allows us to automate a lot of our release process.

Each commit message consists of a **header**, a **body** and a **footer**.

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Type

The type must be one of the following:

-   **feat**: A new feature
-   **fix**: A bug fix
-   **docs**: Documentation only changes
-   **style**: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
-   **refactor**: A code change that neither fixes a bug nor adds a feature
-   **perf**: A code change that improves performance
-   **test**: Adding missing tests or correcting existing tests
-   **build**: Changes that affect the build system or external dependencies (example scopes: gulp, broccoli, npm)
-   **ci**: Changes to our CI configuration files and scripts (example scopes: Travis, Circle, BrowserStack, SauceLabs)
-   **chore**: Other changes that don't modify src or test files
-   **revert**: Reverts a previous commit

### Scope

The scope is an optional part of the commit message that provides additional contextual information.

### Description

The description contains a succinct description of the change.

### Body

The body is an optional part of the commit message that provides additional contextual information about the code changes.

### Footer

The footer is an optional part of the commit message that is used to reference tracking-tool IDs (such as Jira or GitHub issues).

## GitHub Workflows

-   **Branching Strategy:** We use a `main` branch for production-ready code, and feature branches for development. All feature branches should be created from the `main` branch.
-   **Pull Requests:** All changes to the `main` branch must be made through a pull request. All pull requests must be reviewed and approved by at least one other developer before being merged.
-   **Code Reviews:** All code reviews should be constructive and focus on improving the quality of the code.
-   **Branch Protection:** The `main` branch should be protected to prevent direct pushes and to require status checks to pass before merging.

## Pip Publishing

-   **Versioning:** We use [Semantic Versioning](https://semver.org/) for our releases.
-   **PyPI Publishing:** We use GitHub Actions to automatically publish the library to PyPI on every new release. The release process is triggered by creating a new release on GitHub.
-   **Changelog:** The changelog is automatically generated from the commit messages using the Conventional Commits specification.
