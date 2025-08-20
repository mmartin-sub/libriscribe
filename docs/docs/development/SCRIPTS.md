# Development Scripts

This document describes the available scripts for development and maintenance of the LibriScribe2 project.

## Updating Documentation Dependencies

To update the npm dependencies for the Docusaurus documentation site, run the following command:

```bash
hatch run docs:update-deps
```

This script is a convenient wrapper around `npm update` and is defined in `pyproject.toml`. It executes the `scripts/update_docs_deps.sh` script.

## Building the Documentation

To build the documentation locally, you can use the `build_docs.sh` script:

```bash
./scripts/build_docs.sh
```

This will install the necessary npm dependencies and build the Docusaurus site. The output will be in the `docs/build` directory.

## Finding Mock Files from LLM Error Logs

When a test that uses `wiremock` fails due to an LLM error, an `llm_error_exchange_*.log` file is created. This log file contains the input and output of the failed LLM call.

To find the specific `mock_*.json` and `body_*.json` files that were used in the failed call, you can use the `find_mock_files_from_llm_error.sh` script. This is useful for cleaning up the mock files after a failed test run.

**Usage:**

```bash
./scripts/find_mock_files_from_llm_error.sh <path_to_llm_error_exchange_log>
```

**Example:**

```bash
./scripts/find_mock_files_from_llm_error.sh logs/llm_error_exchange_1678886400_abcdef12.log
```

This will print the paths of the mock files found in the log, which can then be used for cleanup.
