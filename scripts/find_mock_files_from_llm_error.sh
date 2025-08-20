#!/bin/bash
# This script finds the mock and body json files from an llm_error_exchange log file.

# Exit immediately if a command exits with a non-zero status.
set -e

if [ -z "$1" ]; then
  echo "Usage: $0 <path_to_llm_error_exchange_log>"
  exit 1
fi

LOG_FILE="$1"

if [ ! -f "$LOG_FILE" ]; then
  echo "Error: Log file not found: $LOG_FILE"
  exit 1
fi

echo "Searching for mock files in $LOG_FILE..."

# Use grep with a regular expression to find the file paths
# The paths are expected to be in the format: tests/mock/wiremock/wiremock-recordings/__files/body-v1-chat-completions-*.json
# or tests/mock/wiremock/wiremock-recordings/mappings/mock_v1_chat_completions_*.json
# The -o flag prints only the matching parts of the lines
# The -E flag enables extended regular expressions
grep -o -E 'tests/mock/wiremock/wiremock-recordings/(__files/body-v1-chat-completions-[a-zA-Z0-9_]+.json|mappings/mock_v1_chat_completions-[a-zA-Z0-9_]+.json)' "$LOG_FILE" | sort | uniq
