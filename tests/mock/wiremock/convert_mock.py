#!/usr/bin/env python3
import argparse
import glob
import json
import os
import re
from pathlib import Path


# ANSI color codes for prettier output
class bcolors:
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def generate_robust_regex(text: str) -> str:
    """Converts a plain string into a whitespace-insensitive regex pattern."""
    escaped_text = re.escape(text.strip())
    whitespace_insensitive_regex = re.sub(r'\s+', r'\\s+', escaped_text)
    return f"(?s){whitespace_insensitive_regex}"

def generate_human_readable_regex(regex: str) -> str:
    """Converts the generated regex into a more human-readable format."""
    return re.sub(r'\\s\+', ' ', regex)

def process_mapping_file(file_path: Path, prompt_save_path: Path, dry_run: bool, verbose: bool) -> tuple[str, str, Path | None]:
    """
    Reads a mapping file, and if it's a candidate, converts it.
    Returns a status, a message, and the path to the created prompt file.
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        return "SKIPPED", "Invalid JSON format", None

    try:
        patterns = data['request']['bodyPatterns']
        if not isinstance(patterns, list) or not patterns:
            return "SKIPPED", "No body patterns found", None

        # Check if the file has already been processed
        if 'matchesJsonPath' in patterns[0]:
            return "SKIPPED", "Already converted to 'matchesJsonPath'", None

        if 'equalToJson' not in patterns[0]:
            return "SKIPPED", "Does not use 'equalToJson' in the first body pattern", None

        inner_data = json.loads(patterns[0]['equalToJson'])
        clean_prompt = inner_data['messages'][0]['content']
    except (KeyError, IndexError, TypeError, json.JSONDecodeError):
        return "SKIPPED", "JSON structure does not match target conversion pattern", None

    # --- Candidate for Conversion ---
    robust_regex = generate_robust_regex(clean_prompt)
    new_body_pattern = {"matchesJsonPath": {"expression": "$.messages[0].content", "matches": robust_regex}}
    data['request']['bodyPatterns'] = [new_body_pattern]

    if verbose:
        print(f"\n{bcolors.OKCYAN}--- Human-Readable Regex for {file_path.name} ---{bcolors.ENDC}")
        print(generate_human_readable_regex(robust_regex))
        print(f"{bcolors.OKCYAN}--- End Human-Readable Regex ---{bcolors.ENDC}")

    try:
        json.loads(json.dumps(data))
    except (TypeError, json.JSONDecodeError) as e:
        return "ERROR", f"Generated content was not valid JSON. Aborting. Error: {e}", None

    if not dry_run:
        with open(prompt_save_path, 'w') as f:
            f.write(clean_prompt)
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        return "CONVERTED", f"-> Prompt at {prompt_save_path}", prompt_save_path
    else:
        return "CONVERTED", f"(Dry Run) -> Would save prompt to {prompt_save_path}", prompt_save_path

def main():
    parser = argparse.ArgumentParser(
        description="A tool to automatically convert brittle WireMock 'equalToJson' mappings to robust 'matchesJsonPath' regex mappings.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('path_pattern', type=str,
                        help="Path pattern for the mapping files to process.\n"
                             "Examples:\n"
                             "  './wiremock-recordings/mappings/*.json'\n"
                             "  './wiremock-recordings/mappings/mock_v1_chat*.json'")
    parser.add_argument('--prompts-dir', type=str, default=None,
                        help="[Override] Specify a directory to save all prompt .txt files.\n"
                             "If used, prompts are always kept.")
    parser.add_argument('--keep-prompts', action='store_true',
                        help="Use with default behavior to keep the prompt files next to the mappings.")
    parser.add_argument('--dry-run', action='store_true',
                        help="Scan and report what would be changed without modifying any files.")
    parser.add_argument('--verbose', action='store_true',
                        help="Print the human-readable version of the regex for debugging.")

    args = parser.parse_args()

    file_list = glob.glob(args.path_pattern)
    if not file_list:
        print(f"{bcolors.FAIL}Error: No files found matching the pattern '{args.path_pattern}'{bcolors.ENDC}")
        return

    if args.dry_run:
        print(f"{bcolors.WARNING}--- Starting in DRY RUN mode. No files will be modified. ---{bcolors.ENDC}")

    prompts_override_dir = Path(args.prompts_dir) if args.prompts_dir else None
    if prompts_override_dir:
        prompts_override_dir.mkdir(parents=True, exist_ok=True)

    results = {"CONVERTED": [], "SKIPPED": [], "ERROR": []}

    for file_path_str in file_list:
        file_path = Path(file_path_str)

        # Determine where to save the prompt file
        if prompts_override_dir:
            prompt_save_path = prompts_override_dir / f"{file_path.stem}_prompt.txt"
        else:
            prompt_save_path = file_path.parent / f"{file_path.stem}_prompt.txt"

        status, message, created_prompt_path = process_mapping_file(file_path, prompt_save_path, args.dry_run, args.verbose)
        results[status].append((file_path, message))

        # --- Automatic Cleanup Logic ---
        if (status == "CONVERTED" and not args.dry_run and not prompts_override_dir and not args.keep_prompts):
            if created_prompt_path and created_prompt_path.exists():
                created_prompt_path.unlink() # Delete the temporary prompt file

    # --- Print Summary Report ---
    print(f"\n{bcolors.BOLD}--- Conversion Summary ---{bcolors.ENDC}")

    if results["CONVERTED"]:
        print(f"\n{bcolors.OKGREEN}✅ Files Converted: {len(results['CONVERTED'])}{bcolors.ENDC}")
        for file, msg in results["CONVERTED"]:
            print(f"   - {file.name} {msg}")

    if results["ERROR"]:
        print(f"\n{bcolors.FAIL}❌ Errors Encountered: {len(results['ERROR'])}{bcolors.ENDC}")
        for file, msg in results["ERROR"]:
            print(f"   - {file.name}: {msg}")

    print(f"\n{bcolors.OKCYAN}⚪ Files Skipped (No conversion needed): {len(results['SKIPPED'])}{bcolors.ENDC}")
    # Display skipped files for clarity
    for file, msg in results["SKIPPED"]:
        print(f"   - {file.name}: {msg}")


    if args.dry_run:
         print(f"\n{bcolors.WARNING}--- DRY RUN complete. No files were modified. ---{bcolors.ENDC}")
    else:
        print(f"\n{bcolors.BOLD}Scan complete.{bcolors.ENDC}")

if __name__ == '__main__':
    main()
