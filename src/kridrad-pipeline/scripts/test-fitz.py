# Let's use PyMuPDF (fitz) to inspect the structure of the PDF:
# This script will list all layers (OCGs), images, and text blocks from each page.

import fitz  # PyMuPDF

pdf_path = "sample.pdf"  # Replace with your file path

doc = fitz.open(pdf_path)

print(f"PDF has {len(doc)} pages\n")

for page_num in range(len(doc)):
    page = doc[page_num]
    print(f"--- Page {page_num + 1} ---")

    # Text blocks
    text_blocks = page.get_text("dict")["blocks"]
    print(f"Text blocks ({len(text_blocks)}):")
    for block in text_blocks:
        if block["type"] == 0:  # Text block
            full_block_text = ""
            for line in block["lines"]:
                for span in line["spans"]:
                    full_block_text += span["text"]
                # Optionally add a space or newline after each line for better readability
                # full_block_text += " " # Add a space between lines
            print(f"  Full Block Text: '{full_block_text}'")
        else: # Image block (type 1)
            print(f"  Image block (type 1) at {block['bbox']}")

    # Images
    image_list = page.get_images(full=True)
    print(f"Images ({len(image_list)}):")
    for img in image_list:
        xref = img[0]
        width = img[2]
        height = img[3]
        print(f"  Image xref={xref}, size={width}x{height}")

    print()

# Optional Content Groups (Layers)
ocgs = doc.get_ocgs()
if ocgs:
    print("Optional Content Groups (Layers):")
    for ocg in ocgs:
        print(f"  OCG: {ocg['name']} - Visible: {ocg['state']}")
else:
    print("No OCGs (layers) found in the document.")

doc.close()