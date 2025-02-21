# src/libriscribe/utils/prompts_context.py

def get_worldbuilding_aspects(category: str) -> str:
    """Dynamically returns worldbuilding aspects based on the project category."""
    category = category.lower()
    if category == "fiction":
        return """
Geography: (Detailed descriptions of the land, climate, significant locations)
Culture and Society: (Customs, traditions, social structures, values, beliefs)
History: (A comprehensive timeline of major events, eras, and turning points)
Rules and Laws: (The legal system, governing bodies, enforcement)
Technology Level: (Specific technologies and their impact on society)
Magic System: (If applicable: rules, limitations, sources, consequences)
Key Locations: (Detailed descriptions of important cities, towns, landmarks)
Important Organizations or Groups: (Their goals, influence, membership)
Flora and Fauna: (Unique plants and animals, their roles in the ecosystem)
Languages: (If applicable: names, origins, basic structure)
Religions and Beliefs: (Deities, rituals, creation myths, afterlife beliefs)
Economy: (Trade, currency, resources, economic systems)
Conflicts: (Past and present wars, rivalries, political tensions)
"""
    elif category == "non-fiction":
        return """
Setting/Context: (The time period, location, and relevant background)
Key Figures: (Important individuals and their roles)
Major Events: (Timeline of significant happenings)
Underlying Causes: (Factors contributing to the events or situation)
Consequences: (Short-term and long-term effects)
Relevant Data/Statistics: (Supporting evidence and information)
Different Perspectives: (Varying viewpoints on the topic)
Key Concepts/Ideas: (Central themes and principles)
"""
    elif category == "business":
        return """
Industry Overview: (Current state of the industry, trends, major players)
Target Audience: (Detailed demographics, needs, and behaviors)
Market Analysis: (Competition, market size, growth potential)
Business Model: (How the business creates, delivers, and captures value)
Marketing and Sales Strategy: (How the business reaches and converts customers)
Operations: (Day-to-day processes, logistics, supply chain)
Financial Projections: (Revenue, expenses, profitability, funding needs)
Management Team: (Key personnel, their experience, and roles)
Legal and Regulatory Environment: (Relevant laws, regulations, compliance)
Risks and Challenges: (Potential obstacles and mitigation strategies)
Opportunities for Growth: (Expansion plans, new markets, product development)
"""
    elif category == "research paper":
        return """
Introduction: (Background information, research question, hypothesis)
Literature Review: (Summary of existing research on the topic)
Methodology: (Research design, data collection methods, participants)
Results: (Presentation of findings, data analysis)
Discussion: (Interpretation of results, implications, limitations)
Conclusion: (Summary of key findings, future research directions)
References: (List of sources cited)
Appendices: (Supplementary materials, raw data, questionnaires)
"""
    else:
        return ""  # Return empty string for unknown categories

WORLDBUILDING_ASPECTS = { #Keep like this, so we can access it in outliner
"fiction": """

Geography: (Detailed descriptions of the land, climate, significant locations)

Culture and Society: (Customs, traditions, social structures, values, beliefs)

History: (A comprehensive timeline of major events, eras, and turning points)

Rules and Laws: (The legal system, governing bodies, enforcement)

Technology Level: (Specific technologies and their impact on society)

Magic System: (If applicable: rules, limitations, sources, consequences)

Key Locations: (Detailed descriptions of important cities, towns, landmarks)

Important Organizations or Groups: (Their goals, influence, membership)

Flora and Fauna: (Unique plants and animals, their roles in the ecosystem)

Languages: (If applicable: names, origins, basic structure)

Religions and Beliefs: (Deities, rituals, creation myths, afterlife beliefs)

Economy: (Trade, currency, resources, economic systems)

Conflicts: (Past and present wars, rivalries, political tensions)
""",
"non-fiction": """

Setting/Context: (The time period, location, and relevant background)

Key Figures: (Important individuals and their roles)

Major Events: (Timeline of significant happenings)

Underlying Causes: (Factors contributing to the events or situation)

Consequences: (Short-term and long-term effects)

Relevant Data/Statistics: (Supporting evidence and information)

Different Perspectives: (Varying viewpoints on the topic)

Key Concepts/Ideas: (Central themes and principles)
""",
"business": """

Industry Overview: (Current state of the industry, trends, major players)

Target Audience: (Detailed demographics, needs, and behaviors)

Market Analysis: (Competition, market size, growth potential)

Business Model: (How the business creates, delivers, and captures value)

Marketing and Sales Strategy: (How the business reaches and converts customers)

Operations: (Day-to-day processes, logistics, supply chain)

Financial Projections: (Revenue, expenses, profitability, funding needs)

Management Team: (Key personnel, their experience, and roles)

Legal and Regulatory Environment: (Relevant laws, regulations, compliance)

Risks and Challenges: (Potential obstacles and mitigation strategies)

Opportunities for Growth: (Expansion plans, new markets, product development)
""",
"research paper": """

Introduction: (Background information, research question, hypothesis)

Literature Review: (Summary of existing research on the topic)

Methodology: (Research design, data collection methods, participants)

Results: (Presentation of findings, data analysis)

Discussion: (Interpretation of results, implications, limitations)

Conclusion: (Summary of key findings, future research directions)

References: (List of sources cited)

Appendices: (Supplementary materials, raw data, questionnaires)
"""
}

