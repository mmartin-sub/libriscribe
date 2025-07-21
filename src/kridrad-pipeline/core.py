from krita import Krita, InfoObject
import subprocess

app = Krita.instance()

def load_kra(path):
    return app.openDocument(path)

def list_text_layers(doc):
    nodes = []
    def traverse(node):
        if node.type() == 'text':
            nodes.append(node)
        for child in node.childNodes():
            traverse(child)
    for top in doc.topLevelNodes():
        traverse(top)
    return nodes

def edit_text_layer(doc, node, text=None, font=None, size=None, color=None):
    if text: node.setText(text)
    if font: node.setFont(font)
    if size: node.setFontSize(size)
    if color: node.setColor(color)
    doc.refreshProjection()

def save_kra(doc, path):
    doc.saveAs(path)

def export_pdf(doc, pdf_path):
    info = InfoObject()
    info.setProperty("mime", "application/pdf")
    doc.exportImage(pdf_path, info)

def export_pdfx_via_ghostscript(input_pdf, output_pdfx):
    subprocess.run([
        'gs', '-dPDFX', '-dBATCH', '-dNOPAUSE',
        '-sDEVICE=pdfwrite',
        f'-sOutputFile={output_pdfx}',
        '-sColorConversionStrategy=CMYK',
        input_pdf
    ], check=True)

# scripts/visualize_layers.py
from kridrad.core import load_kra, list_text_layers
from PyQt5.QtGui import QImage
import os

def save_layer_thumbnails(doc, output_dir="layer_thumbnails"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    layers = list_text_layers(doc)
    for idx, layer in enumerate(layers):
        img = layer.thumbnail()
        path = os.path.join(output_dir, f"layer_{idx}_{layer.name()}.png")
        img.save(path, "PNG")
        print(f"Saved: {path}")

if __name__ == "__main__":
    doc = load_kra("input.kra")
    save_layer_thumbnails(doc)