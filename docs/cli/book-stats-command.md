# Book Statistics Command Documentation

## Overview

The `book-stats` command provides comprehensive statistics about LibriScribe2 projects in a non-interactive format. It displays project information, chapter status, and automatically logs all statistics to the project's log file.

## Command Signature

```bash
hatch run python -m libriscribe2.main book-stats --project-name PROJECT_NAME [--show-logs]
```

## Parameters

### Required Parameters

- `--project-name PROJECT_NAME`: Name of the project to display statistics for

### Optional Parameters

- `--show-logs`: Display the last 20 lines of the project's log file

## Features

### Non-Interactive Operation

The command runs completely non-interactively, making it suitable for:
- Automated scripts and CI/CD pipelines
- Batch processing of multiple projects
- Integration with other tools and workflows

### Automatic Log File Management

- **Creates log file if missing**: If no `book_creation.log` exists in the project directory, it will be created automatically
- **Logs all statistics**: Every time the command runs, it logs a complete statistics report to the project log file
- **Timestamped entries**: All log entries include timestamps for tracking when statistics were generated

### Comprehensive Statistics Display

The command displays:
- **Project metadata**: Title, genre, language, category
- **Content metrics**: Number of chapters, characters, book length
- **Configuration settings**: Worldbuilding status, review preferences
- **Chapter status**: Which chapters exist as files vs. are only recorded in metadata
- **Dynamic questions**: Any custom questions and answers for the project

## Usage Examples

### Basic Statistics Display

```bash
# Display statistics for a project
hatch run python -m libriscribe2.main book-stats --project-name my-fantasy-novel
```

**Output:**
```
╭─────────────────────────────────╮
│ Statistics for 'my-fantasy-novel' │
╰─────────────────────────────────╯
  Title: The Dragon's Quest
  Genre: fantasy
  Language: English
  Category: Fiction
  Book Length: novel
  Number of Characters: 5
  Number of Chapters: 12
  Worldbuilding Needed: True
  Review Preference: detailed
  Description: An epic fantasy adventure about a young mage...

╭──────────────────╮
│ Chapter Status   │
╰──────────────────╯
  Chapter 1: The Beginning - Exists
  Chapter 2: The Journey - Missing
  Chapter 3: The Discovery - Exists

╭─────────────────────────────╮
│ Log File: book_creation.log │
╰─────────────────────────────╯
  Location: projects/my-fantasy-novel/book_creation.log
  Statistics logged: Yes
  Use --show-logs to view recent log entries
```

### Statistics with Log Display

```bash
# Display statistics and recent log entries
hatch run python -m libriscribe2.main book-stats --project-name my-fantasy-novel --show-logs
```

**Additional Output:**
```
╭────────────────────────────────────╮
│ Recent Log Entries (Last 20 lines) │
╰────────────────────────────────────╯
2025-08-15 11:19:29,107 - INFO - === BOOK STATISTICS REPORT ===
2025-08-15 11:19:29,107 - INFO - Statistics generated for project: my-fantasy-novel
2025-08-15 11:19:29,108 - INFO - Project Name: my-fantasy-novel
2025-08-15 11:19:29,109 - INFO - Title: The Dragon's Quest
...
2025-08-15 11:19:29,117 - INFO - === END STATISTICS REPORT ===
```

### Batch Processing Multiple Projects

```bash
# Process multiple projects in a script
for project in project1 project2 project3; do
    echo "Processing $project..."
    hatch run python -m libriscribe2.main book-stats --project-name "$project"
done
```

## Log File Format

The command logs statistics in a structured format:

