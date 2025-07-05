import os
from datetime import datetime
import yaml
import langcodes
from jinja2 import Environment, StrictUndefined, TemplateError, FileSystemLoader, select_autoescape
import json

# The LiteralStr class and its associated functions are no longer needed.
# The new approach uses Jinja2 to render the YAML template directly,
# which correctly handles multi-line strings using the `indent` filter
# within the template itself (e.g., `{{ description | indent(2) }}`).

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
    """
    Generate YAML metadata by rendering the default-book.yaml Jinja2 template.
    This approach is more robust for complex values like multi-line strings.
    """
    # Find project root (four levels up from this file: utils -> libriscribe -> src -> project_root)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    template_dir = os.path.join(project_root, "conf")
    template_file = "default-book.yaml.jinja2" # The template file

    # 1. Prepare the context dictionary from the project knowledge base.
    context = {}

    def get_field(key):
        if hasattr(project_knowledge_base, key):
            return getattr(project_knowledge_base, key, None)
        return project_knowledge_base.get(key, None)

    override_map = {
        "title": "title",
        "subtitle": "subtitle",
        "author": "author",
        "language": "lang",
        "abstract": "abstract",
        "description": "description",
        "date": "date",
        "keywords": "keywords",
        "publisher": "publisher",
        "isbn": "isbn",
        "rights": "rights",
        "subject": "subject",
        "category": "category",
        "outline": "outline",
    }

    for src_key, template_key in override_map.items():
        value = get_field(src_key)
        # We only add non-empty values to the context. The template's `default()`
        # filter will handle cases where a value is not provided.
        if value is not None and value not in ["", []]:
            if template_key == "keywords" and isinstance(value, str):
                context[template_key] = [w.strip() for w in value.split(",")]
            elif template_key == "lang":
                context[template_key] = normalize_language(value)
            elif template_key == "author" and isinstance(value, str):
                # Ensure author is always a list for the template's for-loop
                context[template_key] = [value]
            else:
                context[template_key] = value

    # 2. Set up Jinja2 environment.
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(disabled_extensions=('yaml',)),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )

    # 3. Load and render the template.
    try:
        template = env.get_template(template_file)
        rendered_yaml = template.render(**context)
    except TemplateError as e:
        # Provide a more informative error message for debugging.
        print(f"[red]❌ Jinja2 template error in '{os.path.join(template_dir, template_file)}':[/red]")
        print(f"[red]   Error: {e}[/red]")
        print(f"[yellow]   Context provided to template:[/yellow]")
        # Pretty-print the context for readability
        print(f"[yellow]{json.dumps(context, indent=2, ensure_ascii=False)}[/yellow]")
        raise

    # 4. Wrap in YAML front matter fences for Pandoc.
    yaml_block = f"---\n{rendered_yaml.strip()}\n---\n"

    print(f"[LOG] YAML metadata updated (Jinja2)")

    if write_to_file:
        config_dir = getattr(project_knowledge_base, 'project_dir', None)
        if config_dir is not None:
            config_path = os.path.join(str(config_dir), "config-metadata.yaml")
        else:
            config_path = os.path.join(project_root, "config-metadata.yaml")
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(yaml_block)
        print(f"[green]📝 Metadata YAML generated at: {config_path}[/green]")

    return yaml_block