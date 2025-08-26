#!/bin/bash

# A script to find and optionally delete "buggy" WireMock recordings.
# A recording is considered buggy if:
# 1. The HTTP response status is not 200.
# 2. The associated response body file is empty or contains only whitespace.
# 3. The response body file contains specific error-indicating keywords.

# --- Default Configuration ---
ROOT_DIR="."

# --- Script Flags ---
SHOW_HELP=false
DELETE_FILES=false # Dry-run mode is active by default
FORCE_DELETE=false

# --- User-Configurable Error Patterns ---
# Add or remove case-insensitive keywords to this list to customize what
# is considered an error message within a response body.
declare -a ERROR_PATTERNS=(
    "Bad Request"
    "cloudflare"
    "forbidden"
    "unauthorized"
    "server error"
    "upstream connect error"
)

# --- Color Definitions ---
COLOR_RESET='\033[0m'
COLOR_GREEN='\033[0;32m'
COLOR_YELLOW='\033[0;33m'
COLOR_RED='\033[0;31m'
COLOR_CYAN='\033[0;36m'
COLOR_GRAY='\033[0;90m'

# --- Function Definitions ---

show_help() {
    echo "WireMock Buggy Response Scanner"
    echo
    echo "Usage: ./check_wiremock_responses.sh [OPTIONS]"
    echo
    echo "Scans for WireMock mappings that are considered buggy. A mapping is buggy if it has:"
    echo "  - A non-200 HTTP response status."
    echo "  - An empty or whitespace-only body file."
    echo "  - A body file containing error keywords (e.g., 'Bad Request', 'cloudflare')."
    echo
    echo "By default, it runs in 'dry-run' mode, only reporting what it would delete."
    echo
    echo "Options:"
    echo "  -d, --directory PATH    Specify the root directory where 'mappings' and '__files'"
    echo "                          are located (default: '.')."
    echo "  --delete                Enable deletion mode. This will delete the identified"
    echo "                          mapping files and their associated body files."
    echo "  -f, --force             Use with --delete to bypass the confirmation prompt."
    echo "  --help                  Display this help message and exit."
}

# --- Argument Parsing ---
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -d|--directory)
            if [ -n "$2" ] && [ "${2:0:1}" != "-" ]; then ROOT_DIR="$2"; shift; fi ;;
        --delete) DELETE_FILES=true ;;
        -f|--force) FORCE_DELETE=true ;;
        --help) SHOW_HELP=true ;;
        *) echo -e "${COLOR_RED}Unknown parameter: $1${COLOR_RESET}"; show_help; exit 1 ;;
    esac
    shift
done

if [ "$SHOW_HELP" = true ]; then show_help; exit 0; fi
if [ "$FORCE_DELETE" = true ] && [ "$DELETE_FILES" = false ]; then
    echo -e "${COLOR_RED}Error: The --force flag can only be used with the --delete flag.${COLOR_RESET}" >&2
    exit 1
fi

# --- Dynamic Path Configuration ---
MAPPINGS_DIR="$ROOT_DIR/mappings"
FILES_DIR="$ROOT_DIR/__files"

# --- Pre-flight Checks ---
if ! command -v jq &> /dev/null; then
    echo -e "${COLOR_RED}Error: 'jq' is not installed. Please install it to continue.${COLOR_RESET}" >&2
    exit 1
fi
if [ ! -d "$MAPPINGS_DIR" ]; then
    echo -e "${COLOR_RED}Error: Directory '$MAPPINGS_DIR' not found.${COLOR_RESET}" >&2
    exit 1
fi

# --- Confirmation for Deletion ---
if [ "$DELETE_FILES" = true ] && [ "$FORCE_DELETE" = false ]; then
    echo -e "${COLOR_YELLOW}⚠️  WARNING: Deletion mode is active.${COLOR_RESET}"
    echo "This will permanently remove buggy mappings and their associated body files."
    read -p "Are you sure you want to continue? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborting."
        exit 1
    fi
fi

# --- Main Logic ---
if [ "$DELETE_FILES" = false ]; then
    echo -e "🔍 ${COLOR_CYAN}[DRY RUN]${COLOR_RESET} Scanning for buggy responses in '$MAPPINGS_DIR'..."
