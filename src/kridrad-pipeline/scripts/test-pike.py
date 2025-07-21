# This script uses pikepdf to list all image XObjects and gives a general structure.
# It does NOT extract text directly (pikepdf is low-level), but it can show if images exist and what resources are present.
# We'll also print all object types to explore any layer or image structures.

import pikepdf

pdf_path = "sample.pdf"  # Replace with your file path

with pikepdf.open(pdf_path) as pdf:
    print(f"PDF has {len(pdf.pages)} pages")

    for i, page in enumerate(pdf.pages):
        print(f"\n--- Page {i+1} ---")
        resources = page.get("/Resources", {})
        xobjects = resources.get("/XObject", {})

        if xobjects:
            print("XObjects (likely images or forms):")
            for name, obj in xobjects.items():
                try:
                    xobj = pdf.open_object(obj.objgen)
                    subtype = xobj.get("/Subtype", "Unknown")
                    print(f"  {name}: subtype = {subtype}")
                except Exception as e:
                    print(f"  {name}: error reading object - {e}")
        else:
            print("No XObjects on this page.")

    # Check for optional content properties (OCGs/layers)
    ocprops = pdf.Root.get("/OCProperties", None)
    if ocprops:
        print("\nPDF contains Optional Content Groups (Layers):")
        for k, v in ocprops.items():
            print(f"  {k} -> {v}")
    else:
        print("\nNo Optional Content Groups (Layers) found.")
