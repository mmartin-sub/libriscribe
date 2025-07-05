import os
from datetime import datetime
import yaml
import langcodes

class LiteralStr(str):
    pass

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

def generate_yaml_metadata(project_knowledge_base, write_to_file=True):
    import copy
    # Load defaults from default.yaml
    defaults = {}
    # Find project root (three levels up from this file)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    default_yaml_path = os.path.join(project_root, "conf", "default-book.yaml")
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
        "abstract": "abstract",         # If you want to override the résumé
        "description": "description",   # For PDF comment metadata
        "date": "date",
        "keywords": "keywords",
        "publisher": "publisher",
        "isbn": "isbn",
        "rights": "rights",
        "subject": "subject",           # Add if you want to override
        "category": "category",         # Add if you want to override
        "outline": "outline",
    }

    # Helper to get value from project_knowledge_base (attribute or dict)
    def get_field(key):
        return getattr(project_knowledge_base, key, None) or project_knowledge_base.get(key, None)

    # Only replace if present in project data
    for src_key, yaml_key in override_map.items():
        value = get_field(src_key)
        if value is not None:
            print(f"Key for debugger: {yaml_key}")
            if yaml_key == "keywords":
                if isinstance(value, str):
                    value = [w.strip() for w in value.split(",")]
                metadata[yaml_key] = value
            elif yaml_key == "lang":
                metadata[yaml_key] = normalize_language(value)
            else:
                # Apply ensure_literal_block to all other string values
                metadata[yaml_key] = ensure_literal_block(value)

    # Remove empty values
    metadata = {k: v for k, v in metadata.items() if v not in [None, "", []]}

    # Ensure block style for multiline header-includes
    if "header-includes" in metadata:
        metadata["header-includes"] = [
            ensure_literal_block(item) for item in metadata["header-includes"]
        ]

    try:
        yaml_block = "---\n" + yaml.safe_dump(metadata, sort_keys=False, allow_unicode=True, default_flow_style=False) + "---\n"
    except Exception as e:
        print("DEBUG: description value:", repr(metadata.get("description")))
        error_path = os.path.join(
            getattr(project_knowledge_base, 'project_dir', os.getcwd()),
            "config-error.yaml"
        )

        print("[DEBUG] Metadata field types (on YAML serialization error):")
        for k, v in metadata.items():
            print(f"  {k}: {type(v)}")
        print("[DEBUG] Testing YAML serialization for each metadata field:")
        for k, v in metadata.items():
            try:
                yaml.safe_dump({k: v}, allow_unicode=True)
                print(f"  [OK] {k}")
            except Exception as field_exc:
                print(f"  [FAIL] {k}: {field_exc}")

        raise e
        with open(error_path, "w", encoding="utf-8") as f:
            f.write("# YAML serialization error. Raw metadata below:\n")
            try:
                yaml.safe_dump(metadata, f, sort_keys=False, allow_unicode=True)
            except Exception:
                f.write(repr(metadata))

        print(f"[red]❌ Error serializing YAML metadata. Saved problematic data to: {error_path}[/red]")
        raise e

    # Add log message
    print(f"[LOG] YAML metadata updated")

    # Optionally write to config-metadata.yaml
    if write_to_file:
        # Save config-metadata.yaml in the same directory as chapter_*.md files
        config_dir = getattr(project_knowledge_base, 'project_dir', None)
        if config_dir is not None:
            config_path = os.path.join(str(config_dir), "config-metadata.yaml")
        else:
            config_path = os.path.join(project_root, "config-metadata.yaml")
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(metadata, f, sort_keys=False, allow_unicode=True)
        print(f"[green]📝 Metadata YAML generated at: {config_path}[/green]")

    return yaml_block