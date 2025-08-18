# LibriScribe2 CLI Usage Examples

This file demonstrates comprehensive usage of the LibriScribe2 CLI commands with practical examples for different scenarios and use cases.

> **Note:** These are shell command examples, not Python code to execute. Run these commands in your terminal with the appropriate hatch environment.

---

## BASIC BOOK CREATION EXAMPLES

### 1. Create a complete book with all generation steps (RECOMMENDED)

```bash
hatch run python -m libriscribe2.main create-book \
    --title="My Awesome Fantasy Novel" \
    --genre=fantasy \
    --description="A tale of epic proportions about heroes saving the world" \
    --category=fiction \
    --characters=5 \
    --worldbuilding \
    --all
```

### 2. Create a book with auto-generated title (useful for quick testing)

```bash
hatch run python -m libriscribe2.main create-book \
    --project-type=novel \
    --genre=mystery \
    --auto-title \
    --all \
    --mock
```

### 3. Create different project types

**Short story:**

```bash
hatch run python -m libriscribe2.main create-book \
    --project-type=short_story \
    --genre=horror \
    --auto-title \
    --all \
    --mock
```

**Novella:**

```bash
hatch run python -m libriscribe2.main create-book \
    --project-type=novella \
    --genre=romance \
    --auto-title \
    --all \
    --mock
```

**Epic novel:**

```bash
hatch run python -m libriscribe2.main create-book \
    --project-type=epic \
    --genre=fantasy \
    --auto-title \
    --all \
    --mock
```

### 4. Create with custom project name (spaces allowed)

```bash
hatch run python -m libriscribe2.main create-book \
    --title="My Book" \
    --project-name="my custom project name" \
    --genre=fantasy \
    --all
```

---

## ADVANCED CONFIGURATION EXAMPLES

### 5. Use custom configuration file

```bash
hatch run python -m libriscribe2.main create-book \
    --config-file=config-example.json \
    --title="Configured Book" \
    --genre=sci-fi \
    --all
```

### 6. Override project type defaults with custom values

**Custom chapter count:**

```bash
hatch run python -m libriscribe2.main create-book \
    --project-type=novel \
    --chapters=15 \
    --genre=fantasy \
    --auto-title \
    --all \
    --mock
```

**Custom scenes per chapter:**

```bash
hatch run python -m libriscribe2.main create-book \
    --project-type=novel \
    --scenes-per-chapter=5-8 \
    --genre=fantasy \
    --auto-title \
    --all \
    --mock
```

### 7. Specify target audience and language

```bash
hatch run python -m libriscribe2.main create-book \
    --title="Young Adult Adventure" \
    --genre=adventure \
    --target-audience="Young Adult" \
    --language=English \
    --characters=3-5 \
    --all
```

### 8. Use LiteLLM user tagging for tracking

```bash
hatch run python -m libriscribe2.main create-book \
    --title="Tracked Book" \
    --genre=fantasy \
    --user="user-123" \
    --all
```

---

## STEP-BY-STEP GENERATION EXAMPLES

### 9. Generate only specific components (instead of --all)

**Generate concept and outline only:**

```bash
hatch run python -m libriscribe2.main create-book \
    --title="My Book" \
    --genre=mystery \
    --generate-concept \
    --generate-outline
```

**Generate characters and worldbuilding:**

```bash
hatch run python -m libriscribe2.main create-book \
    --title="My Fantasy World" \
    --genre=fantasy \
    --worldbuilding \
    --generate-characters \
    --generate-worldbuilding
```

**Write chapters only (assumes concept/outline exist):**

```bash
hatch run python -m libriscribe2.main create-book \
    --title="Existing Project" \
    --write-chapters
```

**Format book only (assumes chapters exist):**

```bash
hatch run python -m libriscribe2.main create-book \
    --title="Complete Project" \
    --format-book
```

---

## PROJECT MANAGEMENT EXAMPLES

### 10. View book statistics and logs

```bash
# Basic statistics display
hatch run python -m libriscribe2.main book-stats --project-name my_book

# View statistics with recent log entries
hatch run python -m libriscribe2.main book-stats --project-name my_book --show-logs

# For project with spaces in name:
hatch run python -m libriscribe2.main book-stats --project-name "my custom project" --show-logs
```

### 11. Generate title for existing project

```bash
hatch run python -m libriscribe2.main generate-title --project-name my_book
# Using mock mode:
hatch run python -m libriscribe2.main generate-title \
    --project-name my_book \
    --mock
# With custom config:
hatch run python -m libriscribe2.main generate-title \
    --project-name my_book \
    --config-file=config-example.json
```

### 12. Resume incomplete project

```bash
hatch run python -m libriscribe2.main resume --project-name my_book
```

---

## TESTING AND DEVELOPMENT EXAMPLES

### 13. Mock mode for testing (no API consumption)

**Test complete book creation without API calls:**

```bash
hatch run python -m libriscribe2.main create-book \
    --title="Test Book" \
    --genre=fantasy \
    --mock \
    --all
```

**Test with different project types:**

```bash
hatch run python -m libriscribe2.main create-book \
    --project-type=short_story \
    --auto-title \
    --mock \
    --all
```

