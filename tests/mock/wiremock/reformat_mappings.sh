#!/bin/bash
#
# A script to reformat WireMock recordings into cleaner, more robust mock definitions.
# It reads from an input directory and writes to an output directory,
# either by copying (default) or moving the original files.
#
# Improvements include:
# - Command-line specification for input/output directories.
# - Validation for empty body files.
# - Deletion of invalid files when using --move with the same input/output directory.
# - Cleaner, less verbose logging using relative paths.
# - Addition of a configurable priority to mapping files.
# - A help option for usage instructions.
# - An option to force the output directory to be the same as the input.
# - Smarter, less verbose logging for in-place move operations.
#

# --- Default Configuration ---
# Get the directory where the script itself is located.
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
DEFAULT_INPUT_DIR="${SCRIPT_DIR}/wiremock-recordings"
DEFAULT_OUTPUT_DIR="${SCRIPT_DIR}/wiremock-playing"

# --- Argument Parsing ---
DRY_RUN=false
OPERATION="copy"
LOG_LEVEL="INFO"
MAX_ERRORS=0 # 0 means infinite, will not stop on errors.
ERROR_COUNT=0
INPUT_DIR=""
OUTPUT_DIR=""
PRIORITY=5 # Default priority for WireMock stubs
OUTPUT_LIKE_INPUT=false

# --- Helper Functions ---
show_help() {
  cat << EOF
Usage: $(basename "$0") [OPTIONS]

A script to reformat WireMock recordings into cleaner, more robust mock definitions.
It reads from an input directory and writes to an output directory.

Options:
  --help, -h            Display this help message and exit.
  --move                Move files from input to output. If input and output directories
                        are the same, this will also delete invalid/unprocessed files.
  --copy                Copy files (this is the default behavior).
  --dry-run             Simulate the process without creating, moving, or deleting any files.
  --input-dir DIR       Specify the input directory containing 'mappings' and '__files'.
                        Default: "${DEFAULT_INPUT_DIR}"
  --output-dir DIR      Specify the output directory for the reformatted mocks.
                        This option is ignored if --output-like-input is used.
                        Default: "${DEFAULT_OUTPUT_DIR}"
  --output-like-input   Set the output directory to be the same as the input directory.
                        This is useful for in-place modifications. Overrides --output-dir.
  --priority=NUM        Set the priority for the generated WireMock stubs.
                        Default: 5
  --log=LEVEL           Set the log level. Only 'DEBUG' is currently supported to show
                        more verbose output. Default: 'INFO'.
  --max-error=NUM       Stop the script after a specified number of errors.
                        A value of 0 means it will never stop on errors. Default: 0.

Example for in-place modification:
  $(basename "$0") --move --output-like-input --input-dir ./wiremock/stubs

Example for reformatting to a different directory:
  $(basename "$0") --copy --input-dir /tmp/raw-mocks --output-dir ./wiremock/stubs --priority=10
EOF
}

log_debug() {
  if [ "$LOG_LEVEL" == "DEBUG" ]; then
    echo -e "\033[0;33m  - DEBUG: $1\033[0m"
  fi
}

log_error() {
    echo -e "\033[0;31m  - ERROR: $1\033[0m"
}

# A more robust argument parsing loop
while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h)
      show_help
      exit 0
      ;;
    --move)
      OPERATION="move"
      shift
      ;;
    --copy)
      OPERATION="copy"
      shift
      ;;
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --output-like-input)
      OUTPUT_LIKE_INPUT=true
      shift
      ;;
    --log=*)
      LOG_LEVEL="${1#*=}"
      shift
      ;;
    --max-error=*)
      MAX_ERRORS="${1#*=}"
      shift
      ;;
    --input-dir)
      INPUT_DIR="$2"
      shift 2
      ;;
    --output-dir)
      OUTPUT_DIR="$2"
      shift 2
      ;;
    --priority=*)
      PRIORITY="${1#*=}"
      shift
      ;;
    *)
      echo "Unknown option: $1" >&2
      show_help
      exit 1
      ;;
  esac
done

