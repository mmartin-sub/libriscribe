import os
from datetime import datetime
import yaml
import langcodes

class LiteralStr(str): pass

def literal_str_representer(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')

yaml.add_representer(LiteralStr, literal_str_representer)

def ensure_literal_block(val):
    """Convert multiline strings to LiteralStr for YAML block style."""
    if isinstance(val, str) and '\n' in val:
        return LiteralStr(val)
    if isinstance(val, list):
        return [ensure_literal_block(v) for v in val]
    return val

def normalize_language(lang_value):
    """Normalize language names to BCP 47 codes using langcodes."""
    if not lang_value:
        return lang_value
    try:
        # langcodes standardizes names and codes
        return langcodes.find(lang_value).to_tag()
    except Exception:
        return lang_value  # fallback to original if not recognized

def generate_yaml_metadata(project_knowledge_base):
    import copy
    # Load defaults from default.yaml
    defaults = {}
    if hasattr(project_knowledge_base, "project_dir") and project_knowledge_base.project_dir:
        default_yaml_path = os.path.join(project_knowledge_base.project_dir, "default.yaml")
        if os.path.isfile(default_yaml_path):
            with open(default_yaml_path, "r", encoding="utf-8") as f:
                defaults = yaml.safe_load(f) or {}

    # Start with all keys from default.yaml
    metadata = copy.deepcopy(defaults)

    # List of keys to override (project_data.json → YAML mapping)
    override_map = {
        "title": "title",
        "subtitle": "subtitle",
        "author": "author",
        "language": "lang",
        "description": "abstract",
        "genre": "genre",
        "date": "date",
        "cover-image": "cover-image",
        "keywords": "keywords",
        "publisher": "publisher",
        "isbn": "isbn",
        "rights": "rights",
    }

    # Helper to get value from project_knowledge_base (attribute or dict)
    def get_field(key):
        return getattr(project_knowledge_base, key, None) or project_knowledge_base.get(key, None)

    # Only replace if present in project data
    for src_key, yaml_key in override_map.items():
        value = get_field(src_key)
        if value is not None:
            if yaml_key == "keywords":
                # If keywords is a string, split by comma
                if isinstance(value, str):
                    value = [w.strip() for w in value.split(",")]
                metadata[yaml_key] = value
            elif yaml_key == "lang":
                metadata[yaml_key] = normalize_language(value)
            else:
                metadata[yaml_key] = value

    # Remove empty values
    metadata = {k: v for k, v in metadata.items() if v not in [None, "", []]}

    # Ensure block style for multiline header-includes
    if "header-includes" in metadata:
        metadata["header-includes"] = [
            ensure_literal_block(item) for item in metadata["header-includes"]
        ]

    yaml_block = "---\n" + yaml.safe_dump(metadata, sort_keys=False, allow_unicode=True) + "---\n"
    return yaml_block