```
2025-08-15 11:19:29,107 - INFO - === BOOK STATISTICS REPORT ===
2025-08-15 11:19:29,107 - INFO - Statistics generated for project: my-project
2025-08-15 11:19:29,108 - INFO - Project Name: my-project
2025-08-15 11:19:29,109 - INFO - Title: My Book Title
2025-08-15 11:19:29,110 - INFO - Genre: fantasy
2025-08-15 11:19:29,110 - INFO - Language: English
2025-08-15 11:19:29,110 - INFO - Category: Fiction
2025-08-15 11:19:29,111 - INFO - Book Length: novel
2025-08-15 11:19:29,112 - INFO - Num Characters: 5
2025-08-15 11:19:29,113 - INFO - Num Chapters: 12
2025-08-15 11:19:29,114 - INFO - Worldbuilding Needed: True
2025-08-15 11:19:29,115 - INFO - Review Preference: detailed
2025-08-15 11:19:29,116 - INFO - Description: Book description here...
2025-08-15 11:19:29,116 - INFO - --- Chapter Status ---
2025-08-15 11:19:29,117 - INFO - Chapter 1: The Beginning - Exists
2025-08-15 11:19:29,118 - INFO - Chapter 2: The Journey - Missing
2025-08-15 11:19:29,117 - INFO - === END STATISTICS REPORT ===
```

## Error Handling

### Project Not Found

```bash
$ hatch run python -m libriscribe2.cli book-stats --project-name nonexistent
Error: Project directory 'nonexistent' not found in /path/to/projects
```

### Corrupted Project Data

```bash
$ hatch run python -m libriscribe2.cli book-stats --project-name corrupted-project
Error: Corrupted project data in /path/to/projects/corrupted-project/project_data.json: Invalid JSON
```

### Missing Project Data File

```bash
$ hatch run python -m libriscribe2.cli book-stats --project-name incomplete-project
Error: Project data file not found at /path/to/projects/incomplete-project/project_data.json
```

## Integration with Other Commands

### After Book Creation

```bash
# Create a book and immediately view statistics
hatch run python -m libriscribe2.cli create-book --title "My Book" --all
hatch run python -m libriscribe2.cli book-stats --project-name "my-book"
```

### Monitoring Progress

```bash
# Check progress during book creation
hatch run python -m libriscribe2.cli book-stats --project-name "work-in-progress" --show-logs
```

### CI/CD Integration

```bash
# In a CI/CD pipeline
#!/bin/bash
set -e

# Generate statistics report
hatch run python -m libriscribe2.cli book-stats --project-name "$PROJECT_NAME" > stats_report.txt

# Check if all chapters are complete
if grep -q "Missing" stats_report.txt; then
    echo "Warning: Some chapters are missing"
    exit 1
fi

echo "All chapters complete!"
```

## Comparison with Interactive Mode

### Before (Interactive)

```bash
$ book-stats
Project name: my-project
[displays stats]
Do you want to view the last 20 lines of the log file? [y/N]: y
[displays logs]
```

### After (Non-Interactive)

```bash
$ book-stats --project-name my-project --show-logs
[displays stats and logs immediately]
```

## Benefits

1. **Automation-Friendly**: No user input required
2. **Consistent Logging**: All statistics are automatically logged
3. **Scriptable**: Easy to integrate into scripts and workflows
4. **Reliable**: Creates log files if they don't exist
5. **Comprehensive**: Shows both console output and file-based logging
6. **Flexible**: Optional log display with `--show-logs` flag

## Best Practices

### Regular Monitoring

```bash
# Add to cron job for regular project monitoring
0 9 * * * /path/to/hatch run python -m libriscribe2.cli book-stats --project-name "daily-novel" >> /var/log/book-stats.log
```

### Project Health Checks

```bash
# Script to check multiple projects
#!/bin/bash
PROJECTS_DIR="/path/to/projects"
for project_dir in "$PROJECTS_DIR"/*; do
    if [ -d "$project_dir" ]; then
        project_name=$(basename "$project_dir")
        echo "=== $project_name ==="
        hatch run python -m libriscribe2.cli book-stats --project-name "$project_name"
        echo
    fi
done
```

### Log Analysis

```bash
# Extract statistics from log files
grep "=== BOOK STATISTICS REPORT ===" projects/*/book_creation.log | wc -l
# Count how many times statistics were generated across all projects
```

## See Also

- [CLI Overview](../README.md#cli-commands)
- [Project Management](project-management.md)
- [Book Creation Workflow](book-creation-workflow.md)
- [Logging and Monitoring](logging-monitoring.md)
