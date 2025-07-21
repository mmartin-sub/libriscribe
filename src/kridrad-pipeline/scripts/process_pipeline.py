import yaml
from kridrad.core import load_kra, list_text_layers, edit_text_layer, save_kra, export_pdf, export_pdfx_via_ghostscript

def apply_config(doc, config):
    layers = list_text_layers(doc)
    for layer_cfg in config['layers']:
        for layer in layers:
            if layer.name() == layer_cfg['name']:
                edit_text_layer(
                    doc, layer,
                    text=layer_cfg.get('text'),
                    font=layer_cfg.get('font'),
                    size=layer_cfg.get('size'),
                    color=layer_cfg.get('color')
                )

if __name__ == "__main__":
    with open("config/text_config.yaml") as f:
        config = yaml.safe_load(f)

    doc = load_kra("input.kra")
    apply_config(doc, config)
    save_kra(doc, "output.kra")
    export_pdf(doc, "output.pdf")
    export_pdfx_via_ghostscript("output.pdf", "output_pdfx.pdf")