# --- Prompts ---
# Modified outline
SCENE_OUTLINE_PROMPT = """
Create a detailed outline for a {genre} book titled "{title}" which is categorized as {category}.

Description: {description}

The outline should include:
* A brief summary of the entire book.
* A breakdown of chapters, with each chapter having:
    * A title.
    * A short summary of the events in the chapter.
    * Aim for a relatively consistent number of scenes per chapter (around 3-6 scenes, depending on the chapter's length and complexity).  Do not create excessively long or short chapters.
* A breakdown of scenes, each scene need to have:
    * The number of the scene
    * A short summary
    * Characters Involved
    * Setting
    * Goal (What's the purpose of this scene)
    * Emotional Beat

Return the outline in Markdown format.  Make it very detailed.
"""


OUTLINE_PROMPT = """
Create a structured outline for a {genre} book titled "{title}" which is categorized as {category}.

Description: {description}

IMPORTANT: Format your response EXACTLY as shown below, with consistent header formatting and numbering:
If there's a book length: ({book_length}), adjust the number of chapters accordingly.
# Book Summary
[Write a brief summary of the entire book here, 2-3 paragraphs]

# Chapter List
[Total number of chapters, definitively stated. NO optional chapters.]

# Chapter Details

## Chapter 1: [Chapter Title]
### Summary
[Detailed chapter summary, 1-2 paragraphs]

### Key Events
- [Event 1]
- [Event 2]
- [Event 3]

[Repeat the Chapter structure for each chapter, maintaining EXACT same formatting]

Note: For short stories, use 1-2 chapters. For novellas, use 5-10 chapters. For novels, use 10+ chapters.
Return the outline using this EXACT Markdown structure. Do not include any optional or conditional chapters.
"""

CHARACTER_PROMPT = """
Create detailed character profiles for a {genre} book titled "{title}" which is categorized as {category}.

Book Description: {description}

The book requires the following number of main characters: {num_characters}

For EACH character, include the following in the profile (return as a JSON array of character objects):

Name: (Suggest a suitable name)

Age:

Physical Description: (Detailed, including appearance, clothing style, etc.)

Personality Traits: (At least 5 distinct traits)

Background/Backstory: (Detailed, explaining their past and how it shapes them)

Motivations: (What drives them? What are their goals?)

Relationships with other characters: (Describe their connections to other characters, creating new characters if necessary to complete the story.)

Role in the story: (Protagonist, antagonist, supporting character, etc.)

Internal Conflicts: (What struggles do they face within themselves?)

External Conflicts: (What external challenges do they face?)

Character Arc: (How do they change throughout the story? Provide a brief description)

Return the character profiles in JSON format.
"""

WORLDBUILDING_PROMPT = """
Create detailed worldbuilding information for a {genre} book titled "{title}" which is categorized as {category}.

Book Description: {description}

IMPORTANT: You MUST provide substantial content for EVERY field below. Do not leave any field empty.
Each field should have at least 1-2 paragraphs of detailed content relevant to this {genre} story.

{worldbuilding_aspects}

ENSURE that every field has substantial content. Do not leave any field empty or with placeholder text.
Return the worldbuilding details in valid JSON format ONLY, no markdown wrapper.
"""



