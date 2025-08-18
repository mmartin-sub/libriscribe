# Title Generation Implementation

## Overview

This document outlines the implementation of automatic title generation for LibriScribe2, allowing users to create books without providing a title upfront. The title is generated based on the **full manuscript content** and metadata.

## Implementation Strategy

### Phase 1: Make Title Optional in CLI ✅

**Files Modified:**

- `src/libriscribe2/main.py`

**Changes:**

- Changed `title` parameter from required (`...`) to optional (`None`)
- Added `auto_title` flag for explicit control
- Updated help text to indicate title is optional and will be auto-generated

```python
title: str = typer.Option(None, "--title", "-t", help="Book title (optional - will be auto-generated if not provided)")
auto_title: bool = typer.Option(False, "--auto-title", help="Auto-generate title based on content (default when title not provided)")
```

### Phase 2: Handle Auto-Title in Book Creator ✅

**Files Modified:**

- `src/libriscribe2/services/book_creator.py`

**Changes:**

- Added auto-title handling logic in `create_book()` method
- Uses temporary title "Untitled Book" for project creation when no title provided
- Passes `auto_title` flag through the generation process

### Phase 3: Create Title Generator Agent ✅

**Files Created:**

- `src/libriscribe2/agents/title_generator.py`

**Features:**

- `TitleGeneratorAgent` class for generating titles based on **full manuscript content**
- Analyzes multiple content sources:
  - Book concept and logline
  - Character information
  - Worldbuilding details
  - **Full chapter content and summaries**
  - **Scene information from all chapters**
  - Keywords and metadata
- Generates compelling titles with reasoning
- Updates knowledge base with generated title

### Phase 4: Integrate Title Generation in Workflow ✅

**Files Modified:**

- `src/libriscribe2/services/book_creator.py`

**Changes:**

- Added title generation as **final step** in `_execute_generation_steps()`
- **Runs after all content is created**, especially after chapters are written
- Prefers full manuscript over just concept/outline for better title quality
- Handles errors gracefully if title generation fails

### Phase 5: Update CLI Arguments ✅

**Files Modified:**

- `src/libriscribe2/main.py`

**Changes:**

- Pass `auto_title` flag to book creator service
- Updated examples to show auto-title usage
- Updated help text to reflect new functionality

### Phase 6: Configure LLM for Title Generation ✅

**Files Modified:**

- `config.json`
- `examples/config.json`

**Changes:**

- Added `"title_generation": "gpt-4o"` to model configuration
- Uses GPT-4o for high-quality title generation
- Proper prompt_type integration with LLM client

### Phase 7: Add Resume and Standalone Title Generation ✅

**Files Modified:**

- `src/libriscribe2/knowledge_base.py`
- `src/libriscribe2/services/book_creator.py`
- `src/libriscribe2/agents/project_manager.py`
- `src/libriscribe2/main.py`

**Changes:**

- Added `auto_title` flag to `ProjectKnowledgeBase` to track auto-title setting
- Updated book creator to save auto-title flag in knowledge base
- Added `needs_title_generation()` and `generate_title()` methods to project manager
- Updated resume command to check for auto-title and generate titles when appropriate
- Added standalone `generate-title` command for existing projects

## Usage Examples

### Auto-Generate Title (Default Behavior)

```bash
# Create book with auto-generated title based on full manuscript
create-book --genre=fantasy --chapters=10 --characters=5 --worldbuilding --all --mock

# Create with custom project name and auto-title
create-book --project-name=my-custom-project --genre=fantasy --all --mock
```

### Explicit Auto-Title Control

```bash
# Explicitly enable auto-title generation
create-book --auto-title --genre=mystery --generate-concept --generate-outline --mock

# Provide specific title (overrides auto-generation)
create-book --title="My Specific Title" --genre=fantasy --all --mock
```

### Resume with Auto-Title

```bash
# Resume a project - will generate title if auto-title was enabled and content is available
resume my-project-name

# Generate title for existing project
generate-title my-project-name
```

## Title Generation Process

### 1. Content Analysis (Full Manuscript)

The title generator analyzes available content in this order:

