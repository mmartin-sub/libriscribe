#!/bin/bash
set -e

echo "--- Testing Documentation Commands ---"

# Test the main help command
echo "Testing: hatch run python -m libriscribe2.main --help"
hatch run python -m libriscribe2.main --help

# Test the quick test command
echo "Testing: hatch run python -m libriscribe2.main create-book --title=\"Test Book\" --mock --generate-concept"
hatch run python -m libriscribe2.main create-book --title="Test Book" --mock --generate-concept

# Test the book stats command
# Note: This requires a project to exist. The previous command created one.
echo "Testing: hatch run python -m libriscribe2.main book-stats --project-name \"Test Book\""
hatch run python -m libriscribe2.main book-stats --project-name "Test Book"

# Test the uv global installation commands
# We need to uninstall first in case a previous run installed it
echo "Testing: uv tool uninstall libriscribe2"
uv tool uninstall libriscribe2 || true # Ignore error if not installed
echo "Testing: uv tool install ."
uv tool install .
echo "Testing: libriscribe2 --version"
libriscribe2 --version
echo "Testing: uv tool uninstall libriscribe2"
uv tool uninstall libriscribe2

echo "--- All Documentation Commands Passed ---"
