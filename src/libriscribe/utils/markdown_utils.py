import yaml

def generate_yaml_metadata(project_knowledge_base):
    """Generate a YAML metadata block from the project knowledge base."""
    metadata = {
        "title": project_knowledge_base.title,
        "subtitle": getattr(project_knowledge_base, "subtitle", None),
        "author": getattr(project_knowledge_base, "author", None),
        "date": getattr(project_knowledge_base, "date", None),
        "lang": getattr(project_knowledge_base, "language", None),
        "keywords": getattr(project_knowledge_base, "keywords", None),
        "cover-image": getattr(project_knowledge_base, "cover_image", None),
        "abstract": getattr(project_knowledge_base, "description", None),
        "publisher": getattr(project_knowledge_base, "publisher", None),
        "rights": getattr(project_knowledge_base, "rights", None),
        "subject": getattr(project_knowledge_base, "genre", None),
        "isbn": getattr(project_knowledge_base, "isbn", None),
    }
    # Remove None values
    metadata = {k: v for k, v in metadata.items() if v}
    yaml_block = "---\n" + yaml.safe_dump(metadata, sort_keys=False, allow_unicode=True) + "---\n"
    return yaml_block