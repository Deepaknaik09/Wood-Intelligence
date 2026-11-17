"""Download more wood-surface images with tighter queries.
Run from the ml folder:  python fetch_more_wood.py
Afterwards open extra_wood_samples and DELETE anything that is not a wood surface."""
import os
import time
import urllib.parse
import fetch_images as fi

QUERIES = [
    "oak wood texture", "pine board texture", "walnut veneer",
    "wood plank background", "wooden table top texture",
    "hardwood floor close-up", "weathered wood boards", "plywood sheet",
    "wood grain macro", "timber plank surface", "bamboo wood texture",
    "cherry wood grain", "maple wood texture", "wooden deck boards",
    "rough sawn lumber",
]
PER_QUERY = 4

folder = os.path.join(fi.BASE, "extra_wood_samples")
saved = 0
for qi, q in enumerate(QUERIES):
    try:
        urls = fi.search(q, PER_QUERY)
    except Exception as e:
        print(f"  search failed for '{q}': {e}")
        continue
    for k, url in enumerate(urls):
        ext = os.path.splitext(urllib.parse.urlparse(url).path)[1].lower()
        if ext not in (".jpg", ".jpeg", ".png"):
            ext = ".jpg"
        path = os.path.join(folder, f"wood2_{qi:02d}_{k}{ext}")
        try:
            fi.download(url, path)
            saved += 1
            print(f"  saved {os.path.basename(path)}  ({q})")
        except Exception as e:
            print(f"  download failed ({q}): {e}")
        time.sleep(1.0)
print(f"\nSaved {saved} images into {folder}")