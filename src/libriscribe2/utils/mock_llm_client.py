# src/libriscribe2/utils/mock_llm_client.py

import json
import logging
import re
import secrets
from typing import ClassVar, TypedDict

from ..settings import Settings


class MockConfig(TypedDict):
    scene_length: dict[str, int]
    chapter_length: dict[str, int]
    lorem_ipsum_words: list[str]


logger = logging.getLogger(__name__)


class MockLLMClient:
    """
    A mock LLM client for testing purposes.
    Returns deterministic responses based on prompt type or a default.
    """

    # Mock configuration settings
    # Mark as a shared, intentional class variable
    MOCK_CONFIG: ClassVar[MockConfig] = {
        "scene_length": {
            # Target ~4000-5000 characters per scene (~700-900 words)
            "min_words": 700,
            "max_words": 900,
        },
        "chapter_length": {
            "min_words": 800,
            "max_words": 1500,
        },
        "lorem_ipsum_words": [
            "lorem",
            "ipsum",
            "dolor",
            "sit",
            "amet",
            "consectetur",
            "adipiscing",
            "elit",
            "sed",
            "do",
            "eiusmod",
            "tempor",
            "incididunt",
            "ut",
            "labore",
            "et",
            "dolore",
            "magna",
            "aliqua",
            "ut",
            "enim",
            "ad",
            "minim",
            "veniam",
            "quis",
            "nostrud",
            "exercitation",
            "ullamco",
            "laboris",
            "nisi",
            "ut",
            "aliquip",
            "ex",
            "ea",
            "commodo",
            "consequat",
            "duis",
            "aute",
            "irure",
            "dolor",
            "in",
            "reprehenderit",
            "voluptate",
            "velit",
            "esse",
            "cillum",
            "dolore",
            "eu",
            "fugiat",
            "nulla",
            "pariatur",
            "excepteur",
            "sint",
            "occaecat",
            "cupidatat",
            "non",
            "proident",
            "sunt",
            "culpa",
            "qui",
            "officia",
            "deserunt",
            "mollit",
            "anim",
            "id",
            "est",
            "laborum",
            "et",
            "dolore",
            "magna",
            "aliqua",
            "ut",
            "enim",
            "ad",
            "minim",
            "veniam",
            "quis",
            "nostrud",
            "exercitation",
            "ullamco",
            "laboris",
            "nisi",
            "ut",
            "aliquip",
            "ex",
            "ea",
            "commodo",
            "consequat",
            "duis",
            "aute",
            "irure",
            "dolor",
            "in",
            "reprehenderit",
            "voluptate",
            "velit",
            "esse",
            "cillum",
            "dolore",
            "eu",
            "fugiat",
            "nulla",
            "pariatur",
            "excepteur",
            "sint",
            "occaecat",
            "cupidatat",
            "non",
            "proident",
            "sunt",
            "culpa",
            "qui",
            "officia",
            "deserunt",
            "mollit",
            "anim",
            "id",
            "est",
            "laborum",
        ],
    }

    def __init__(
        self,
        llm_provider: str = "mock",
        model_config: dict[str, str] | None = None,
        settings: Settings | None = None,
        project_name: str = "",
        user: str | None = None,
        mock_config: MockConfig | None = None,
    ):
        self.llm_provider = llm_provider
        self.settings = settings or Settings()
        self.model_config = model_config if model_config is not None else {}
        self.default_model = self.model_config.get("default", "mock-model")
        self.environment = self.settings.default_environment
        self.project_name = project_name
        self.user = user

        # Merge mock configuration with defaults
        self.mock_config: MockConfig = self.MOCK_CONFIG.copy()
        if mock_config:
            self.mock_config.update(mock_config)

        # Sanitize provider name for logging to prevent log injection
        safe_provider = str(self.llm_provider).replace("\n", "").replace("\r", "")[:50]
        logger.info(f"Initialized MockLLMClient with provider: {safe_provider}")

        # Log LiteLLM metadata in DEBUG mode
        logger.debug(
            f"MockLLMClient LiteLLM metadata: environment={self.environment}, project={self.project_name}, user={self.user}"
        )

    def _generate_lorem_ipsum(self, min_words: int, max_words: int) -> str:
        """
        Generate lorem ipsum text with cryptographically secure random length between min_words and max_words.
        Creates realistic-looking content for mock scenes and chapters.
        """
        word_count = secrets.randbelow(max_words - min_words + 1) + min_words
        words = list(self.mock_config["lorem_ipsum_words"])

        # Generate paragraphs with realistic structure
        paragraphs = []
        remaining_words = word_count

        while remaining_words > 0:
            # Each paragraph has 20-50 words
            para_length = min(secrets.randbelow(31) + 20, remaining_words)  # 20-50 range
            paragraph_words: list[str] = []

            for _ in range(para_length):
                word: str = secrets.choice(words)
                # Capitalize first word of paragraph
                if not paragraph_words:
                    word = word.capitalize()
                paragraph_words.append(word)

            # Add some variety with punctuation
            if secrets.randbelow(100) < 30:  # 30% chance
                paragraph_words.append(".")
            elif secrets.randbelow(100) < 20:  # 20% chance
                paragraph_words.append("!")
            else:
                paragraph_words.append(".")

            paragraph = " ".join(paragraph_words)
            paragraphs.append(paragraph)
            remaining_words -= para_length

        return " ".join(paragraphs)

    def update_mock_config(self, new_config: MockConfig) -> None:
        """
        Update mock configuration settings.
        Useful for testing different content lengths and styles.
        """
        self.mock_config.update(new_config)
        logger.debug(f"Updated mock config: {new_config}")

    def _extract_requested_characters_from_prompt(self, prompt: str) -> int:
        """
        Try to extract the requested number of characters from the prompt text.

        Looks for common patterns like:
        - "num_characters: 8" or "num_characters=8"
        - "Generate 8 characters" / "Create 8 character profiles"
        Falls back to 3 if nothing is found.
        """
        try:
            # Most explicit: num_characters field
            m = re.search(r"num_characters\s*[:=]\s*(\d+)", prompt, re.IGNORECASE)
            if m:
                val = int(m.group(1))
                if 1 <= val <= 50:
                    return val

            # Phrasal patterns
            patterns = [
                # e.g. "Generate 8 characters"
                r"\b(?:generate|create|produce)\s+(\d+)\s+(?:characters|character\s+profiles?)\b",
                # e.g. "8 characters" or "8 character profiles"
                r"\b(\d+)\s+(?:main\s+)?(?:characters|character\s+profiles?)\b",
                # e.g. "number of characters: 8" or "number of main characters: 8"
                r"number\s+of\s+(?:main\s+)?characters\s*[:=]?\s*(\d+)",
                # e.g. "requires 8 characters" / "need 8 main characters"
                r"\b(?:require|requires|need|needs)\s+(\d+)\s+(?:main\s+)?characters\b",
                # e.g. "requires the following number of main characters: 8"
                r"\brequires\s+the\s+following\s+number\s+of\s+(?:main\s+)?characters\s*[:=]?\s*(\d+)",
            ]
            for pat in patterns:
                m2 = re.search(pat, prompt, re.IGNORECASE)
                if m2:
                    val = int(m2.group(1))
                    if 1 <= val <= 50:
                        return val
        except ValueError as e:
            logger.debug("Failed to parse requested character count: %s", e)

        # Sensible default if unspecified
        return 3

    def get_mock_config(self) -> MockConfig:
        """Get current mock configuration settings."""
        return self.mock_config.copy()

    def get_model_for_prompt_type(self, prompt_type: str) -> str:
        """Gets the specific model for a given prompt type, falling back to default."""
        return self.model_config.get(prompt_type, self.default_model)

    async def generate_content(
        self,
        prompt: str,
        prompt_type: str = "default",
        temperature: float | None = None,
        language: str | None = None,
        timeout: int | None = None,
    ) -> str:
        """
        Generates mock content based on the prompt type.
        """
        temperature = temperature or self.settings.default_temperature
        language = language or self.settings.default_language
        model_to_use = self.get_model_for_prompt_type(prompt_type)
        logger.debug(f"MockLLMClient: Generating content for prompt_type={prompt_type}, model={model_to_use}")

        # Simple deterministic responses based on prompt_type
        if prompt_type == "questions":
            return """
            {
                "q1": "Mock question 1?",
                "q2": "Mock question 2?",
                "q3": "Mock question 3?"
            }
            """
        elif prompt_type == "concept":
            return """
            ```json
            {
                "title": "Mock Concept Title",
                "logline": "A mock logline for a mock book.",
                "description": "This is a mock description of a mock book concept, generated by the mock LLM client."
            }
            ```
            """
        elif prompt_type == "outline":
            return """
            # Mock Outline
            ## Chapter 1: The Beginning
            - Scene 1.1: Mock opening
            - Scene 1.2: Mock conflict introduction
            ## Chapter 2: The Middle
            - Scene 2.1: Mock rising action
            - Scene 2.2: Mock climax
            ## Chapter 3: The End
            - Scene 3.1: Mock falling action
            - Scene 3.2: Mock resolution
            """
        elif prompt_type == "scene_outline":
            return """
            Scene 1:
                * Summary: Mock scene 1 summary
                * Characters: Mock Character 1, Mock Character 2
                * Setting: Mock setting for scene 1
                * Goal: Mock goal for scene 1
                * Emotional Beat: Mock emotional beat for scene 1

            Scene 2:
                * Summary: Mock scene 2 summary
                * Characters: Mock Character 1, Mock Character 3
                * Setting: Mock setting for scene 2
                * Goal: Mock goal for scene 2
                * Emotional Beat: Mock emotional beat for scene 2

            Scene 3:
                * Summary: Mock scene 3 summary
                * Characters: Mock Character 2, Mock Character 3
                * Setting: Mock setting for scene 3
                * Goal: Mock goal for scene 3
                * Emotional Beat: Mock emotional beat for scene 3
            """
        elif prompt_type == "character":
            # Generate language-appropriate character content, honoring requested count
            count = self._extract_requested_characters_from_prompt(prompt)
            entries = []
            lang = language.lower()

            for i in range(1, count + 1):
                if lang == "french":
                    name = f"Personnage Fictif {i}"
                    age = "25" if i % 2 else "23"
                    physical = (
                        "Un jeune homme aux cheveux bruns et aux yeux verts."
                        if i % 2
                        else "Une jeune femme aux cheveux roux et aux yeux bleus."
                    )
                    traits = (
                        "Courageux, Loyal, Impulsif, Intelligent, Compatissant"
                        if i % 2
                        else "Sage, Curieuse, Déterminée, Créative, Empathique"
                    )
                    background = (
                        "Né dans une famille modeste, a toujours rêvé d'aventure."
                        if i % 2
                        else "Étudiante en histoire, passionnée par les légendes anciennes."
                    )
                    motivations = (
                        "Protéger sa famille et découvrir de nouveaux horizons."
                        if i % 2
                        else "Découvrir la vérité cachée derrière les mystères du village."
                    )
                    relationships = (
                        "Ami fidèle et mentor de jeunes aventuriers."
                        if i % 2
                        else "Meilleure amie et guide spirituel du groupe."
                    )
                    role = "Protagoniste principal" if i % 2 else "Protagoniste secondaire"
                    internal = (
                        "Doute entre sécurité familiale et appel de l'aventure."
                        if i % 2
                        else "Conflit entre connaissances académiques et expériences mystiques."
                    )
                    external = (
                        "Affronte des forces mystérieuses qui menacent son village."
                        if i % 2
                        else "Fait face au scepticisme de la communauté académique."
                    )
                    arc = (
                        "Évolue d'un jeune homme timide vers un héros confiant."
                        if i % 2
                        else "Se transforme d'une académique sceptique en croyante en la magie."
                    )
                elif lang == "spanish":
                    name = f"Personaje Ficticio {i}"
                    age = "25" if i % 2 else "23"
                    physical = (
                        "Un joven de cabello castaño y ojos verdes."
                        if i % 2
                        else "Una joven de cabello rojo y ojos azules."
                    )
                    traits = (
                        "Valiente, Leal, Impulsivo, Inteligente, Compasivo"
                        if i % 2
                        else "Sabia, Curiosa, Determinada, Creativa, Empática"
                    )
                    background = (
                        "Nacido en una familia humilde, siempre soñó con aventuras."
                        if i % 2
                        else "Estudiante de historia, apasionada por las leyendas antiguas."
                    )
                    motivations = (
                        "Proteger a su familia y descubrir nuevos horizontes."
                        if i % 2
                        else "Descubrir la verdad oculta detrás de los misterios del pueblo."
                    )
                    relationships = (
                        "Amigo fiel y mentor de jóvenes aventureros."
                        if i % 2
                        else "Mejor amiga y guía espiritual del grupo."
                    )
                    role = "Protagonista principal" if i % 2 else "Protagonista secundaria"
                    internal = (
                        "Duda entre la seguridad familiar y la llamada de la aventura."
                        if i % 2
                        else "Lucha entre el conocimiento académico y las experiencias místicas."
                    )
                    external = (
                        "Enfrenta fuerzas misteriosas que amenazan su pueblo."
                        if i % 2
                        else "Enfrenta el escepticismo de la comunidad académica."
                    )
                    arc = (
                        "Evoluciona de un joven tímido a un héroe confiado."
                        if i % 2
                        else "Se transforma de una académica escéptica a una creyente en la magia."
                    )
                else:
                    name = f"Mock Character {i}"
                    age = "25" if i % 2 else "23"
                    physical = (
                        "A brave mock character with brown hair and green eyes."
                        if i % 2
                        else "A wise mock character with red hair and blue eyes."
                    )
                    traits = (
                        "Brave, Loyal, Impulsive, Intelligent, Compassionate"
                        if i % 2
                        else "Wise, Curious, Determined, Creative, Empathetic"
                    )
                    background = (
                        "Born in a modest family, always dreamed of adventure."
                        if i % 2
                        else "History student, passionate about ancient legends."
                    )
                    motivations = (
                        "Protect family and discover new horizons."
                        if i % 2
                        else "Discover hidden truth behind village mysteries."
                    )
                    relationships = (
                        "Faithful friend and mentor to young adventurers."
                        if i % 2
                        else "Best friend and spiritual guide of the group."
                    )
                    role = "Main protagonist" if i % 2 else "Secondary protagonist"
                    internal = (
                        "Doubt between family safety and adventure call."
                        if i % 2
                        else "Struggle between academic knowledge and mystical experiences."
                    )
                    external = (
                        "Faces mysterious forces threatening his village."
                        if i % 2
                        else "Faces skepticism from academic community about discoveries."
                    )
                    arc = (
                        "Evolves from timid young man to confident hero."
                        if i % 2
                        else "Transforms from skeptical scholar to believer in magic."
                    )

                entries.append(
                    {
                        "name": name,
                        "age": age,
                        "physical_description": physical,
                        "personality_traits": traits,
                        "background": background,
                        "motivations": motivations,
                        "relationships": relationships,
                        "role": role,
                        "internal_conflicts": internal,
                        "external_conflicts": external,
                        "character_arc": arc,
                    }
                )

            json_block = json.dumps(entries, ensure_ascii=False, indent=4)
            return f"""
            ```json
            {json_block}
            ```
            """
        elif prompt_type == "worldbuilding":
            # Generate language-appropriate worldbuilding content
            if language.lower() == "french":
                return """
                ```json
                {
                    "geography": "Montagnes majestueuses et rivières sinueuses traversent ce paysage fantastique.",
                    "culture_and_society": "Traditions ancestrales et coutumes mystérieuses rythment la vie quotidienne."
                }
                ```
                """
            elif language.lower() == "spanish":
                return """
                ```json
                {
                    "geography": "Montañas majestuosas y ríos serpenteantes atraviesan este paisaje fantástico.",
                    "culture_and_society": "Tradiciones ancestrales y costumbres misteriosas marcan el ritmo de la vida cotidiana."
                }
                ```
                """
            else:
                return """
                ```json
                {
                    "geography": "Mock mountains and rivers.",
                    "culture_and_society": "Mock traditions and customs."
                }
                ```
                """
        elif prompt_type == "chapter":
            # Generate language-appropriate chapter content with configurable length
            min_words = self.mock_config["chapter_length"]["min_words"]
            max_words = self.mock_config["chapter_length"]["max_words"]

            if language.lower() == "french":
                content = self._generate_french_lorem_ipsum(min_words, max_words)
            elif language.lower() == "spanish":
                content = self._generate_spanish_lorem_ipsum(min_words, max_words)
            else:
                content = self._generate_lorem_ipsum(min_words, max_words)

            return f"# Chapter Content\n\n{content}"
        elif prompt_type == "scene":
            # Generate language-appropriate scene content with configurable length
            min_words = self.mock_config["scene_length"]["min_words"]
            max_words = self.mock_config["scene_length"]["max_words"]

            if language.lower() == "french":
                content = self._generate_french_lorem_ipsum(min_words, max_words)
            elif language.lower() == "spanish":
                content = self._generate_spanish_lorem_ipsum(min_words, max_words)
            else:
                content = self._generate_lorem_ipsum(min_words, max_words)

            # Prepend a markdown scene header similar to real LLM output.
            # Try to extract scene number and summary from the prompt's instruction.
            scene_num = None
            scene_title = None
            try:
                # Pattern from SCENE_TITLE_INSTRUCTION: "## Scene {scene_number}: {scene_summary}"
                m = re.search(r"##\s*Scene\s*(\d+)\s*:\s*(.+)", prompt, flags=re.IGNORECASE)
                if m:
                    scene_num = m.group(1)
                    scene_title = m.group(2).strip()
                else:
                    # Fallback: extract from the Scene Details section ("- Summary: ...")
                    m2 = re.search(r"Scene\s*Details:.*?-\s*Summary:\s*(.+)", prompt, flags=re.IGNORECASE | re.DOTALL)
                    if m2:
                        scene_title = m2.group(1).strip()
                    m3 = re.search(r"scene_number\s*[:=]\s*(\d+)", prompt, flags=re.IGNORECASE)
                    if m3:
                        scene_num = m3.group(1)
            except Exception as exc:
                # Be resilient—on any parsing issue, fall back to defaults but log for debugging
                logger.debug(
                    "Failed to parse scene metadata from prompt; using defaults. Error=%r",
                    exc,
                    exc_info=True,
                )

            if not scene_num:
                scene_num = "1"
            if not scene_title:
                scene_title = "Untitled Scene"

            header = f"## Scene {scene_num}: {scene_title}"
            return f"{header}\n\n{content}"
        elif prompt_type == "formatting":
            # Generate language-appropriate formatted book content
            min_words = self.mock_config["chapter_length"]["min_words"] * 3  # Longer for full book
            max_words = self.mock_config["chapter_length"]["max_words"] * 3

            if language.lower() == "french":
                content = self._generate_french_lorem_ipsum(min_words, max_words)
            elif language.lower() == "spanish":
                content = self._generate_spanish_lorem_ipsum(min_words, max_words)
            else:
                content = self._generate_lorem_ipsum(min_words, max_words)

            return f"# Formatted Book\n\n{content}"
        elif prompt_type == "style_editing":
            return f"This is a mock style-edited content for {prompt_type}."
        elif prompt_type == "research":
            return f"This is a mock research summary for {prompt_type}."
        elif prompt_type == "critique":
            return "Mock critique: This concept has good potential but could be improved in several areas."
        elif prompt_type == "refine":
            return """
            ```json
            {
                "title": "Mock Refined Title",
                "logline": "A mock refined logline for a mock book.",
                "description": "This is a mock refined description of a mock book concept, generated by the mock LLM client."
            }
            ```
            """
        elif prompt_type == "keywords":
            return """
            ```json
            {
                "primary_keywords": ["mock", "fantasy", "adventure"],
                "secondary_keywords": ["friendship", "courage", "magic"],
                "genre_keywords": ["epic", "quest", "heroic"]
            }
            ```
            """
        elif prompt_type == "plagiarism_check":
            return """
            ```json
            [
                {"text": "Mock plagiarized text.", "score": 0.8},
                {"text": "Mock original text.", "score": 0.1}
            ]
            ```
            """
        elif prompt_type == "fact_check":
            return """
            ```json
            [
                {"claim": "Mock claim 1.", "fact_checked": true, "evidence": "Mock evidence 1."},
                {"claim": "Mock claim 2.", "fact_checked": false, "evidence": "Mock evidence 2."}
            ]
            ```
            """
        elif prompt_type == "content_review":
            return "Mock content review: This chapter is well-written and engaging."
        else:
            return f"Mock response for prompt type: {prompt_type}. Prompt: {prompt}"

    def generate_content_with_json_repair(
        self,
        original_prompt: str,
        prompt_type: str = "default",
        temperature: float | None = None,
    ) -> str:
        """
        Generates mock content and simulates JSON repair if needed.
        For simplicity, this mock always returns valid JSON based on prompt_type.
        """
        logger.debug(f"MockLLMClient: Generating content with JSON repair for prompt_type={prompt_type}")
        # In a real mock, you might have a flag to simulate broken JSON and then repair it.
        # For now, we'll just return the valid mock content directly.
        return self.generate_content(original_prompt, prompt_type, temperature)

    def _generate_french_lorem_ipsum(self, min_words: int, max_words: int) -> str:
        """
        Generate French lorem ipsum text with cryptographically secure random length.
        Creates realistic-looking French content for mock scenes and chapters.
        """
        word_count = secrets.randbelow(max_words - min_words + 1) + min_words
        french_words = [
            "le",
            "la",
            "les",
            "un",
            "une",
            "des",
            "et",
            "ou",
            "mais",
            "donc",
            "car",
            "ni",
            "or",
            "avec",
            "sans",
            "pour",
            "par",
            "sur",
            "sous",
            "dans",
            "entre",
            "devant",
            "derrière",
            "avant",
            "après",
            "pendant",
            "depuis",
            "jusqu'à",
            "vers",
            "contre",
            "selon",
            "malgré",
            "homme",
            "femme",
            "enfant",
            "famille",
            "ami",
            "travail",
            "maison",
            "ville",
            "pays",
            "temps",
            "jour",
            "nuit",
            "matin",
            "soir",
            "année",
            "mois",
            "semaine",
            "heure",
            "grand",
            "petit",
            "beau",
            "laid",
            "bon",
            "mauvais",
            "nouveau",
            "vieux",
            "jeune",
            "vivre",
            "mourir",
            "naître",
            "grandir",
            "changer",
            "rester",
            "partir",
            "arriver",
            "penser",
            "croire",
            "savoir",
            "vouloir",
            "pouvoir",
            "devoir",
            "falloir",
            "aimer",
            "histoire",
            "aventure",
            "mystère",
            "magie",
            "héros",
            "héroïne",
            "village",
            "forêt",
            "montagne",
            "rivière",
            "mer",
            "ciel",
            "soleil",
            "lune",
            "étoile",
            "vent",
            "pluie",
        ]

        # Generate paragraphs with realistic structure
        paragraphs = []
        remaining_words = word_count

        while remaining_words > 0:
            # Each paragraph has 20-50 words
            para_length = min(secrets.randbelow(31) + 20, remaining_words)  # 20-50 range
            paragraph_words: list[str] = []

            for _ in range(para_length):
                word: str = secrets.choice(french_words)
                # Capitalize first word of paragraph
                if not paragraph_words:
                    word = word.capitalize()
                paragraph_words.append(word)

            # Add some variety with punctuation
            if secrets.randbelow(100) < 30:  # 30% chance
                paragraph_words.append(".")
            elif secrets.randbelow(100) < 20:  # 20% chance
                paragraph_words.append("!")
            else:
                paragraph_words.append(".")

            paragraph = " ".join(paragraph_words)
            paragraphs.append(paragraph)
            remaining_words -= para_length

        return "\n\n".join(paragraphs)

    def _generate_spanish_lorem_ipsum(self, min_words: int, max_words: int) -> str:
        """
        Generate Spanish lorem ipsum text with cryptographically secure random length.
        Creates realistic-looking Spanish content for mock scenes and chapters.
        """
        word_count = secrets.randbelow(max_words - min_words + 1) + min_words
        spanish_words = [
            "el",
            "la",
            "los",
            "las",
            "un",
            "una",
            "unos",
            "unas",
            "y",
            "o",
            "pero",
            "porque",
            "si",
            "con",
            "sin",
            "para",
            "por",
            "sobre",
            "bajo",
            "entre",
            "detrás",
            "delante",
            "antes",
            "después",
            "durante",
            "desde",
            "hasta",
            "hacia",
            "contra",
            "según",
            "a pesar de",
            "hombre",
            "mujer",
            "niño",
            "familia",
            "amigo",
            "trabajo",
            "casa",
            "ciudad",
            "país",
            "tiempo",
            "día",
            "noche",
            "mañana",
            "tarde",
            "año",
            "mes",
            "semana",
            "hora",
            "grande",
            "pequeño",
            "hermoso",
            "feo",
            "bueno",
            "malo",
            "nuevo",
            "viejo",
            "joven",
            "vivir",
            "morir",
            "nacer",
            "crecer",
            "cambiar",
            "quedarse",
            "partir",
            "llegar",
            "pensar",
            "creer",
            "saber",
            "querer",
            "poder",
            "deber",
            "necesitar",
            "amar",
            "historia",
            "aventura",
            "misterio",
            "magia",
            "héroe",
            "heroína",
            "pueblo",
            "bosque",
            "montaña",
            "río",
            "mar",
            "cielo",
            "sol",
            "luna",
            "estrella",
            "viento",
            "lluvia",
        ]

        # Generate paragraphs with realistic structure
        paragraphs = []
        remaining_words = word_count

        while remaining_words > 0:
            # Each paragraph has 20-50 words
            para_length = min(secrets.randbelow(31) + 20, remaining_words)  # 20-50 range
            paragraph_words: list[str] = []

            for _ in range(para_length):
                word: str = secrets.choice(spanish_words)
                # Capitalize first word of paragraph
                if not paragraph_words:
                    word = word.capitalize()
                paragraph_words.append(word)

            # Add some variety with punctuation
            if secrets.randbelow(100) < 30:  # 30% chance
                paragraph_words.append(".")
            elif secrets.randbelow(100) < 20:  # 20% chance
                paragraph_words.append("!")
            else:
                paragraph_words.append(".")

            paragraph = " ".join(paragraph_words)
            paragraphs.append(paragraph)
            remaining_words -= para_length

        return "\n\n".join(paragraphs)