# --- Path Resolution ---
INPUT_BASE_DIR=${INPUT_DIR:-$DEFAULT_INPUT_DIR}
if [ "$OUTPUT_LIKE_INPUT" = true ]; then
    OUTPUT_BASE_DIR=$INPUT_BASE_DIR
else
    OUTPUT_BASE_DIR=${OUTPUT_DIR:-$DEFAULT_OUTPUT_DIR}
fi

INPUT_BASE_DIR_ABS=$(realpath "$INPUT_BASE_DIR")
OUTPUT_BASE_DIR_ABS=$(realpath "$OUTPUT_BASE_DIR")

INPUT_MAPPINGS_DIR="${INPUT_BASE_DIR_ABS}/mappings"
INPUT_FILES_DIR="${INPUT_BASE_DIR_ABS}/__files"
OUTPUT_MAPPINGS_DIR="${OUTPUT_BASE_DIR_ABS}/mappings"
OUTPUT_FILES_DIR="${OUTPUT_BASE_DIR_ABS}/__files"

ARE_DIRS_SAME=false
if [ "$INPUT_BASE_DIR_ABS" == "$OUTPUT_BASE_DIR_ABS" ]; then
  ARE_DIRS_SAME=true
fi

# Handles invalid files by logging the error and optionally deleting them.
handle_invalid_file() {
  local mapping_file="$1"
  local body_file="$2"
  local reason="$3"
  log_error "$reason"
  ((ERROR_COUNT++))
  if [ "$OPERATION" == "move" ] && [ "$ARE_DIRS_SAME" = true ]; then
    if [ "$DRY_RUN" = true ]; then
      echo "  - [Dry Run] Would DELETE invalid mapping file: $(basename "$mapping_file")"
      [ -n "$body_file" ] && echo "  - [Dry Run] Would DELETE associated body file: $(basename "$body_file")"
    else
      echo "  - Deleting invalid mapping file: $(basename "$mapping_file")"
      rm -f "$mapping_file"
      if [ -n "$body_file" ] && [ -f "$body_file" ]; then
        echo "  - Deleting associated body file: $(basename "$body_file")"
        rm -f "$body_file"
      fi
    fi
  fi
}

# --- Pre-flight Checks ---
if ! command -v jq &> /dev/null; then
  echo "Error: jq is not installed. Please install it to run this script." >&2
  exit 1
fi
if [ ! -d "$INPUT_MAPPINGS_DIR" ]; then
  echo "Error: Input mappings directory not found at '$INPUT_MAPPINGS_DIR'" >&2
  exit 1
fi
if [ "$DRY_RUN" = false ]; then
  mkdir -p "$OUTPUT_MAPPINGS_DIR"
  mkdir -p "$OUTPUT_FILES_DIR"
fi

# --- Main Processing Loop ---
echo "--- Starting Reformatting Process ---"
if [ "$DRY_RUN" = true ]; then echo "--- Running in DRY RUN Mode ---"; fi
echo "Input Path:  $(realpath --relative-to=. "$INPUT_BASE_DIR_ABS")"
echo "Output Path: $(realpath --relative-to=. "$OUTPUT_BASE_DIR_ABS")"
if [ "$ARE_DIRS_SAME" = true ]; then
    echo "Mode:        In-place operation (input and output are the same)"
fi
echo "Operation:   ${OPERATION}"
echo "Priority:    ${PRIORITY}"
log_debug "Log Level set to DEBUG"
if [ "$MAX_ERRORS" -gt 0 ]; then echo "Will stop after $MAX_ERRORS error(s)."; fi
echo "----------------------------------------"

shopt -s nullglob
files_to_process=("$INPUT_MAPPINGS_DIR"/mapping-*.json)

