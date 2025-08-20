#!/bin/bash
# This script updates the npm dependencies for the docusaurus documentation site.

# Exit immediately if a command exits with a non-zero status.
set -e

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# The docs directory is one level up from the scripts directory
DOCS_DIR="$SCRIPT_DIR/../docs"

# Check if the docs directory and package.json exist
if [ ! -d "$DOCS_DIR" ] || [ ! -f "$DOCS_DIR/package.json" ]; then
  echo "Error: Could not find docs/package.json"
  exit 1
fi

# Change to the docs directory
cd "$DOCS_DIR"

# Update npm dependencies
echo "Updating npm dependencies in $(pwd)..."
npm update

echo "Dependencies updated successfully."
