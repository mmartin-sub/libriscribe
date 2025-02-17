# src/libriscribe/utils/prompts_context.py

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
* A breakdown of scenes, with each scene having:
    * A number
    * A short summary
    * Characters Involved
    * Setting
    * Goal (What's the purpose of this scene)
    * Emotional Beat

Return the outline in Markdown format.  Make it very detailed.
"""

PARAGRAPH_PLAN_PROMPT = """
Create a paragraph-by-paragraph plan for a chapter titled "{chapter_title}" of a {genre} book.

Chapter Summary:
{chapter_summary}

Scenes:
{scenes}

Characters:
{characters}

Worldbuilding:
{worldbuilding}

Instructions:
- Outline the content of each paragraph in the chapter.
- Indicate which scene each paragraph belongs to (if applicable).
- Focus on the flow of information and how each paragraph contributes to the overall chapter goals.
- Be concise but clear.

Return a JSON array where each element is a dictionary with the following keys:
- "paragraph_number": (int) The number of the paragraph within the chapter.
- "scene_number": (int, optional) The scene number this paragraph belongs to.  If it doesn't belong to a specific scene, omit this key.
- "summary": (str) A brief summary of the paragraph's content.

Example:
```json
[
    {{"paragraph_number": 1, "scene_number": 1, "summary": "Introduce the protagonist, Sarah, and her ordinary life in a small town."}},
    {{"paragraph_number": 2, "scene_number": 1, "summary": "Describe Sarah's morning routine and her job at the local library."}},
    {{"paragraph_number": 3, "summary": "Transition to the inciting incident - a mysterious letter arrives for Sarah."}}
]
"""

CHAPTER_PROMPT = """
Write chapter {chapter_number} of a {genre} book titled "{book_title}" which is categorized as {category}.

Chapter Title: {chapter_title}

Outline:
{outline}

Chapter Summary:
{chapter_summary}

Scenes:
{scenes}

Characters:
{characters}

Worldbuilding:
{worldbuilding}

Paragraph Plan:
{paragraph_plan}

Instructions:

Write the chapter in a compelling and engaging style, appropriate for the genre and category.

Maintain consistency with previous chapters (if applicable).

Focus on advancing the plot, developing characters, and building the world.

Include dialogue, descriptions, and internal monologues as appropriate.

Use the paragraph plan as a guide, but feel free to expand on it and add creative details.

Aim for approximately 1500-2000 words, unless specified otherwise.

Ensure smooth transitions between scenes.

Pay attention to pacing and emotional impact.

Conclude the chapter with a satisfying resolution or a compelling cliffhanger, as appropriate for the overall story arc.
"""

OUTLINE_PROMPT = """
Create a structured outline for a {genre} book titled "{title}" which is categorized as {category}.

Description: {description}

IMPORTANT: Format your response EXACTLY as shown below, with consistent header formatting and numbering:

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

Focus on the following aspects, as relevant to the genre and description. Provide EXTENSIVE detail. Output in JSON format.

{worldbuilding_aspects}

Return the worldbuilding details in JSON format. Be thorough and imaginative.
"""

WORLDBUILDING_ASPECTS = {
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
EDITOR_PROMPT = """
You are an expert editor tasked with refining and improving a chapter of a {genre} book titled "{book_title}".

Chapter {chapter_number}: {chapter_title}

Here is the chapter content:
{chapter_content}
Instructions:

Content and Structure:

Evaluate the chapter's overall structure, pacing, and clarity.

Ensure the chapter advances the plot and contributes to the overall story arc.

Identify any plot holes, inconsistencies, or confusing elements.

Suggest improvements to scene transitions, character interactions, and dialogue.

Check if the chapter's beginning grabs the reader's attention and if the ending leaves a lasting impression.

Style and Tone:

Assess the writing style and tone for consistency with the genre, target audience, and the rest of the book.

Identify any instances of passive voice, repetitive sentence structures, or weak verbs.

Suggest improvements to word choice, sentence variety, and overall flow.

Enhance the descriptive language to create vivid imagery and engage the reader's senses.

Character Development:

Evaluate the portrayal of characters within the chapter.

Ensure their actions, dialogue, and thoughts are consistent with their established personalities and motivations.

Suggest enhancements to character development, revealing their inner conflicts, growth, and relationships.

Worldbuilding (if applicable):

Check for consistency with the established worldbuilding rules and details.

Suggest improvements to integrate the worldbuilding elements seamlessly into the narrative.

Grammar and Mechanics:

Correct any grammatical errors, spelling mistakes, punctuation issues, and typos.

Ensure proper formatting and adherence to style guidelines.

Fact-Checking and Consistency

Verify all names, and places

Make sure every sentence is consistent

Output:

Provide DETAILED feedback and suggestions for improvement in Markdown format, including:

Summary of Overall Assessment: A brief overview of the chapter's strengths and weaknesses.

Specific Suggestions: Numbered list of specific suggestions, referencing line numbers or sections where possible. Include explanations for each suggestion.

Revised Chapter: The complete, revised chapter with your edits and improvements incorporated. Use Markdown formatting.

Example Output Structure:
## Chapter Editing Report - Chapter {chapter_number}

**Summary of Overall Assessment:**

The chapter has a good foundation, but the pacing feels rushed in the middle section.  The dialogue between [Character A] and [Character B] could be more engaging.  There are a few minor inconsistencies with [Worldbuilding Element].

**Specific Suggestions:**

1.  **Line 12:**  "The sun was setting."  ->  "Crimson and gold bled across the horizon as the sun dipped below the jagged peaks." (Enhance descriptive language)
2.  **Lines 45-50:** The conversation between [Character A] and [Character B] feels flat.  Consider adding more conflict or revealing more about their individual motivations.
3.  **Line 78:**  "[Worldbuilding Element] is mentioned, but it contradicts the description in Chapter 2."  ->  "Ensure consistency with the established rules of [Worldbuilding Element]."
4. **Lines 101-110**: Pacing is rushed, add a little more to make it perfect

**Revised Chapter:**

[The full revised chapter content, with changes implemented, formatted in Markdown]
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