### 14. Custom logging configuration

**Debug level logging:**

```bash
hatch run python -m libriscribe2.main create-book \
    --title="Debug Book" \
    --log-level=DEBUG \
    --all
```

**Custom log file location:**

```bash
hatch run python -m libriscribe2.main create-book \
    --title="Custom Log Book" \
    --log-file=custom.log \
    --all
```

---

## CHARACTER AND WORLDBUILDING EXAMPLES

### 15. Different character configurations

**Exact number of characters:**

```bash
hatch run python -m libriscribe2.main create-book \
    --title="Five Character Story" \
    --characters=5 \
    --genre=adventure \
    --all
```

**Range of characters:**

```bash
hatch run python -m libriscribe2.main create-book \
    --title="Variable Cast Story" \
    --characters=3-7 \
    --genre=fantasy \
    --all
```

**Minimum number of characters:**

```bash
hatch run python -m libriscribe2.main create-book \
    --title="Large Cast Story" \
    --characters=5+ \
    --genre=epic \
    --all
```

### 16. Worldbuilding enabled projects

**Fantasy with worldbuilding:**

```bash
hatch run python -m libriscribe2.main create-book \
    --title="Fantasy Realm" \
    --genre=fantasy \
    --worldbuilding \
    --characters=4 \
    --all
```

**Sci-fi with worldbuilding:**

```bash
hatch run python -m libriscribe2.main create-book \
    --title="Future World" \
    --genre=sci-fi \
    --worldbuilding \
    --characters=3 \
    --all
```

---

## ERROR HANDLING AND WORKFLOW INTEGRATION EXAMPLES

### 17. Workflow integration with error checking

**Bash script example for workflow integration:**

```bash
#!/bin/bash

# Create book and check exit code
if hatch run python -m libriscribe2.main create-book \
    --title="Workflow Book" \
    --genre=fantasy \
    --all; then
    echo "✅ Book creation successful"

    # View statistics
    hatch run python -m libriscribe2.main book-stats --project-name "workflow-book"

    # Generate title if needed
    hatch run python -m libriscribe2.main generate-title --project-name "workflow-book"
else
    exit_code=$?
    echo "❌ Book creation failed with exit code $exit_code"

    case $exit_code in
        1) echo "Runtime or unexpected error" ;;
        2) echo "Invalid input provided" ;;
        3) echo "Missing dependencies" ;;
        5) echo "Book creation process failed" ;;
        *) echo "Unknown error" ;;
    esac

    exit $exit_code
fi
```

---

## GENRE-SPECIFIC EXAMPLES

### 18. Genre-specific book creation

**Fantasy novel with worldbuilding:**

```bash
hatch run python -m libriscribe2.main create-book \
    --title="The Dragon's Quest" \
    --genre=fantasy \
    --description="A young hero must find the ancient dragon to save the kingdom" \
    --worldbuilding \
    --characters=4 \
    --target-audience="Young Adult" \
    --all
```

**Mystery novel:**

```bash
hatch run python -m libriscribe2.main create-book \
    --title="The Missing Heir" \
    --genre=mystery \
    --description="A detective investigates the disappearance of a wealthy family's heir" \
    --characters=3-5 \
    --target-audience="Adult" \
    --all
```

**Romance novella:**

```bash
hatch run python -m libriscribe2.main create-book \
    --project-type=novella \
    --title="Summer Love" \
    --genre=romance \
    --description="Two strangers meet during a summer vacation and find unexpected love" \
    --characters=2-4 \
    --target-audience="Adult" \
    --all
```

**Horror short story:**

```bash
hatch run python -m libriscribe2.main create-book \
    --project-type=short_story \
    --title="The Haunted House" \
    --genre=horror \
    --description="A family moves into a house with a dark secret" \
    --characters=3 \
    --target-audience="Adult" \
    --all
```

**Science fiction epic:**

```bash
hatch run python -m libriscribe2.main create-book \
    --project-type=epic \
    --title="Galactic Empire" \
    --genre=sci-fi \
    --description="A rebellion fights against an oppressive galactic empire" \
    --worldbuilding \
    --characters=6-10 \
    --target-audience="Adult" \
    --all
```

---

## HELP AND VERSION EXAMPLES

### 19. Getting help and version information

```bash
# Show version
hatch run python -m libriscribe2.main --version
# Show general help
hatch run python -m libriscribe2.main --help
# Show help for specific command
hatch run python -m libriscribe2.main create-book --help
hatch run python -m libriscribe2.main book-stats --help
hatch run python -m libriscribe2.main generate-title --help
```

---

## ADVANCED INTERACTIVE COMMANDS (EXPERIMENTAL)

### 20. Interactive commands (ADVANCED - LIMITED SUPPORT)

