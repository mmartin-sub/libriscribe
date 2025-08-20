#!/bin/bash

# A script to find and classify duplicate WireMock recordings.
# It can identify:
# - Full duplicates (identical request and response body)
# - Partial duplicates (identical request, but different response bodies)

# --- Default Configuration ---
ROOT_DIR="."

# --- Script Flags ---
SHOW_HELP=false
DELETE_FILES=false
FORCE_DELETE=false
declare -a EXCLUDE_PATTERNS=("proxy*.json") # Array of patterns to exclude

# --- Color Definitions ---
COLOR_RESET='\033[0m'
COLOR_GREEN='\033[0;32m'
COLOR_YELLOW='\033[0;33m'
COLOR_RED='\033[0;31m'
COLOR_CYAN='\033[0;36m'

# --- Function Definitions ---

show_help() {
    echo "WireMock Duplicate Scanner"
    echo
    echo "Usage: ./find_wiremock_duplicates.sh [OPTIONS]"
    echo
    echo "Scans WireMock mappings to find full and partial duplicates."
    echo
    echo "Options:"
    echo "  -d, --directory PATH    Specify the root directory where 'mappings' and '__files'"
    echo "                          are located (e.g., 'wiremock-recordings')."
    echo "  --delete                Delete all but one file from each duplicate group found."
    echo "  -f, --force             Use with --delete to bypass the confirmation prompt."
    echo "  --help                  Display this help message and exit."
    echo
    echo "Exclusions:"
    echo "  By default, files matching 'proxy*.json' are excluded. This can be"
    echo "  changed by editing the EXCLUDE_PATTERNS array in the script."
}

# --- Argument Parsing ---
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -d|--directory)
            if [ -n "$2" ] && [ "${2:0:1}" != "-" ]; then ROOT_DIR="$2"; shift; fi ;;
        --delete) DELETE_FILES=true ;;
        -f|--force) FORCE_DELETE=true ;;
        --help) SHOW_HELP=true ;;
        *) echo "Unknown parameter: $1"; show_help; exit 1 ;;
    esac
    shift
done

if [ "$SHOW_HELP" = true ]; then show_help; exit 0; fi
if [ "$FORCE_DELETE" = true ] && [ "$DELETE_FILES" = false ]; then
    echo -e "${COLOR_RED}Error: The --force flag can only be used with the --delete flag.${COLOR_RESET}" >&2; exit 1;
fi

# --- Dynamic Path Configuration ---
MAPPINGS_DIR="$ROOT_DIR/mappings"
FILES_DIR="$ROOT_DIR/__files"

# --- Pre-flight Checks ---
if ! command -v jq &> /dev/null; then echo -e "${COLOR_RED}Error: 'jq' is not installed.${COLOR_RESET}" >&2; exit 1; fi
if [ ! -d "$MAPPINGS_DIR" ]; then echo -e "${COLOR_RED}Error: Directory '$MAPPINGS_DIR' not found.${COLOR_RESET}" >&2; exit 1; fi

# --- Confirmation for Deletion ---
if [ "$DELETE_FILES" = true ] && [ "$FORCE_DELETE" = false ]; then
    echo -e "${COLOR_YELLOW}⚠️  WARNING: The --delete flag is active.${COLOR_RESET}"
    echo "This will permanently remove all but the first file in each duplicate group."
    read -p "Are you sure you want to continue? [y/N] " -n 1 -r; echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then echo "Aborting."; exit 1; fi
fi

echo "🔍 Scanning for duplicates in '$MAPPINGS_DIR'..."
echo "================================================="

# --- Main Logic ---
find "$MAPPINGS_DIR" -name "*.json" | while read -r mapping_file; do
    filename=$(basename "$mapping_file")
    is_excluded=false
    for pattern in "${EXCLUDE_PATTERNS[@]}"; do
        if [[ $filename == $pattern ]]; then is_excluded=true; break; fi
    done
    if [ "$is_excluded" = true ]; then continue; fi

    req_hash=$(jq -c ".request" "$mapping_file" | md5sum | cut -d' ' -f1)
    if [[ "$req_hash" == "d41d8cd98f00b204e9800998ecf8427e" ]]; then continue; fi # MD5 of empty string

    body_filename=$(jq -r '.response.bodyFileName' "$mapping_file")
    body_hash="NO_BODY_FILE"; body_path="N/A"

    if [[ -n "$body_filename" && "$body_filename" != "null" ]]; then
        body_path="$FILES_DIR/$body_filename"
        if [ -f "$body_path" ]; then
            body_hash=$(md5sum "$body_path" | cut -d' ' -f1)
        else
            body_hash="MISSING_BODY_FILE"
        fi
    fi
    echo "$req_hash|$body_hash|$mapping_file|$body_path"

done | sort -t'|' -k1,2 | awk -v delete_mode="$DELETE_FILES" '
BEGIN {
    FS = "|"; OFS = "\t"; group_count = 0;
    COLOR_RESET = "\033[0m"; COLOR_GREEN = "\033[0;32m"; COLOR_YELLOW = "\033[0;33m"; COLOR_CYAN = "\033[0;36m";
}

function process_group() {
    if (count <= 1) return;

    group_count++;
    print "-------------------------------------------------";

    is_full_duplicate = 1;
    for (i = 2; i <= count; i++) {
        if (group_body_hash[1] != group_body_hash[i]) {
            is_full_duplicate = 0;
            break;
        }
    }

    if (is_full_duplicate) {
        print COLOR_GREEN "Found Full Duplicate Group (Identical Request and Response):" COLOR_RESET;
    } else {
        print COLOR_YELLOW "Found Partial Duplicate Group (Identical Request, Different Responses):" COLOR_RESET;
    }

    for (i = 1; i <= count; i++) {
        print ""; # Add spacing
        print "    Mapping: " group_file[i];
        if (group_body_path[i] == "N/A") {
            print "    Body:    " group_body_path[i];
        } else {
            print "    Body:    " group_body_path[i] " (" COLOR_CYAN "Hash: " group_body_hash[i] COLOR_RESET ")";
        }
    }

    # ##################################################################
    # ### CRITICAL FIX HERE ###
    # ##################################################################
    # The condition now explicitly checks if delete_mode is the string "true".
    if (delete_mode == "true") {
        print "";
        for (i = 2; i <= count; i++) {
            mapping_to_delete = group_file[i];
            body_to_delete = group_body_path[i];

            system("rm \"" mapping_to_delete "\"");
            print "  -> " COLOR_YELLOW "DELETED MAPPING: " mapping_to_delete COLOR_RESET;

            if (body_to_delete != "N/A" && group_body_hash[i] != "MISSING_BODY_FILE") {
                system("rm \"" body_to_delete "\"");
                print "  -> " COLOR_YELLOW "DELETED BODY:    " body_to_delete COLOR_RESET;
            }
        }
    }
}

# Main loop
{
    req_hash = $1;
    if (req_hash != prev_req_hash && NR > 1) {
        process_group();
        count = 0;
        delete group_file; delete group_body_hash; delete group_body_path;
    }

    count++;
    group_file[count] = $3;
    group_body_hash[count] = $2;
    group_body_path[count] = $4;
    prev_req_hash = req_hash;
}

# END block
END {
    process_group();
    print "=================================================";
    if (group_count == 0) {
        print COLOR_GREEN "✅ Scan complete. No duplicate mappings found." COLOR_RESET;
    } else {
        print COLOR_YELLOW "⚠️  Scan complete. Found " group_count " duplicate group(s)." COLOR_RESET;
    }
}
'
