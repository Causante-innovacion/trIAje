import fitz

doc = fitz.open(r"c:\Others\Project\CAUSANTE\gpt-legal\Fase 2 - ACE Legal.pdf")
with open(r"c:\Others\Project\CAUSANTE\gpt-legal\fase2_extracted.txt", "w", encoding="utf-8") as f:
    for i, page in enumerate(doc):
        f.write(f"--- PAGE {i+1} ---\n")
        f.write(page.get_text())
        f.write("\n")
print("Done! Saved to fase2_extracted.txt")
