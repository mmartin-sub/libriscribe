#!/bin/bash

# Function to upgrade dependencies in a specific section
upgrade_dependencies() {
    local section_title=$1
    local dependency_group=$2 # e.g., --group dev

    echo "Upgrading dependencies for: ${section_title}"

    # Extract the section name for parsing
    local section_name
    if [[ "$section_title" == "[project.dependencies]" ]]; then
        section_name="dependencies"
    else
        # Extract the group name from the section title
        section_name=$(echo "$section_title" | sed 's/\[project\.optional-dependencies\.\([^]]*\)\]/\1/')
    fi

    # Extract dependencies using grep and sed
    local start_line
    local end_line

    if [[ "$section_name" == "dependencies" ]]; then
        # Find the main dependencies section
        start_line=$(grep -n "^dependencies = \[" pyproject.toml | cut -d: -f1)
    else
        # Find the optional dependencies section
        start_line=$(grep -n "^${section_name} = \[" pyproject.toml | cut -d: -f1)
    fi

    if [[ -z "$start_line" ]]; then
        echo "No dependencies found for ${section_title}."
        return
    fi

    # Find the end of the list (next closing bracket)
    end_line=$(tail -n +$((start_line + 1)) pyproject.toml | grep -n "^\]" | head -1 | cut -d: -f1)
    end_line=$((start_line + end_line))

    # Extract the dependency lines and clean them up
    dependencies=$(sed -n "${start_line},${end_line}p" pyproject.toml | \
        grep -E '^[[:space:]]*"[^"]+"' | \
        sed 's/^[[:space:]]*"//; s/".*$//; s/[><=!].*$//' | \
        tr '\n' ' ')

    if [[ -z "$dependencies" ]]; then
        echo "No dependencies found for ${section_title}."
        return
    fi

    echo "Found dependencies: $dependencies"

    for package in $dependencies; do
        echo "Upgrading ${package}..."
        # Add the package with the latest version
        uv add "${package}" ${dependency_group}
    done
}

# Upgrade main dependencies
upgrade_dependencies "[project.dependencies]"

# Upgrade optional 'test' dependencies
upgrade_dependencies "[project.optional-dependencies.test]" "--group test"

# Upgrade optional 'dev' dependencies
upgrade_dependencies "[project.optional-dependencies.dev]" "--group dev"

echo "All dependencies have been upgraded."
