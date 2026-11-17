"""Download sample images from Wikimedia Commons for testing the wood check.

Usage (from the ml folder, venv active):
    python fetch_images.py wood      -> saves into extra_wood_samples/
    python fetch_images.py nonwood   -> saves into non_wood_samples/
Afterwards open the folder and DELETE anything that doesn't belong
(the wood folder must hold only clear photos of wood; the non-wood
folder must not contain any wood).
"""
import os
import sys
import json
import time
import urllib.parse
import urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
API = "https://commons.wikimedia.org/w/api.php"
UA = "WoodIntelligenceStudentProject/1.0 (local testing)"

SETS = {
    "wood": ("extra_wood_samples", 3, [
        "pine wood texture", "oak planks", "walnut wood grain", "teak wood",
        "cedar wood boards", "plywood texture", "wooden floor", "wooden door",
        "birch wood", "wooden fence", "mahogany wood", "wooden table surface",
    ]),
    "nonwood": ("non_wood_samples", 2, [
        "cardboard texture", "brick wall", "sand texture", "leather texture",
        "rusty metal", "concrete wall", "street photograph",
        "portrait photograph", "food dish", "flower garden",
        "cat photograph", "car", "grass lawn", "stone wall", "beach",
        "fabric texture",
    ]),
}


def search(query, n):
    params = {
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": f"{query} filetype:bitmap", "gsrnamespace": "6",
        "gsrlimit": str(n * 3), "prop": "imageinfo",
        "iiprop": "url|mime", "iiurlwidth": "640",
    }
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    pages = data.get("query", {}).get("pages", {})
    out = []
    for p in sorted(pages.values(), key=lambda x: x.get("index", 0)):
        info = p.get("imageinfo", [{}])[0]
        if info.get("mime") in ("image/jpeg", "image/png") and info.get("thumburl"):
            out.append(info["thumburl"])
    return out[:n]


def download(url, path):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r, open(path, "wb") as f:
        f.write(r.read())


def main(kind):
    folder_name, per_query, queries = SETS[kind]
    folder = os.path.join(BASE, folder_name)
    os.makedirs(folder, exist_ok=True)
    saved = 0
    for qi, q in enumerate(queries):
        try:
            urls = search(q, per_query)
        except Exception as e:
            print(f"  search failed for '{q}': {e}")
            continue
        for k, url in enumerate(urls):
            ext = os.path.splitext(urllib.parse.urlparse(url).path)[1].lower()
            if ext not in (".jpg", ".jpeg", ".png"):
                ext = ".jpg"
            path = os.path.join(folder, f"{kind}_{qi:02d}_{k}{ext}")
            try:
                download(url, path)
                saved += 1
                print(f"  saved {os.path.basename(path)}  ({q})")
            except Exception as e:
                print(f"  download failed ({q}): {e}")
            time.sleep(1.0)
    print(f"\nSaved {saved} images into {folder}")


if __name__ == "__main__":
    kind = sys.argv[1] if len(sys.argv) > 1 else ""
    if kind in SETS:
        main(kind)
    else:
        print("Usage: python fetch_images.py wood | nonwood")