if [ ${#files_to_process[@]} -eq 0 ]; then
  echo "No mapping files found to process in '$INPUT_MAPPINGS_DIR'."
  exit 0
fi

for file in "${files_to_process[@]}"; do
  echo "Processing: $(basename "$file")"
  original_body_filename=$(jq -r '.response.bodyFileName' "$file")
  if [ -z "$original_body_filename" ] || [ "$original_body_filename" == "null" ]; then
      handle_invalid_file "$file" "" "Could not extract bodyFileName."
      echo "----------------------------------------"
      continue
  fi
  original_body_filepath="${INPUT_FILES_DIR}/${original_body_filename}"
  if [ ! -f "$original_body_filepath" ]; then
      handle_invalid_file "$file" "" "Associated body file is missing at '${original_body_filepath}'."
      echo "----------------------------------------"
      continue
  fi
  if ! grep -q '[^[:space:]]' "$original_body_filepath"; then
      handle_invalid_file "$file" "$original_body_filepath" "Body file is empty or contains only whitespace."
      echo "----------------------------------------"
      continue
  fi
  unique_id=$(basename "$file" .json | sed -E 's/.*-([a-zA-Z0-9]+)$/\1/')
  if [ -z "$unique_id" ]; then
      handle_invalid_file "$file" "$original_body_filepath" "Could not extract a unique ID from filename."
      echo "----------------------------------------"
      continue
  fi
  url_path_part=$(jq -r '.request.url' "$file" | tr '/' '_' | sed 's/^_//')
  new_mock_name="mock_${url_path_part}_${unique_id}"
  new_mapping_filename="${new_mock_name}.json"
  new_body_filename_ref="${new_mock_name}_body.json"
  log_debug "New mock name: $new_mock_name"
  log_debug "New mapping path: ${OUTPUT_MAPPINGS_DIR}/${new_mapping_filename}"
  log_debug "New body file path: ${OUTPUT_FILES_DIR}/${new_body_filename_ref}"

  if [ "$DRY_RUN" = true ]; then
    echo "  - [Dry Run] Would create new mapping: $new_mapping_filename (priority: $PRIORITY)"
    echo "  - [Dry Run] Would ${OPERATION} body file to: $new_body_filename_ref"
  else
    jq_output=$(jq --arg name "$new_mock_name" \
       --arg body_ref "$new_body_filename_ref" \
       --argjson priority "$PRIORITY" \
    '
      {
        "name": $name, "priority": $priority, "request": { "url": .request.url, "method": .request.method,
        "bodyPatterns": [ { "equalToJson": (.request.bodyPatterns[0].equalToJson | fromjson | { "messages": .messages } | tojson),
        "ignoreExtraElements": true, "ignoreArrayOrder": true } ] },
        "response": { "status": .response.status, "bodyFileName": $body_ref,
        "headers": { "Content-Type": "application/json" } }
      }
    ' "$file" 2> /tmp/jq_error.log)

    if [ $? -eq 0 ]; then
      echo "$jq_output" > "${OUTPUT_MAPPINGS_DIR}/${new_mapping_filename}"
      if [ "$OPERATION" == "copy" ]; then
          cp "$original_body_filepath" "${OUTPUT_FILES_DIR}/${new_body_filename_ref}"
      else # move
          mv "$original_body_filepath" "${OUTPUT_FILES_DIR}/${new_body_filename_ref}"
          rm "$file"
      fi

      # --- MODIFIED LOGIC: Provide concise or verbose logging based on context ---
      if [ "$OPERATION" == "move" ] && [ "$ARE_DIRS_SAME" = true ] && [ "$LOG_LEVEL" != "DEBUG" ]; then
        # Concise log for the common in-place move operation
        echo "  - Reformatted and renamed to: $new_mapping_filename"
      else
        # Verbose log for copy, move to a different directory, or any debug run
        echo "  - Created new mapping: $new_mapping_filename"
        if [ "$OPERATION" == "copy" ]; then
            echo "  - Copied body file to: $new_body_filename_ref"
        else # move
            echo "  - Moved body file to: $new_body_filename_ref"
            echo "  - Removed original mapping: $(basename "$file")"
        fi
      fi
    else
      handle_invalid_file "$file" "$original_body_filepath" "Failed to reformat content with jq."
      log_debug "jq error details: $(cat /tmp/jq_error.log)"
      if [ "$MAX_ERRORS" -gt 0 ] && [ "$ERROR_COUNT" -ge "$MAX_ERRORS" ]; then
        log_error "Maximum error count of $MAX_ERRORS reached. Aborting script."
        exit 1
      fi
    fi
  fi
  echo "----------------------------------------"
done

echo "Script finished."