1. **Book Concept** - Title, logline, description
2. **Character Information** - Main character names and roles
3. **Worldbuilding Elements** - Geography, culture, magic systems
4. **Full Chapter Content** - All chapters, not just first 3
5. **Scene Information** - Scene summaries from all chapters
6. **Keywords** - Genre-specific and thematic keywords
7. **Metadata** - Genre, category, language, target audience

### 2. Title Generation Criteria

- **Compelling and memorable** - Should grab reader attention
- **Genre-appropriate** - Reflects the book's genre and tone
- **Length** - Between 1-8 words
- **Avoid clichés** - Unless they serve the story well
- **Target audience appropriate** - Matches the intended readership
- **Based on full manuscript** - Not just initial concepts

### 3. Output Format

```json
{
    "title": "The generated title",
    "subtitle": "Optional subtitle (if appropriate)",
    "reasoning": "Brief explanation of why this title works"
}
```

## Technical Implementation

### Title Generation Timing

- **Trigger**: When `auto_title` is enabled AND substantial content is available
- **Timing**: **After all content generation steps**, especially after chapters are written
- **Preference**: Full manuscript over just concept/outline for better quality
- **Fallback**: Uses temporary title "Untitled Book" if no content available

### LLM Configuration

- **Model**: Uses `gpt-4o` for title generation (configured in `config.json`)
- **Prompt Type**: `title_generation` for proper model selection
- **Temperature**: 0.7 for creative but consistent results

### Error Handling

- Graceful degradation if title generation fails
- Logs warnings but doesn't stop book creation process
- Maintains temporary title if generation fails

### Knowledge Base Updates

- Updates `project_knowledge_base.title` with generated title
- Saves updated knowledge base to file
- Preserves all other metadata and content

## Benefits

### 1. **Improved User Experience**

- No need to think of title upfront
- Title is contextually appropriate to **full content**
- Reduces cognitive load during book creation

### 2. **Better Title Quality**

- Based on **actual manuscript content** rather than initial ideas
- Considers **full story arc** and character development
- Genre and audience-appropriate

### 3. **Flexibility**

- Optional feature - users can still provide specific titles
- Works with all existing workflows
- Backward compatible

### 4. **Content-Driven**

- Title reflects **complete story content**
- Adapts to changes in plot and characters throughout the book
- More accurate than pre-written titles

## Configuration

### Model Configuration

Add to your `config.json`:

```json
{
  "models": {
    "title_generation": "gpt-4o"
  }
}
```

### Usage Recommendations

- **Best Results**: Use with `--write-chapters` or `--all` for full manuscript analysis
- **Good Results**: Use with `--generate-concept --generate-outline --generate-characters`
- **Limited Results**: Use with only concept generation (less content to analyze)

## Future Enhancements

### 1. **Multiple Title Options**

- Generate 3-5 title options for user selection
- Include reasoning for each option
- Allow user to refine or regenerate

### 2. **Title Refinement**

- Allow users to provide feedback on generated titles
- Iterative improvement based on user preferences
- A/B testing for title effectiveness

### 3. **Genre-Specific Templates**

- Different title patterns for different genres
- Fantasy: "The [Noun] of [Place/Concept]"
- Mystery: "[Character] and the [Mystery]"
- Romance: "[Emotional] [Relationship]"

### 4. **Market Analysis**

- Check title availability (not already used)
- SEO-friendly title suggestions
- Market trend analysis for genre-appropriate titles

## Testing Strategy

### 1. **Unit Tests**

- Test title generation with various content types
- Verify JSON parsing and validation
- Test error handling scenarios

### 2. **Integration Tests**

- Test full workflow with auto-title enabled
- Verify knowledge base updates
- Test with different content combinations

### 3. **User Testing**

- Gather feedback on generated title quality
- Test with different genres and content types
- Validate user satisfaction with auto-generated titles

## Conclusion

The automatic title generation feature provides a significant improvement to the LibriScribe2 user experience by eliminating the need to provide a title upfront while ensuring the final title is contextually appropriate and high-quality. The implementation is robust, flexible, and maintains backward compatibility with existing workflows.

**Key Innovation**: The title generator now analyzes the **full manuscript content** rather than just initial concepts, resulting in much more accurate and compelling titles that reflect the complete story.