EDITOR_PROMPT = """
You are an expert editor tasked with refining and improving a chapter of a {genre} book titled "{book_title}".

Chapter {chapter_number}: {chapter_title}

Here is the chapter content:
{chapter_content}

A content reviewer has provided the following feedback. MAKE SURE to address ALL issues they raised:
{review_feedback}

Instructions:

1. Fix ALL issues mentioned in the reviewer's feedback
2. Content and Structure:
- Evaluate the chapter's overall structure, pacing, and clarity.
- Ensure the chapter advances the plot and contributes to the overall story arc.
- Identify any plot holes, inconsistencies, or confusing elements.
- Suggest improvements to scene transitions, character interactions, and dialogue.

3. Style and Tone:
- Assess the writing style and tone for consistency with the genre.
- Identify any instances of passive voice, repetitive sentence structures, or weak verbs.
- Enhance the descriptive language to create vivid imagery.

4. Character Development:
- Ensure their actions, dialogue, and thoughts are consistent with their established personalities.

5. Grammar and Mechanics:
- Correct any grammatical errors, spelling mistakes, punctuation issues, and typos.

Output:

Provide the complete, revised chapter with all improvements incorporated. Use Markdown formatting.
Wrap the ENTIRE revised chapter in a Markdown code block, like this:

```markdown
[The full revised chapter content]
"""

RESEARCH_PROMPT = """
Research the following topic and provide a comprehensive summary of your findings:

Topic: {query}

Instructions:

Gather Information: Conduct thorough research using reliable sources.

Synthesize Information: Combine information from multiple sources to create a coherent and well-organized summary.

Key Findings: Identify the most important facts, data, perspectives, and conclusions related to the topic.

Structure: Organize the summary into clear sections with headings and subheadings.

Citations: Provide a list of sources used in a consistent citation style (e.g., APA, MLA, Chicago).

Summary Length: Aim for approximately 500-750 words, unless specified otherwise.

Objectivity: Present the information objectively and avoid personal opinions or biases.

Accuracy: Ensure all information is accurate and up-to-date.

Output:

Return the research summary in Markdown format, including:

Title: The research topic.

Introduction: A brief overview of the topic and its significance.

Key Findings: A detailed summary of your research, organized into logical sections.

Conclusion: A concise summary of the main points and their implications.

References: A list of sources used, formatted according to the chosen citation style.
"""

FORMATTING_PROMPT = """
Combine the provided chapters into a single, well-formatted Markdown document representing the complete book manuscript.

Chapters:
{chapters}

Instructions:

Concatenate Chapters: Combine the content of all chapters in the correct order.

Add Title Page (if information available):

If title, author, and genre are provided, create a title page at the beginning.

Use appropriate Markdown headings for title and author.

Chapter Headings: Ensure each chapter begins with a level 1 heading (#) indicating the chapter title (e.g., # Chapter 1: The Beginning).

Consistent Formatting: Maintain consistent formatting throughout the document (e.g., paragraph spacing, indentation).

Table of Contents (Optional): If requested, generate a table of contents with links to each chapter. (Note: This requires a Markdown processor that supports ToC generation). For this basic version, just list the chapter titles.

Output: Return the complete book manuscript in Markdown format.
"""

SCENE_PROMPT = """
Write Scene {scene_number} of {total_scenes} for Chapter {chapter_number}: {chapter_title} of the {genre} {category} book "{book_title}".

Chapter Summary:
{chapter_summary}

Scene Details:
- Summary: {scene_summary}
- Characters: {characters}
- Setting: {setting}
- Goal: {goal}
- Emotional Beat: {emotional_beat}

Instructions:
- Write a vivid, engaging scene that captures these elements.
- Include descriptive details and sensory information about the setting.
- Show character emotions and development through actions and dialogue.
- Advance the story according to the scene's goal and emotional beat.
- Make the scene flow naturally and avoid unnecessary exposition.
- Ensure the scene ends in a way that connects smoothly to the next scene.
- Use language and style appropriate for the genre.

Important: Focus on showing rather than telling. Create an immersive experience that brings the scene to life.
"""