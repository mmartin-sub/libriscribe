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

# A more robust argument parsing loop
while [[ $# -gt 0 ]]; do
  case "$1" in
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
    --priority=*) # New argument for priority
      PRIORITY="${1#*=}"
      shift
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 1
      ;;
  esac
done

# --- Path Resolution ---
# Use command-line directories if provided, otherwise fall back to defaults.
INPUT_BASE_DIR=${INPUT_DIR:-$DEFAULT_INPUT_DIR}
OUTPUT_BASE_DIR=${OUTPUT_DIR:-$DEFAULT_OUTPUT_DIR}

INPUT_MAPPINGS_DIR="${INPUT_BASE_DIR}/mappings"
INPUT_FILES_DIR="${INPUT_BASE_DIR}/__files"
OUTPUT_MAPPINGS_DIR="${OUTPUT_BASE_DIR}/mappings"
OUTPUT_FILES_DIR="${OUTPUT_BASE_DIR}/__files"

# Determine if input and output directories are the same for the delete logic
ARE_DIRS_SAME=false
if [ "$(realpath "$INPUT_BASE_DIR")" == "$(realpath "$OUTPUT_BASE_DIR")" ]; then
  ARE_DIRS_SAME=true
fi


# --- Helper Functions ---
log_debug() {
  if [ "$LOG_LEVEL" == "DEBUG" ]; then
    echo -e "\033[0;33m  - DEBUG: $1\033[0m"
  fi
}

log_error() {
    echo -e "\033[0;31m  - ERROR: $1\033[0m"
}

# Handles invalid files by logging the error and optionally deleting them.
handle_invalid_file() {
  local mapping_file="$1"
  local body_file="$2"
  local reason="$3"

  log_error "$reason"
  ((ERROR_COUNT++))

  # If using 'move' and in-place, delete the invalid files to clean up.
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
echo "Input Path:  $(realpath --relative-to=. "$INPUT_BASE_DIR")"
echo "Output Path: $(realpath --relative-to=. "$OUTPUT_BASE_DIR")"
echo "Operation:   ${OPERATION}"
echo "Priority:    ${PRIORITY}" # Display the priority being used
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

  # 1. Extract body file name and validate its existence
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

  # 2. NEW: Validate that the body file is not empty (ignoring whitespace)
  if ! grep -q '[^[:space:]]' "$original_body_filepath"; then
      handle_invalid_file "$file" "$original_body_filepath" "Body file is empty or contains only whitespace."
      echo "----------------------------------------"
      continue
  fi

  # 3. Generate new mock name from URL and a unique hash
  unique_id=$(basename "$file" .json | sed -E 's/.*-([a-zA-Z0-9]+)$/\1/')
  if [ -z "$unique_id" ]; then
      handle_invalid_file "$file" "$original_body_filepath" "Could not extract a unique ID from filename."
      echo "----------------------------------------"
      continue
  fi
  url_path_part=$(jq -r '.request.url' "$file" | tr '/' '_' | sed 's/^_//')
  new_mock_name="mock_${url_path_part}_${unique_id}"

  # 4. Define destination paths
  new_mapping_filename="${new_mock_name}.json"
  new_body_filename_ref="${new_mock_name}_body.json"

  log_debug "New mock name: $new_mock_name"
  log_debug "New mapping path: ${OUTPUT_MAPPINGS_DIR}/${new_mapping_filename}"
  log_debug "New body file path: ${OUTPUT_FILES_DIR}/${new_body_filename_ref}"


  # 5. Perform file operations or simulate them
  if [ "$DRY_RUN" = true ]; then
    echo "  - [Dry Run] Would create new mapping: $new_mapping_filename (priority: $PRIORITY)"
    echo "  - [Dry Run] Would ${OPERATION} body file to: $new_body_filename_ref"
  else
    # A. Create the new, reformatted mapping file
    # Updated jq command to include priority
    jq_output=$(jq --arg name "$new_mock_name" \
       --arg body_ref "$new_body_filename_ref" \
       --argjson priority "$PRIORITY" \
    '
      {
        "name": $name,
        "priority": $priority, # <-- PRIORITY IS ADDED HERE
        "request": {
          "url": .request.url,
          "method": .request.method,
          "bodyPatterns": [
            {
              "equalToJson": (.request.bodyPatterns[0].equalToJson | fromjson | { "messages": .messages } | tojson),
              "ignoreExtraElements": true,
              "ignoreArrayOrder": true
            }
          ]
        },
        "response": {
          "status": .response.status,
          "bodyFileName": $body_ref,
          "headers": { "Content-Type": "application/json" }
        }
      }
    ' "$file" 2> /tmp/jq_error.log)

    # B. Check if jq succeeded before proceeding.
    if [ $? -eq 0 ]; then
      echo "$jq_output" > "${OUTPUT_MAPPINGS_DIR}/${new_mapping_filename}"
      echo "  - Created new mapping: $new_mapping_filename"

      # C. Copy or move the body file.
      if [ "$OPERATION" == "copy" ]; then
          cp "$original_body_filepath" "${OUTPUT_FILES_DIR}/${new_body_filename_ref}"
          echo "  - Copied body file to: $new_body_filename_ref"
      else # move
          mv "$original_body_filepath" "${OUTPUT_FILES_DIR}/${new_body_filename_ref}"
          echo "  - Moved body file to: $new_body_filename_ref"
          rm "$file"
          echo "  - Removed original mapping: $(basename "$file")"
      fi
    else
      # D. Handle jq failure
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
