This tool processes PSD/KRA files by replacing text layers based on a config, generating previews, and exporting to PDF/X.

## Requirements
- Krita with Python scripting enabled
- Ghostscript
- Python packages in `requirements.txt`

## Installation (Ubuntu)
```bash
sudo snap install krita
```

## Usage
1. Put your `.kra` file as `input.kra`
2. Define config in `config/text_config.yaml`
3. Run `python scripts/process_pipeline.py`
4. Review `output.kra`, `output.pdf`, `output_pdfx.pdf`

## Extras
Run `visualize_layers.py` to generate thumbnails of text layers to help define your config.