```bash
# Start interactive mode (not fully implemented)
hatch run python -m libriscribe2.main start
# Generate concept for existing project (not implemented)
hatch run python -m libriscribe2.main concept --project-name my_book
# Generate outline for existing project (not implemented)
hatch run python -m libriscribe2.main outline --project-name my_book
# Generate characters for existing project (not implemented)
hatch run python -m libriscribe2.main characters --project-name my_book
# Generate worldbuilding for existing project (not implemented)
hatch run python -m libriscribe2.main worldbuilding --project-name my_book
# Write specific chapter (not implemented)
hatch run python -m libriscribe2.main write --project-name my_book --chapter-number 1
# Edit specific chapter (not implemented)
hatch run python -m libriscribe2.main edit --project-name my_book --chapter-number 1
# Format book (partially implemented)
hatch run python -m libriscribe2.main format --project-name my_book
# Research functionality (not implemented)
hatch run python -m libriscribe2.main research --query "medieval castles"
```

---

## PRACTICAL WORKFLOW EXAMPLES

### 21. Complete workflow examples

#### Workflow 1: Quick test book creation

```bash
# 1. Create a test book with mock mode
hatch run python -m libriscribe2.main create-book \
    --project-type=short_story \
    --genre=fantasy \
    --auto-title \
    --mock \
    --all
# 2. View the results
hatch run python -m libriscribe2.main book-stats --project-name "untitled-book-*"
```

#### Workflow 2: Production book creation

```bash
# 1. Create book with specific requirements
hatch run python -m libriscribe2.main create-book \
    --title="The Chronicles of Aethermoor" \
    --genre=fantasy \
    --description="An epic tale of magic, adventure, and destiny in the realm of Aethermoor" \
    --project-type=novel \
    --worldbuilding \
    --characters=5 \
    --target-audience="Young Adult" \
    --config-file=production-config.json \
    --user="author-001" \
    --all
# 2. Check the results
hatch run python -m libriscribe2.main book-stats --project-name "the-chronicles-of-aethermoor"
# 3. Generate a better title if needed
hatch run python -m libriscribe2.main generate-title --project-name "the-chronicles-of-aethermoor"
```

#### Workflow 3: Iterative development

```bash
# 1. Start with concept and outline
hatch run python -m libriscribe2.main create-book \
    --title="Work in Progress" \
    --genre=mystery \
    --generate-concept \
    --generate-outline
# 2. Add characters
hatch run python -m libriscribe2.main create-book \
    --title="Work in Progress" \
    --characters=4 \
    --generate-characters
# 3. Write chapters
hatch run python -m libriscribe2.main create-book \
    --title="Work in Progress" \
    --write-chapters
# 4. Format final book
hatch run python -m libriscribe2.main create-book \
    --title="Work in Progress" \
    --format-book
# 5. Check final results
hatch run python -m libriscribe2.main book-stats --project-name "work-in-progress"
```

---

## TROUBLESHOOTING EXAMPLES

### 22. Common troubleshooting scenarios

```bash
# Check if project exists
ls projects/
# View project structure
ls projects/my-project-name/
# Check log files
cat projects/my-project-name/book_creation.log
# View application logs
ls logs/
cat logs/libriscribe_*.log
# Test with mock mode if API issues
hatch run python -m libriscribe2.main create-book \
    --title="Test Book" \
    --mock \
    --all
# Check configuration
cat config-example.json  # Copy to config.json and customize
cat .env
# Verify dependencies
hatch run pip list
```

---

## CONFIGURATION FILE EXAMPLES

### 23. Example configuration files

**config-example.json (copy to config.json and customize):**

```json
{
    "openai_api_key": "your-api-key-here",
    "openai_base_url": "https://api.openai.com/v1",
    "default_model": "gpt-4o-mini",
    "models": {
        "concept": "gpt-4o",
        "outline": "gpt-4o",
        "characters": "gpt-4o-mini",
        "worldbuilding": "gpt-4o",
        "chapter": "gpt-4o-mini",
        "formatting": "gpt-4o-mini"
    },
    "projects_dir": "projects",
    "log_level": "INFO"
}
```

**.env example:**

```env
OPENAI_API_KEY=your-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
DEFAULT_MODEL=gpt-4o-mini
PROJECTS_DIR=projects
LOG_LEVEL=INFO
```

**config.yaml example:**

```yaml
openai_api_key: your-api-key-here
openai_base_url: https://api.openai.com/v1
default_model: gpt-4o-mini
models:
  concept: gpt-4o
  outline: gpt-4o
  characters: gpt-4o-mini
  worldbuilding: gpt-4o
  chapter: gpt-4o-mini
  formatting: gpt-4o-mini
projects_dir: projects
log_level: INFO
```

---

## PERFORMANCE AND OPTIMIZATION EXAMPLES

### 24. Performance optimization examples

**Use appropriate models for different tasks:**

```bash
hatch run python -m libriscribe2.main create-book \
    --title="Optimized Book" \
    --config-file=optimized-config.json \
    --all
```

**Batch operations for multiple books:**

```bash
#!/bin/bash
for genre in fantasy mystery romance sci-fi horror; do
    hatch run python -m libriscribe2.main create-book \
        --project-type=short_story \
        --genre=$genre \
        --auto-title \
        --mock \
        --all
done
```

**Monitor resource usage:**

```bash
time hatch run python -m libriscribe2.main create-book \
    --title="Performance Test" \
    --all
```
