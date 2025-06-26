import os
from datetime import datetime
import yaml

def generate_yaml_metadata(project_knowledge_base):
    """Generate a YAML metadata block from the project knowledge base, using defaults if available."""
    # --- Load defaults from default.yaml if present ---
    defaults = {}
    default_yaml_path = None
    if hasattr(project_knowledge_base, "project_dir") and project_knowledge_base.project_dir:
        default_yaml_path = os.path.join(project_knowledge_base.project_dir, "default.yaml")
        if os.path.isfile(default_yaml_path):
            with open(default_yaml_path, "r", encoding="utf-8") as f:
                defaults = yaml.safe_load(f) or {}

    # --- Required fields with project values taking precedence over defaults ---
    def get_field(key, fallback=None):
        return getattr(project_knowledge_base, key, None) or project_knowledge_base.get(key, None) or defaults.get(key, fallback)

    title = get_field("title", "Untitled")
    author = get_field("author", "Unknown Author")
    language = get_field("language")
    abstract = get_field("description", "")
    genre = get_field("genre", "")
    date = get_field("date") or defaults.get("date") or datetime.now().strftime("%Y-%m-%d")

    # --- Optional: cover image ---
    cover_image = None
    if hasattr(project_knowledge_base, "project_dir") and project_knowledge_base.project_dir:
        for ext in ["jpg", "jpeg", "png"]:
            candidate = os.path.join(project_knowledge_base.project_dir, f"cover.{ext}")
            if os.path.isfile(candidate):
                cover_image = f"cover.{ext}"
                break
    if not cover_image:
        cover_image = defaults.get("cover-image")

    # --- Generate keywords (merge with defaults if present) ---
    stopwords = {"the", "a", "an", "of", "and", "in", "on", "for", "to", "de", "la", "le", "et", "du", "des"}
    keywords = set(defaults.get("keywords", []))
    for word in (str(title) + " " + str(genre)).lower().replace("'", " ").replace(":", " ").split():
        if word not in stopwords and len(word) > 2:
            keywords.add(word)
    if isinstance(author, str):
        keywords.add(author.lower())
    keywords = sorted(keywords)

    # --- Eisvogel/Pandoc-specific fields ---
    subtitle = get_field("subtitle")
    publisher = get_field("publisher")
    isbn = get_field("isbn")
    rights = get_field("rights")
    toc = defaults.get("toc", True)
    toc_title = defaults.get("toc-title", "Table des Matières")
    toc_own_page = defaults.get("toc-own-page", True)
    lof = defaults.get("lof", False)
    lot = defaults.get("lot", False)
    colorlinks = defaults.get("colorlinks", True)
    linkcolor = defaults.get("linkcolor", "blue")
    mainfont = defaults.get("mainfont", "Linux Libertine O")
    sansfont = defaults.get("sansfont", "Linux Biolinum O")
    monofont = defaults.get("monofont", "Fira Mono")
    fontsize = defaults.get("fontsize", "12pt")
    geometry = defaults.get("geometry", "margin=2.5cm")
    header_includes = defaults.get("header-includes", [
        "\\usepackage{microtype}",
        "\\usepackage{csquotes}"
    ])

    # --- YAML construction ---
    metadata = {
        "title": title,
        "subtitle": subtitle,
        "author": author,
        "date": date,
        "lang": language,
        "abstract": abstract,
        "genre": genre,
        "cover-image": cover_image,
        "keywords": keywords,
        "publisher": publisher,
        "isbn": isbn,
        "rights": rights,
        "toc": toc,
        "toc-title": toc_title,
        "toc-own-page": toc_own_page,
        "lof": lof,
        "lot": lot,
        "colorlinks": colorlinks,
        "linkcolor": linkcolor,
        "mainfont": mainfont,
        "sansfont": sansfont,
        "monofont": monofont,
        "fontsize": fontsize,
        "geometry": geometry,
        "header-includes": header_includes,
    }
    # Remove None or empty values
    metadata = {k: v for k, v in metadata.items() if v not in [None, "", []]}
    yaml_block = "---\n" + yaml.safe_dump(metadata, sort_keys=False, allow_unicode=True)