else
    echo -e "🔥 ${COLOR_RED}[DELETE MODE]${COLOR_RESET} Scanning for buggy responses in '$MAPPINGS_DIR'..."
fi
echo "======================================================================"

buggy_count=0
deleted_mappings=0
deleted_bodies=0

find "$MAPPINGS_DIR" -name "*.json" | while read -r mapping_file; do
    declare -a reasons=() # Use an array to store multiple reasons for failure

    # --- Check 1: Non-200 Status ---
    status=$(jq '.response.status' "$mapping_file")
    if [[ "$status" =~ ^[0-9]+$ ]] && [ "$status" -ne 200 ]; then
        reasons+=("Non-200 status: $status")
    fi

    # --- Body File Checks (only if a body file exists) ---
    body_filename=$(jq -r '.response.bodyFileName' "$mapping_file")
    if [[ -n "$body_filename" && "$body_filename" != "null" ]]; then
        body_path="$FILES_DIR/$body_filename"
        if [ -f "$body_path" ]; then
            # --- Check 2: Empty/Whitespace Body File ---
            if [ -z "$(tr -d '[:space:]' < "$body_path")" ]; then
                reasons+=("Empty body file")
            else
                # --- Check 3: Error Patterns in Body Content ---
                for pattern in "${ERROR_PATTERNS[@]}"; do
                    # Use grep -q (quiet) and -i (case-insensitive)
                    if grep -q -i "$pattern" "$body_path"; then
                        reasons+=("Body contains error text: '$pattern'")
                        break # Found a match, no need to check other patterns
                    fi
                done
            fi
        fi
    fi

    # --- Process if any condition was met ---
    if [ ${#reasons[@]} -gt 0 ]; then
        buggy_count=$((buggy_count + 1))

        # Join the reasons with a comma for clean output
        printf -v full_reason '%s, ' "${reasons[@]}"
        full_reason="${full_reason%, }" # Removes trailing comma and space

        echo -e "----------------------------------------------------------------------"
        echo -e "Found buggy recording. Reason(s): ${COLOR_YELLOW}${full_reason}${COLOR_RESET}"
        echo -e "  ${COLOR_GRAY}Mapping:${COLOR_RESET}\t$mapping_file"

        # Report or delete the mapping file
        if [ "$DELETE_FILES" = true ]; then
            if rm "$mapping_file"; then
                echo -e "  ${COLOR_RED}DELETED MAPPING${COLOR_RESET}"
                deleted_mappings=$((deleted_mappings + 1))
            else
                echo -e "  ${COLOR_RED}ERROR: Failed to delete mapping file.${COLOR_RESET}"
            fi
        else
            echo -e "  ${COLOR_CYAN}[DRY RUN] Would delete mapping file.${COLOR_RESET}"
        fi

        # Check for and handle the body file
        if [[ -n "$body_filename" && "$body_filename" != "null" ]]; then
            echo -e "  ${COLOR_GRAY}Body File:${COLOR_RESET}\t$body_path"
            if [ -f "$body_path" ]; then
                if [ "$DELETE_FILES" = true ]; then
                    if rm "$body_path"; then
                        echo -e "  ${COLOR_RED}DELETED BODY FILE${COLOR_RESET}"
                        deleted_bodies=$((deleted_bodies + 1))
                    else
                         echo -e "  ${COLOR_RED}ERROR: Failed to delete body file.${COLOR_RESET}"
                    fi
                else
                    echo -e "  ${COLOR_CYAN}[DRY RUN] Would delete body file.${COLOR_RESET}"
                fi
            else
                echo -e "  ${COLOR_YELLOW}WARNING: Body file not found at expected path.${COLOR_RESET}"
            fi
        else
             echo -e "  ${COLOR_GRAY}Body File:${COLOR_RESET}\t(None specified)"
        fi
    fi
done

# --- Final Summary ---
echo "======================================================================"
if [ "$buggy_count" -eq 0 ]; then
    echo -e "${COLOR_GREEN}✅ Scan complete. No buggy recordings found.${COLOR_RESET}"
else
    echo -e "⚠️  Scan complete. Found ${buggy_count} buggy recording(s)."
    if [ "$DELETE_FILES" = true ]; then
        echo -e "${COLOR_RED}Deleted ${deleted_mappings} mapping file(s) and ${deleted_bodies} body file(s).${COLOR_RESET}"
    fi
fi
