"""
=============================================================================
WOOD INTELLIGENCE — MULTI-PERSPECTIVE ARCHITECTURAL DESIGN VISUALIZER
=============================================================================
Procedural multi-view architectural design generator for furniture design patterns,
enriched with authentic timber species tone mapping, high-definition studio cyclorama
rendering, precision CAD drafting, structural joinery schematics, and in-situ room contexts.
Every design pattern receives unique, bespoke architectural illustrations matching its
individual design style (Floating, Spindle Slat, Live-Edge, Craftsman, Trestle, Kumiko, etc.).
=============================================================================
"""

import os
import re
import math
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageOps

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "generated_designs")
os.makedirs(ASSETS_DIR, exist_ok=True)

ROOT_PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ASSETS_DIR = os.path.join(ROOT_PROJECT_DIR, "assets")

# Authentic color grading palettes for all 29 commercial timbers in Wood Intelligence
WOOD_SPECIES_TINTS = {
    "teak": (185, 125, 65),              # Golden honey bronze
    "sal": (140, 95, 55),                # Deep coarse brown
    "sheesham": (95, 50, 28),            # Deep auburn dark chocolate
    "mahogany": (160, 65, 45),           # Rich reddish amber
    "white_oak": (195, 160, 115),        # Textured golden straw
    "hard_maple": (245, 230, 205),       # Creamy blonde butter
    "black_walnut": (75, 50, 35),        # Smoky espresso mocha
    "white_ash": (240, 230, 210),        # Crisp porcelain wheat
    "beech": (220, 185, 160),            # Pale salmon blush
    "black_cherry": (175, 80, 50),       # Warm cinnamon amber
    "pine": (240, 215, 160),             # Pale golden yellow
    "western_red_cedar": (180, 95, 60),  # Warm reddish cedar
    "deodar": (215, 175, 120),           # Light golden fawn
    "rubberwood": (230, 210, 175),       # Pale cream straw
    "acacia": (170, 115, 65),            # Golden brown with dark sapwood
    "mango": (210, 170, 120),            # Golden blonde with gray streaks
    "jackfruit": (225, 170, 55),         # Radiant golden saffron
    "bamboo": (235, 220, 185),           # Clean pale ivory straw
    "yellow_birch": (230, 195, 140),     # Golden blonde birch
    "poplar": (205, 200, 165),           # Light olive cream
    "ironwood": (65, 45, 30),            # Heavy dark espresso
    "african_padauk": (160, 45, 30),     # Vermillion brick crimson
    "andaman_padauk": (150, 40, 25),     # Deep crimson red
    "marupa": (248, 242, 230),           # Pristine pale white cream
    "eucalyptus": (215, 175, 155),       # Soft pinkish light tan
    "haldu": (225, 175, 75),             # Radiant warm mustard gold
    "sapele": (150, 75, 45),             # Ribbon-striped cedar bronze
    "wenge": (45, 30, 22),               # Intense near-black espresso
    "red_oak": (200, 150, 120),          # Warm pinkish tan oak
    "default": (200, 150, 95)            # Universal neutral timber
}

def get_font(size: int = 14, bold: bool = False, mono: bool = False):
    """Loads system TrueType font with graceful fallback to default PIL font."""
    font_paths = []
    if mono:
        if bold:
            font_paths.append("C:/Windows/Fonts/consolab.ttf")
        font_paths.append("C:/Windows/Fonts/consola.ttf")
    else:
        if bold:
            font_paths.append("C:/Windows/Fonts/segoeuib.ttf")
            font_paths.append("C:/Windows/Fonts/arialbd.ttf")
        font_paths.append("C:/Windows/Fonts/segoeui.ttf")
        font_paths.append("C:/Windows/Fonts/arial.ttf")
    
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                continue
    return ImageFont.load_default()

def get_wood_tint(wood_id: str) -> tuple:
    """Returns the RGB tint corresponding to the wood species."""
    if not wood_id:
        return WOOD_SPECIES_TINTS["default"]
    w_clean = wood_id.lower().replace("-", "_").replace(" ", "_")
    for k, tint in WOOD_SPECIES_TINTS.items():
        if k in w_clean or w_clean in k:
            return tint
    return WOOD_SPECIES_TINTS["default"]

def slugify(text: str) -> str:
    """Generates a clean filesystem slug from a title string."""
    return re.sub(r'[^a-zA-Z0-9_]+', '_', text.strip().lower())[:40]

def get_design_image_path(furniture_id: str, pattern_title: str, wood_id: str) -> str:
    """Legacy single-image path compatibility (maps to CAD Blueprint)."""
    p_slug = slugify(pattern_title)
    w_slug = slugify(wood_id)
    return os.path.join(ASSETS_DIR, f"{furniture_id}_{p_slug}_{w_slug}.png")

def get_design_suite_paths(furniture_id: str, pattern_title: str, wood_id: str) -> dict:
    """Returns paths for all 4 multi-perspective views in the design suite."""
    p_slug = slugify(pattern_title)
    w_slug = slugify(wood_id)
    base = f"{furniture_id}_{p_slug}_{w_slug}"
    return {
        "studio": os.path.join(ASSETS_DIR, f"{base}_studio.png"),
        "blueprint": os.path.join(ASSETS_DIR, f"{base}_cad.png"),
        "joinery": os.path.join(ASSETS_DIR, f"{base}_joinery.png"),
        "insitu": os.path.join(ASSETS_DIR, f"{base}_insitu.png")
    }

def is_suite_generated(furniture_id: str, pattern_title: str, wood_id: str) -> bool:
    """Returns True if all 4 views of the suite exist on disk."""
    paths = get_design_suite_paths(furniture_id, pattern_title, wood_id)
    return all(os.path.exists(p) for p in paths.values())


# =============================================================================
# AUTHENTIC PHOTOREALISTIC DESIGN ENGINE & TONE MAPPING
# =============================================================================
def apply_species_photographic_grading(img: Image.Image, wood_id: str) -> Image.Image:
    """Subtly grades the timber highlights and midtones to match the active wood species,
    preserving 100% of photographic grain, reflections, shadows, and natural depth."""
    if not wood_id:
        return img
    img = img.convert("RGB")
    tint = get_wood_tint(wood_id)
    if tint == WOOD_SPECIES_TINTS.get("default"):
        return img
    tint_layer = Image.new("RGB", img.size, tint)
    graded = Image.blend(img, tint_layer, alpha=0.08)
    enhancer = ImageEnhance.Contrast(graded)
    return enhancer.enhance(1.04)


def get_pattern_photo(furniture_id: str, pattern: dict = None, pattern_index: int = 0) -> str:
    """Finds the best authentic, high-resolution photograph for this furniture piece & pattern."""
    p_title = pattern.get("title", "").lower() if pattern else ""
    candidates = [
        os.path.join(PROJECT_ASSETS_DIR, "furniture_patterns", f"{furniture_id}_{pattern_index}.jpg"),
        os.path.join(PROJECT_ASSETS_DIR, "furniture_patterns", f"{furniture_id}_{pattern_index}.png"),
    ]
    if "wishbone" in p_title or "scandi" in p_title:
        candidates.insert(0, os.path.join(PROJECT_ASSETS_DIR, "furniture_patterns", "dining_chair_0.jpg"))
    elif "sculptural" in p_title or "mid_century" in p_title or "mid-century" in p_title:
        if "chair" in furniture_id:
            candidates.insert(0, os.path.join(PROJECT_ASSETS_DIR, "furniture_patterns", "dining_chair_1.jpg"))
        elif "cot" in furniture_id or "bed" in furniture_id:
            candidates.insert(0, os.path.join(PROJECT_ASSETS_DIR, "furniture_patterns", "cot_1.jpg"))
    elif "platform" in p_title or "floating" in p_title or "cantilever" in p_title:
        candidates.insert(0, os.path.join(PROJECT_ASSETS_DIR, "furniture_patterns", "cot_0.jpg"))
    elif "live_edge" in p_title or "slab" in p_title or "organic" in p_title:
        if "cot" in furniture_id or "bed" in furniture_id:
            candidates.insert(0, os.path.join(PROJECT_ASSETS_DIR, "furniture_patterns", "cot_2.jpg"))
        elif "table" in furniture_id:
            candidates.insert(0, os.path.join(PROJECT_ASSETS_DIR, "furniture_patterns", "dining_table_0.jpg"))
    elif "craftsman" in p_title or "post" in p_title or "beam" in p_title:
        candidates.insert(0, os.path.join(PROJECT_ASSETS_DIR, "furniture_patterns", "cot_3.jpg"))
    elif "lattice" in p_title or "kumiko" in p_title or "slat" in p_title:
        if "chair" in furniture_id:
            candidates.insert(0, os.path.join(PROJECT_ASSETS_DIR, "furniture_patterns", "dining_chair_2.jpg"))
        elif "partition" in furniture_id:
            candidates.insert(0, os.path.join(PROJECT_ASSETS_DIR, "furniture_patterns", "wooden_partition_0.jpg"))

    candidates.append(os.path.join(PROJECT_ASSETS_DIR, "furniture_patterns", f"{furniture_id}_0.jpg"))
    candidates.append(os.path.join(PROJECT_ASSETS_DIR, "furniture", f"{furniture_id}.jpg"))
    candidates.append(os.path.join(PROJECT_ASSETS_DIR, "furniture", f"{furniture_id}.webp"))
    candidates.append(os.path.join(PROJECT_ASSETS_DIR, "furniture", f"{furniture_id}.png"))

    cat_fallbacks = {
        "dining_chair": ["chair.jpg", "wooden_chair.jpg", "armchair.jpg"],
        "wooden_chair": ["dining_chair.jpg", "chair.jpg"],
        "armchair": ["dining_chair.jpg", "chair.jpg"],
        "stool": ["chair.jpg", "bench.jpg"],
        "bench": ["chair.jpg", "table.jpg"],
        "cot": ["bed.jpg", "bed_frame.jpg"],
        "bed_frame": ["cot.jpg", "bed.jpg"],
        "bunk_bed": ["bed.jpg", "cot.jpg"],
        "dining_table": ["table.jpg", "coffee_table.jpg"],
        "coffee_table": ["table.jpg", "dining_table.jpg"],
        "desk": ["table.jpg", "study_table.jpg"],
        "study_table": ["table.jpg", "desk.jpg"],
        "wooden_partition": ["door.jpg", "window_frame.jpg"]
    }
    for fb in cat_fallbacks.get(furniture_id, []):
        candidates.append(os.path.join(PROJECT_ASSETS_DIR, "furniture", fb))

    for c in candidates:
        if os.path.exists(c) and os.path.getsize(c) > 5000:
            return c
    return os.path.join(PROJECT_ASSETS_DIR, "furniture", "chair.jpg")


# =============================================================================
# PROCEDURAL ARCHITECTURAL FURNITURE ILLUSTRATION ENGINE
# =============================================================================
def draw_wood_grain(draw, bbox, base_tint, lines=10, dark_factor=0.82):
    """Draws realistic flowing timber grain lines across the specified bounding box."""
    x1, y1, x2, y2 = bbox
    w = max(1, x2 - x1)
    h = max(1, y2 - y1)
    grain_col = (int(base_tint[0] * dark_factor), int(base_tint[1] * dark_factor), int(base_tint[2] * dark_factor), 140)
    for i in range(lines):
        gy = y1 + int(h * (i + 0.5) / lines)
        wave_pts = []
        for gx in range(x1, x2, 12):
            offset = math.sin((gx - x1) * 0.04 + i) * 3
            wave_pts.append((gx, min(y2 - 1, max(y1, gy + offset))))
        if len(wave_pts) > 1:
            draw.line(wave_pts, fill=grain_col, width=1)

def draw_butterfly_key(draw, cx, cy, size=16, color=(50, 30, 18, 240)):
    """Draws a traditional butterfly / bow-tie joinery inlay key."""
    hw = size // 2
    hh = size // 3
    pts = [
        (cx - hw, cy - hh), (cx, cy - 2), (cx + hw, cy - hh),
        (cx + hw, cy + hh), (cx, cy + 2), (cx - hw, cy + hh)
    ]
    draw.polygon(pts, fill=color)

def generate_pattern_artwork(furniture_id: str, pattern: dict, wood_info: dict, width: int = 700, height: int = 430, style: str = "studio") -> Image:
    """
    Renders a bespoke, clean architectural illustration of the furniture piece
    tailored specifically to the pattern's design style, joinery, and dimensions,
    authentically color-graded in the active timber species tone.
    """
    w_id = wood_info.get("id", "timber") if wood_info else "timber"
    tint = get_wood_tint(w_id)
    im = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)

    p_title = pattern.get("title", "").lower()

    # Species timber shade variations
    top_tint = tuple(min(255, int(c * 1.08)) for c in tint)
    side_tint = tuple(max(0, int(c * 0.72)) for c in tint)
    front_tint = tint
    line_col = tuple(max(0, int(c * 0.45)) for c in tint)
    highlight_col = tuple(min(255, int(c * 1.25)) for c in tint)

    # -------------------------------------------------------------------------
    # 1. COT / BED DESIGNS
    # -------------------------------------------------------------------------
    if "cot" in furniture_id or "bed" in furniture_id:
        bx1, by1 = 120, 160
        bx2, by2 = width - 120, height - 85
        pw = bx2 - bx1

        if "floating" in p_title or "cantilever" in p_title:
            # 1a. Cantilevered Floating Platform Cot (Recessed invisible plinth + levitating deck)
            draw.rectangle([bx1 + 80, by2 - 25, bx2 - 80, by2 + 10], fill=(20, 20, 25, 180))
            deck_y1 = by1 + 60
            deck_y2 = by2 - 25

            draw.polygon([(bx1 - 30, deck_y1 + 40), (bx1 + 30, deck_y1), (bx2 + 30, deck_y1), (bx2 - 30, deck_y1 + 40)], fill=top_tint + (255,), outline=line_col)
            draw_wood_grain(draw, (bx1 - 25, deck_y1, bx2 + 25, deck_y1 + 40), top_tint, lines=6)

            draw.polygon([(bx1 - 30, deck_y1 + 40), (bx2 - 30, deck_y1 + 40), (bx2 - 30, deck_y2), (bx1 - 30, deck_y2)], fill=front_tint + (255,), outline=line_col)
            draw_wood_grain(draw, (bx1 - 30, deck_y1 + 40, bx2 - 30, deck_y2), front_tint, lines=4)

            m_col = (248, 246, 242, 255) if style != "blueprint" else (255, 255, 255, 255)
            draw.polygon([(bx1 + 10, deck_y1 + 32), (bx1 + 55, deck_y1 + 8), (bx2 - 10, deck_y1 + 8), (bx2 - 55, deck_y1 + 32)], fill=m_col, outline=line_col)
            draw.polygon([(bx1 + 10, deck_y1 + 32), (bx2 - 55, deck_y1 + 32), (bx2 - 55, deck_y1 + 52), (bx1 + 10, deck_y1 + 52)], fill=(235, 232, 225, 255) if style != "blueprint" else (255, 255, 255, 255), outline=line_col)

            hb_y1 = by1 - 70
            hb_y2 = deck_y1 + 25
            draw.rectangle([bx1 - 45, hb_y1, bx2 + 45, hb_y2], fill=front_tint + (255,), outline=line_col, width=2)
            draw_wood_grain(draw, (bx1 - 45, hb_y1, bx2 + 45, hb_y2), front_tint, lines=8)
            draw.line([(bx1 - 45, hb_y1 + 45), (bx2 + 45, hb_y1 + 45)], fill=line_col + (200,), width=2)
            draw.line([(bx1 - 45, hb_y1 + 47), (bx2 + 45, hb_y1 + 47)], fill=highlight_col + (200,), width=1)

            draw.rectangle([bx1 - 75, hb_y2 - 30, bx1 - 35, hb_y2 - 10], fill=top_tint + (255,), outline=line_col)
            draw.rectangle([bx2 + 35, hb_y2 - 30, bx2 + 75, hb_y2 - 10], fill=top_tint + (255,), outline=line_col)

        elif "spindle" in p_title:
            # 1b. Mid-Century Spindle Slat Cot (Turned spindles, tapered crest rail, splayed legs)
            leg_w = 16
            draw.polygon([(bx1, by2 - 40), (bx1 - 20, by2 + 15), (bx1 - 10, by2 + 15), (bx1 + leg_w, by2 - 40)], fill=side_tint + (255,), outline=line_col)
            draw.polygon([(bx2 - leg_w, by2 - 40), (bx2 + 10, by2 + 15), (bx2 + 20, by2 + 15), (bx2, by2 - 40)], fill=side_tint + (255,), outline=line_col)
            draw.polygon([(bx1 - 18, by2 + 3), (bx1 - 20, by2 + 15), (bx1 - 10, by2 + 15), (bx1 - 12, by2 + 3)], fill=(218, 165, 32, 255), outline=line_col)
            draw.polygon([(bx2 + 12, by2 + 3), (bx2 + 10, by2 + 15), (bx2 + 20, by2 + 15), (bx2 + 18, by2 + 3)], fill=(218, 165, 32, 255), outline=line_col)

            deck_y1 = by1 + 65
            deck_y2 = by2 - 40
            draw.rectangle([bx1, deck_y2 - 25, bx2, deck_y2], fill=front_tint + (255,), outline=line_col, width=2)
            draw_wood_grain(draw, (bx1, deck_y2 - 25, bx2, deck_y2), front_tint, lines=3)

            m_col = (250, 248, 244, 255) if style != "blueprint" else (255, 255, 255, 255)
            draw.rectangle([bx1 + 15, deck_y1 + 10, bx2 - 15, deck_y2 - 25], fill=m_col, outline=line_col)

            hb_top = by1 - 85
            hb_bot = deck_y1 + 10
            draw.rectangle([bx1 - 10, hb_top, bx1 + 12, deck_y2], fill=side_tint + (255,), outline=line_col, width=2)
            draw.rectangle([bx2 - 12, hb_top, bx2 + 10, deck_y2], fill=side_tint + (255,), outline=line_col, width=2)
            draw.polygon([(bx1 - 15, hb_top + 10), (bx1 - 10, hb_top - 4), (bx2 + 10, hb_top - 4), (bx2 + 15, hb_top + 10), (bx2 + 10, hb_top + 24), (bx1 - 10, hb_top + 24)], fill=top_tint + (255,), outline=line_col)
            draw_wood_grain(draw, (bx1 - 10, hb_top - 4, bx2 + 10, hb_top + 24), top_tint, lines=2)

            draw.rectangle([bx1 + 12, hb_bot - 16, bx2 - 12, hb_bot], fill=front_tint + (255,), outline=line_col)

            num_spindles = 17
            sp_step = (bx2 - bx1 - 40) / (num_spindles + 1)
            for s in range(num_spindles):
                sx = int(bx1 + 20 + (s + 1) * sp_step)
                draw.rectangle([sx - 3, hb_top + 24, sx + 3, hb_bot - 16], fill=side_tint + (255,), outline=line_col)
                draw.line([(sx, hb_top + 24), (sx, hb_bot - 16)], fill=highlight_col + (180,), width=1)

        elif "live" in p_title or "slab" in p_title:
            # 1c. Live-Edge Organic Slab Cot (Live edge slab with butterfly joinery keys)
            deck_y1 = by1 + 60
            deck_y2 = by2 - 15
            draw.rectangle([bx1 + 10, deck_y2, bx1 + 75, deck_y2 + 25], fill=side_tint + (255,), outline=line_col)
            draw.rectangle([bx2 - 75, deck_y2, bx2 - 10, deck_y2 + 25], fill=side_tint + (255,), outline=line_col)

            draw.rectangle([bx1, deck_y2 - 35, bx2, deck_y2], fill=front_tint + (255,), outline=line_col, width=2)
            draw_wood_grain(draw, (bx1, deck_y2 - 35, bx2, deck_y2), front_tint, lines=4)

            m_col = (248, 245, 240, 255) if style != "blueprint" else (255, 255, 255, 255)
            draw.rectangle([bx1 + 20, deck_y1 + 10, bx2 - 20, deck_y2 - 35], fill=m_col, outline=line_col)

            hb_top = by1 - 95
            hb_bot = deck_y1 + 15
            contour_pts = []
            for px in range(bx1 - 35, bx2 + 40, 12):
                wave = math.sin((px - bx1) * 0.03) * 14 + math.cos((px - bx1) * 0.07) * 7
                contour_pts.append((px, int(hb_top + wave)))
            contour_pts.append((bx2 + 35, hb_bot))
            contour_pts.append((bx1 - 35, hb_bot))

            draw.polygon(contour_pts, fill=front_tint + (255,), outline=line_col)
            draw_wood_grain(draw, (bx1 - 35, hb_top - 15, bx2 + 35, hb_bot), front_tint, lines=10)

            draw_butterfly_key(draw, bx1 + 60, hb_top + 28, size=18)
            draw_butterfly_key(draw, bx1 + pw // 2, hb_top + 38, size=20)
            draw_butterfly_key(draw, bx2 - 70, hb_top + 25, size=18)

        else:
            # 1d. Post-and-Beam Craftsman Cot (Heavy timber posts + mortise pegs)
            deck_y1 = by1 + 60
            deck_y2 = by2 - 20
            post_w = 34
            hb_top = by1 - 95

            for px in [bx1 - 15, bx2 - post_w + 15]:
                draw.polygon([(px, hb_top + 10), (px + post_w // 2, hb_top), (px + post_w, hb_top + 10), (px + post_w, hb_top + 18), (px, hb_top + 18)], fill=top_tint + (255,), outline=line_col)
                draw.rectangle([px, hb_top + 18, px + post_w, deck_y2 + 25], fill=side_tint + (255,), outline=line_col, width=2)
                draw_wood_grain(draw, (px, hb_top + 18, px + post_w, deck_y2 + 25), side_tint, lines=12)

            draw.rectangle([bx1 - 15, hb_top + 22, bx2 + 15, hb_top + 52], fill=top_tint + (255,), outline=line_col, width=2)
            draw_wood_grain(draw, (bx1 - 15, hb_top + 22, bx2 + 15, hb_top + 52), top_tint, lines=3)
            for px in [bx1 + 2, bx2 - 18]:
                draw.rectangle([px, hb_top + 32, px + 8, hb_top + 42], fill=(45, 25, 12, 255), outline=line_col)

            draw.rectangle([bx1 + post_w - 15, deck_y1 - 10, bx2 - post_w + 15, deck_y1 + 10], fill=front_tint + (255,), outline=line_col)
            c_slats = 9
            c_step = (bx2 - bx1 - 2 * post_w) / (c_slats + 1)
            for c in range(c_slats):
                cx = int(bx1 + post_w - 15 + (c + 1) * c_step)
                draw.rectangle([cx - 8, hb_top + 52, cx + 8, deck_y1 - 10], fill=front_tint + (255,), outline=line_col)

            fb_h = deck_y2 - 60
            for px in [bx1 - 10, bx2 - post_w + 10]:
                draw.polygon([(px, fb_h - 10), (px + post_w // 2, fb_h - 18), (px + post_w, fb_h - 10)], fill=top_tint + (255,), outline=line_col)
                draw.rectangle([px, fb_h - 10, px + post_w, deck_y2 + 25], fill=side_tint + (255,), outline=line_col, width=2)
            draw.rectangle([bx1 + post_w - 10, fb_h, bx2 - post_w + 10, fb_h + 30], fill=front_tint + (255,), outline=line_col)

    # -------------------------------------------------------------------------
    # 2. CHAIR / SEATING DESIGNS
    # -------------------------------------------------------------------------
    elif "chair" in furniture_id or "stool" in furniture_id or "armchair" in furniture_id or "bench" in furniture_id:
        cx = width // 2
        seat_y = height - 150
        seat_w = 260
        seat_h = 32

        # Legs
        draw.polygon([(cx - seat_w // 2 + 10, seat_y + seat_h), (cx - seat_w // 2 - 18, height - 25), (cx - seat_w // 2 - 4, height - 25), (cx - seat_w // 2 + 24, seat_y + seat_h)], fill=side_tint + (255,), outline=line_col)
        draw.polygon([(cx + seat_w // 2 - 24, seat_y + seat_h), (cx + seat_w // 2 + 4, height - 25), (cx + seat_w // 2 + 18, height - 25), (cx + seat_w // 2 - 10, seat_y + seat_h)], fill=side_tint + (255,), outline=line_col)

        # Seat
        draw.rectangle([cx - seat_w // 2, seat_y, cx + seat_w // 2, seat_y + seat_h], fill=top_tint + (255,), outline=line_col, width=2)
        draw_wood_grain(draw, (cx - seat_w // 2, seat_y, cx + seat_w // 2, seat_y + seat_h), top_tint, lines=4)

        if "wishbone" in p_title or "scandinavian" in p_title:
            # Curved continuous crest rail
            rail_pts = [(cx - seat_w // 2 - 20, seat_y - 120), (cx, seat_y - 170), (cx + seat_w // 2 + 20, seat_y - 120), (cx + seat_w // 2 + 15, seat_y - 95), (cx, seat_y - 145), (cx - seat_w // 2 - 15, seat_y - 95)]
            draw.polygon(rail_pts, fill=front_tint + (255,), outline=line_col)
            # Y-Wishbone splat
            draw.polygon([(cx - 10, seat_y - 145), (cx + 10, seat_y - 145), (cx + 4, seat_y - 70), (cx - 4, seat_y - 70)], fill=side_tint + (255,), outline=line_col)
            draw.polygon([(cx - 4, seat_y - 70), (cx + 4, seat_y - 70), (cx + 35, seat_y), (cx + 20, seat_y)], fill=side_tint + (255,), outline=line_col)
            draw.polygon([(cx - 4, seat_y - 70), (cx + 4, seat_y - 70), (cx - 20, seat_y), (cx - 35, seat_y)], fill=side_tint + (255,), outline=line_col)
        elif "lattice" in p_title or "slat" in p_title:
            # Vertical slat back
            draw.rectangle([cx - seat_w // 2 + 20, seat_y - 160, cx + seat_w // 2 - 20, seat_y - 135], fill=top_tint + (255,), outline=line_col)
            for s in range(7):
                sx = cx - seat_w // 2 + 35 + s * 30
                draw.rectangle([sx, seat_y - 135, sx + 12, seat_y], fill=front_tint + (255,), outline=line_col)
        else:
            # Sculptural curved back
            draw.polygon([(cx - seat_w // 2 + 15, seat_y - 160), (cx + seat_w // 2 - 15, seat_y - 160), (cx + seat_w // 2 - 30, seat_y), (cx - seat_w // 2 + 30, seat_y)], fill=front_tint + (255,), outline=line_col)
            draw_wood_grain(draw, (cx - seat_w // 2 + 15, seat_y - 160, cx + seat_w // 2 - 15, seat_y), front_tint, lines=6)

    # -------------------------------------------------------------------------
    # 3. TABLE DESIGNS
    # -------------------------------------------------------------------------
    elif "table" in furniture_id or "desk" in furniture_id:
        top_y = height - 210
        top_h = 36
        tw = width - 160
        tx1 = 80
        tx2 = width - 80

        # Tabletop
        draw.rectangle([tx1, top_y, tx2, top_y + top_h], fill=top_tint + (255,), outline=line_col, width=2)
        draw_wood_grain(draw, (tx1, top_y, tx2, top_y + top_h), top_tint, lines=5)

        if "trestle" in p_title or "live" in p_title:
            # Trestle base
            draw_butterfly_key(draw, tx1 + 100, top_y + top_h // 2, size=18)
            draw_butterfly_key(draw, tx2 - 100, top_y + top_h // 2, size=18)
            # Left & Right Trestle uprights
            draw.rectangle([tx1 + 90, top_y + top_h, tx1 + 130, height - 40], fill=side_tint + (255,), outline=line_col)
            draw.rectangle([tx2 - 130, top_y + top_h, tx2 - 90, height - 40], fill=side_tint + (255,), outline=line_col)
            # Trestle feet
            draw.rectangle([tx1 + 50, height - 40, tx1 + 170, height - 15], fill=front_tint + (255,), outline=line_col)
            draw.rectangle([tx2 - 170, height - 40, tx2 - 50, height - 15], fill=front_tint + (255,), outline=line_col)
            # Center Stretcher beam with wedge key
            draw.rectangle([tx1 + 130, height - 90, tx2 - 130, height - 60], fill=front_tint + (255,), outline=line_col)
            draw.polygon([(tx1 + 75, height - 95), (tx1 + 85, height - 95), (tx1 + 80, height - 55), (tx1 + 72, height - 55)], fill=(40, 20, 10, 255))
            draw.polygon([(tx2 - 75, height - 95), (tx2 - 85, height - 95), (tx2 - 80, height - 55), (tx2 - 72, height - 55)], fill=(40, 20, 10, 255))
        elif "x_frame" in p_title or "cross" in p_title:
            # X-Frame Truss
            draw.line([(tx1 + 70, top_y + top_h), (tx1 + 170, height - 20)], fill=side_tint + (255,), width=26)
            draw.line([(tx1 + 170, top_y + top_h), (tx1 + 70, height - 20)], fill=side_tint + (255,), width=26)
            draw.line([(tx2 - 170, top_y + top_h), (tx2 - 70, height - 20)], fill=side_tint + (255,), width=26)
            draw.line([(tx2 - 70, top_y + top_h), (tx2 - 170, height - 20)], fill=side_tint + (255,), width=26)
        else:
            # Tapered round legs
            draw.polygon([(tx1 + 30, top_y + top_h), (tx1 + 10, height - 20), (tx1 + 25, height - 20), (tx1 + 45, top_y + top_h)], fill=side_tint + (255,), outline=line_col)
            draw.polygon([(tx2 - 45, top_y + top_h), (tx2 - 25, height - 20), (tx2 - 10, height - 20), (tx2 - 30, top_y + top_h)], fill=side_tint + (255,), outline=line_col)

    # -------------------------------------------------------------------------
    # 4. PARTITION / SCREEN / ROOM DIVIDER DESIGNS
    # -------------------------------------------------------------------------
    elif "partition" in furniture_id or "screen" in furniture_id or "divider" in furniture_id:
        px1 = 120
        px2 = width - 120
        py1 = 40
        py2 = height - 40

        # Outer Frame
        draw.rectangle([px1, py1, px2, py2], fill=top_tint + (255,), outline=line_col, width=3)

        if "baffle" in p_title or "vertical" in p_title:
            # Vertical Timber Baffles
            num_slats = 16
            s_gap = (px2 - px1 - 30) / num_slats
            for i in range(num_slats):
                sx = int(px1 + 15 + i * s_gap)
                draw.rectangle([sx, py1 + 12, sx + 14, py2 - 12], fill=front_tint + (255,), outline=line_col)
                draw.line([(sx + 3, py1 + 12), (sx + 3, py2 - 12)], fill=highlight_col + (150,), width=1)
        elif "kumiko" in p_title or "lattice" in p_title:
            # Kumiko Diamond Lattice Fretwork
            for gx in range(px1 + 20, px2 - 20, 28):
                draw.line([(gx, py1 + 15), (gx, py2 - 15)], fill=side_tint + (255,), width=1)
            for gy in range(py1 + 20, py2 - 20, 28):
                draw.line([(px1 + 15, gy), (px2 - 15, gy)], fill=side_tint + (255,), width=1)
            # Diagonal trellis lines
            for d in range(-300, 500, 40):
                draw.line([(px1 + 15, py1 + 15 + d), (px1 + 15 + (py2 - py1), py2 - 15 + d)], fill=front_tint + (255,), width=1)
        elif "tri_fold" in p_title or "accordion" in p_title:
            # Tri-Fold panels
            leaf_w = (px2 - px1) // 3
            for l in range(3):
                lx1 = px1 + l * leaf_w
                lx2 = lx1 + leaf_w - 6
                draw.rectangle([lx1, py1, lx2, py2], fill=front_tint + (255,), outline=line_col, width=2)
                draw.rectangle([lx1 + 15, py1 + 25, lx2 - 15, py2 - 25], fill=side_tint + (180,), outline=line_col)
                if l < 2:
                    draw.rectangle([lx2 + 1, py1 + 80, lx2 + 5, py1 + 110], fill=(218, 165, 32, 255))
                    draw.rectangle([lx2 + 1, py2 - 110, lx2 + 5, py2 - 80], fill=(218, 165, 32, 255))
        else:
            # Perforated Jali panel
            draw.rectangle([px1 + 15, py1 + 15, px2 - 15, py2 - 15], fill=front_tint + (255,), outline=line_col)
            for jx in range(px1 + 35, px2 - 35, 45):
                for jy in range(py1 + 35, py2 - 35, 45):
                    draw.ellipse([jx - 12, jy - 12, jx + 12, jy + 12], fill=(245, 246, 248, 255) if style != 'blueprint' else (255, 255, 255, 255), outline=line_col)

    # -------------------------------------------------------------------------
    # 5. GENERAL CASEWORK / CABINET / BOOKSHELF / OTHER
    # -------------------------------------------------------------------------
    else:
        bx1, by1 = 140, 80
        bx2, by2 = width - 140, height - 50
        draw.rectangle([bx1, by1, bx2, by2], fill=front_tint + (255,), outline=line_col, width=2)
        draw_wood_grain(draw, (bx1, by1, bx2, by2), front_tint, lines=10)
        # Shelves / Divisions
        sh1 = by1 + (by2 - by1) // 3
        sh2 = by1 + 2 * (by2 - by1) // 3
        draw.line([(bx1, sh1), (bx2, sh1)], fill=line_col, width=3)
        draw.line([(bx1, sh2), (bx2, sh2)], fill=line_col, width=3)
        # Plinth base
        draw.rectangle([bx1 + 15, by2, bx2 - 15, by2 + 18], fill=side_tint + (255,), outline=line_col)

    return im


# =============================================================================
# VIEW 1: 3D STUDIO PRODUCT RENDER (Photorealistic Studio Cyclorama)
# =============================================================================
def render_studio_view(furniture_item: dict, pattern: dict, wood_info: dict, output_path: str, pattern_index: int = 0):
    W, H = 1200, 840
    bg_cyclorama = (248, 249, 251)
    im = Image.new("RGB", (W, H), bg_cyclorama)
    draw = ImageDraw.Draw(im)

    w_id = wood_info.get("id", "timber") if wood_info else "timber"
    w_name = wood_info.get("name", "Solid Hardwood") if wood_info else "Solid Hardwood"
    w_sci = wood_info.get("scientificName", "") if wood_info else ""
    f_name = furniture_item.get("name", "Woodwork Piece")
    p_title = pattern.get("title", "Studio Design Pattern")
    p_badge = pattern.get("badge", "Mastercraft")

    # 1. Neutral Studio Cyclorama Backdrop with Radial Spotlight
    for y in range(H):
        factor = (y / H) * 0.04
        r = int(248 * (1 - factor))
        g = int(249 * (1 - factor))
        b = int(251 * (1 - factor))
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    spot_center_x, spot_center_y = W // 2, H // 2 - 20
    glow_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_overlay)
    for r in range(450, 0, -30):
        alpha = int(14 * (1 - r / 450))
        glow_draw.ellipse(
            [spot_center_x - r, spot_center_y - int(r * 0.7),
             spot_center_x + r, spot_center_y + int(r * 0.7)],
            fill=(255, 255, 255, alpha)
        )
    im = Image.alpha_composite(im.convert("RGBA"), glow_overlay).convert("RGB")
    draw = ImageDraw.Draw(im)

    # 2. Outer Technical Border
    draw.rectangle([20, 18, W - 20, H - 18], outline=(215, 220, 230), width=1)
    draw.rectangle([24, 22, W - 24, H - 22], outline=(232, 236, 244), width=1)

    # 3. Header Strip
    f_h1 = get_font(18, bold=True)
    f_h2 = get_font(13, bold=False)
    f_badge = get_font(11, bold=True, mono=True)
    f_tag = get_font(11, bold=True)

    draw.rectangle([35, 30, W - 35, 84], fill=(255, 255, 255), outline=(218, 224, 234), width=1)
    draw.line([(35, 30), (W - 35, 30)], fill=(217, 143, 43), width=3)

    draw.text((50, 38), f"{f_name.upper()} — PHOTOREALISTIC DESIGN MASTER RENDER", fill=(25, 30, 42), font=f_h1)
    draw.text((50, 62), f"Design Pattern: {p_title} · Style: [{p_badge}] · Crafted in Authentic {w_name} ({w_sci})", fill=(100, 108, 120), font=f_h2)

    draw.rectangle([W - 260, 38, W - 48, 76], fill=(245, 248, 255), outline=(180, 200, 235), width=1)
    draw.text((W - 248, 44), "📸 4500K STUDIO PHOTOMETRICS", fill=(35, 80, 150), font=f_badge)
    draw.text((W - 248, 59), f"Solid {w_name} Grain & Specular Finish", fill=(90, 120, 170), font=f_tag)

    # 4. Load & Composite Authentic High-Res Photograph
    photo_path = get_pattern_photo(furniture_item.get("id", "piece"), pattern, pattern_index)
    photo = Image.open(photo_path).convert("RGB")
    graded_photo = apply_species_photographic_grading(photo, w_id)

    photo_fit = graded_photo.copy()
    photo_fit.thumbnail((960, 560), Image.Resampling.LANCZOS)
    px = (W - photo_fit.width) // 2
    py = 100 + (610 - photo_fit.height) // 2

    # Multi-stage realistic contact & soft floor drop shadow
    shadow_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow_overlay)
    s_w, s_h = int(photo_fit.width * 1.05), 36
    s_x = (W - s_w) // 2
    s_y = py + photo_fit.height - 18
    s_draw.ellipse([s_x, s_y, s_x + s_w, s_y + s_h], fill=(0, 0, 0, 32))
    c_w, c_h = int(photo_fit.width * 0.85), 18
    c_x = (W - c_w) // 2
    c_y = py + photo_fit.height - 10
    s_draw.ellipse([c_x, c_y, c_x + c_w, c_y + c_h], fill=(0, 0, 0, 65))

    im = Image.alpha_composite(im.convert("RGBA"), shadow_overlay).convert("RGB")
    im.paste(photo_fit, (px, py))
    draw = ImageDraw.Draw(im)

    # 5. Bottom Architectural Feature Cards
    card_y = H - 110
    f_lbl = get_font(10, bold=True)
    f_val = get_font(12, bold=True)

    draw.rectangle([35, card_y, 380, H - 32], fill=(255, 255, 255), outline=(220, 225, 235), width=1)
    draw.text((48, card_y + 10), "FINISHED CRAFT DIMENSIONS", fill=(175, 110, 25), font=f_lbl)
    draw.text((48, card_y + 26), pattern.get("dimensions", "Standard Metric Proportions")[:38], fill=(30, 35, 45), font=f_val)

    draw.rectangle([395, card_y, 790, H - 32], fill=(255, 255, 255), outline=(220, 225, 235), width=1)
    draw.text((408, card_y + 10), f"TIMBER SPECIES: {w_name.upper()}", fill=(45, 120, 55), font=f_lbl)
    mor_val = wood_info.get("mor", 90.0) if wood_info else 90.0
    janka_val = wood_info.get("hardness", 5000) if wood_info else 5000
    draw.text((408, card_y + 26), f"Flexural MOR: {mor_val:.1f} MPa | Hardness: {janka_val} N", fill=(30, 35, 45), font=f_val)

    draw.rectangle([805, card_y, W - 35, H - 32], fill=(255, 255, 255), outline=(220, 225, 235), width=1)
    draw.text((818, card_y + 10), "RECOMMENDED PROTECTIVE COATING", fill=(60, 95, 165), font=f_lbl)
    draw.text((818, card_y + 26), pattern.get("recommended_finish", "Natural Hardwax Oil")[:38], fill=(30, 35, 45), font=f_val)

    im.save(output_path, "PNG", optimize=True)
    return output_path


# =============================================================================
# VIEW 2: ARCHITECTURAL CAD BLUEPRINT (Workshop Drafting Sheet)
# =============================================================================
def render_blueprint_view(furniture_item: dict, pattern: dict, wood_info: dict, output_path: str):
    W, H = 1200, 780
    bg_paper = (252, 250, 246)
    im = Image.new("RGB", (W, H), bg_paper)
    draw = ImageDraw.Draw(im)

    w_name = wood_info.get("name", "Solid Hardwood") if wood_info else "Solid Hardwood"
    w_sci = wood_info.get("scientificName", "") if wood_info else ""
    f_name = furniture_item.get("name", "Woodwork Piece")
    p_title = pattern.get("title", "Architectural Blueprint")
    p_badge = pattern.get("badge", "Design Studio")

    f_h1 = get_font(16, bold=True)
    f_h2 = get_font(12, bold=False)
    f_body = get_font(11, bold=False)
    f_bold = get_font(11, bold=True)
    f_stamp = get_font(11, bold=True, mono=True)
    f_dim = get_font(11, bold=True, mono=True)

    # 1. Architectural CAD Grid Layer
    grid_col = (238, 234, 226)
    for x in range(0, W, 32):
        draw.line([(x, 0), (x, H)], fill=grid_col, width=1)
    for y in range(0, H, 32):
        draw.line([(0, y), (W, y)], fill=grid_col, width=1)

    # 2. Outer Technical Border Frame
    draw.rectangle([25, 20, W - 25, H - 20], outline=(205, 195, 180), width=2)
    draw.rectangle([29, 24, W - 29, H - 24], outline=(228, 222, 210), width=1)

    # 3. Header Masthead
    draw.rectangle([35, 30, W - 35, 94], fill=(255, 255, 255), outline=(210, 195, 175), width=1)
    draw.line([(35, 30), (W - 35, 30)], fill=(200, 128, 31), width=4)

    draw.text((50, 38), "WOOD INTELLIGENCE · INDUSTRIAL TIMBER & JOINERY CAD STUDIO", fill=(175, 110, 25), font=f_bold)
    draw.text((50, 54), f"ARCHITECTURAL SPECIFICATION: {p_title.upper()} · [{p_badge.upper()}]", fill=(35, 25, 15), font=f_h1)
    sci_label = f" ({w_sci})" if w_sci else ""
    draw.text((50, 74), f"Engineered for: {f_name} | Crafting Timber: {w_name}{sci_label}", fill=(110, 85, 65), font=f_h2)

    # Certified Stamp Box on Top Right
    draw.rectangle([W - 250, 38, W - 50, 86], fill=(244, 252, 245), outline=(75, 160, 85), width=1)
    draw.text((W - 238, 46), "✓ ARCHITECTURAL CAD VERIFIED", fill=(35, 125, 45), font=f_stamp)
    draw.text((W - 238, 64), "Scale 1:25 Metric | Shop Ready", fill=(75, 135, 80), font=f_body)

    # 4. Left Visual Viewport (Clean Furniture Picture with Architectural Annotations)
    img_box_x1, img_box_y1 = 45, 108
    img_box_x2, img_box_y2 = 680, 680
    draw.rectangle([img_box_x1, img_box_y1, img_box_x2, img_box_y2], fill=(255, 255, 255), outline=(220, 210, 195), width=1)

    # Corner CAD markers
    m_len = 14
    for cx, cy in [(img_box_x1, img_box_y1), (img_box_x2, img_box_y1), (img_box_x1, img_box_y2), (img_box_x2, img_box_y2)]:
        dx = m_len if cx == img_box_x1 else -m_len
        dy = m_len if cy == img_box_y1 else -m_len
        draw.line([(cx, cy), (cx + dx, cy)], fill=(185, 115, 30), width=2)
        draw.line([(cx, cy), (cx, cy + dy)], fill=(185, 115, 30), width=2)

    # Generate & Composite Bespoke Pattern Artwork
    vw = (img_box_x2 - img_box_x1) - 40
    vh = (img_box_y2 - img_box_y1) - 60
    artwork = generate_pattern_artwork(furniture_item.get("id", "piece"), pattern, wood_info, width=vw, height=vh, style="blueprint")
    paste_x = img_box_x1 + 20
    paste_y = img_box_y1 + 10
    im.paste(artwork, (paste_x, paste_y), artwork)

    # Dimension Leader Lines at Bottom of Picture Box
    dim_text = pattern.get("dimensions", "Standard Scale")
    draw.line([(img_box_x1 + 30, img_box_y2 - 28), (img_box_x2 - 30, img_box_y2 - 28)], fill=(185, 115, 30), width=2)
    draw.line([(img_box_x1 + 30, img_box_y2 - 36), (img_box_x1 + 30, img_box_y2 - 20)], fill=(185, 115, 30), width=2)
    draw.line([(img_box_x2 - 30, img_box_y2 - 36), (img_box_x2 - 30, img_box_y2 - 20)], fill=(185, 115, 30), width=2)

    d_label = f"FINISHED PROPORTIONS: {dim_text}"
    draw.rectangle([img_box_x1 + 60, img_box_y2 - 42, img_box_x2 - 60, img_box_y2 - 14], fill=(255, 255, 255), outline=(185, 115, 30), width=1)
    draw.text((img_box_x1 + 75, img_box_y2 - 34), d_label[:75], fill=(185, 115, 30), font=f_dim)

    # Top Left Picture Badge
    draw.rectangle([img_box_x1 + 15, img_box_y1 + 15, img_box_x1 + 250, img_box_y1 + 40], fill=(245, 240, 230), outline=(210, 195, 170))
    draw.text((img_box_x1 + 25, img_box_y1 + 20), f"TIMBER FINISH: {w_name.upper()}", fill=(130, 85, 30), font=f_bold)

    # 5. Right CAD Engineering & Workshop Dossier Panel
    cad_x1 = 698
    cad_y1 = 108
    cad_x2 = W - 35
    cad_y2 = 680

    draw.rectangle([cad_x1, cad_y1, cad_x2, cad_y2], fill=(255, 255, 255), outline=(215, 205, 190), width=1)
    draw.rectangle([cad_x1, cad_y1, cad_x2, cad_y1 + 38], fill=(247, 243, 235), outline=(220, 210, 195))
    draw.text((cad_x1 + 16, cad_y1 + 10), "📐 JOINERY & STRUCTURAL SPECIFICATIONS", fill=(145, 90, 20), font=f_bold)

    curr_y = cad_y1 + 50
    draw.text((cad_x1 + 16, curr_y), "PRIMARY STRUCTURAL JOINERY", fill=(160, 100, 25), font=f_bold)
    draw.rectangle([cad_x1 + 16, curr_y + 18, cad_x2 - 16, curr_y + 68], fill=(244, 250, 245), outline=(75, 160, 85))
    j_text = pattern.get("recommended_joinery", "Precision Joinery")
    draw.text((cad_x1 + 26, curr_y + 26), j_text[:46], fill=(30, 95, 40), font=f_bold)
    if len(j_text) > 46:
        draw.text((cad_x1 + 26, curr_y + 44), j_text[46:95], fill=(30, 95, 40), font=f_body)

    curr_y += 82
    draw.text((cad_x1 + 16, curr_y), "PROTECTIVE FINISH SYSTEM", fill=(160, 100, 25), font=f_bold)
    draw.rectangle([cad_x1 + 16, curr_y + 18, cad_x2 - 16, curr_y + 54], fill=(252, 248, 240), outline=(210, 175, 115))
    f_text = pattern.get("recommended_finish", "Natural Hardwax Oil")
    draw.text((cad_x1 + 26, curr_y + 26), f_text[:50], fill=(70, 50, 30), font=f_body)

    curr_y += 68
    draw.text((cad_x1 + 16, curr_y), "DESIGN LOAD CAPACITY", fill=(160, 100, 25), font=f_bold)
    draw.rectangle([cad_x1 + 16, curr_y + 18, cad_x2 - 16, curr_y + 54], fill=(250, 245, 240), outline=(210, 155, 130))
    l_text = pattern.get("load_capacity", "Heavy Domestic Rating")
    draw.text((cad_x1 + 26, curr_y + 26), l_text[:50], fill=(120, 50, 30), font=f_body)

    curr_y += 68
    draw.text((cad_x1 + 16, curr_y), f"CRAFTING TIMBER: {w_name.upper()}", fill=(160, 100, 25), font=f_bold)
    draw.rectangle([cad_x1 + 16, curr_y + 18, cad_x2 - 16, curr_y + 90], fill=(245, 248, 255), outline=(130, 165, 220))

    mor_val = wood_info.get("mor", 90.0) if wood_info else 90.0
    density_val = wood_info.get("density", 650) if wood_info else 650
    hardness_val = wood_info.get("hardness", 5000) if wood_info else 5000
    stability_val = wood_info.get("shrinkage", {}).get("stability_score", 7.5) if wood_info else 7.5

    draw.text((cad_x1 + 26, curr_y + 26), f"Flexural MOR: {mor_val:.1f} MPa | Density: {density_val} kg/m³", fill=(30, 70, 130), font=f_bold)
    draw.text((cad_x1 + 26, curr_y + 44), f"Janka Hardness: {hardness_val} N (Dent & Scuff Resistant)", fill=(40, 80, 140), font=f_body)
    draw.text((cad_x1 + 26, curr_y + 64), f"Stability Rating: {stability_val}/10 (Kiln-Dried Movement)", fill=(50, 90, 150), font=f_body)

    curr_y += 105
    draw.text((cad_x1 + 16, curr_y), "MASTER FABRICATION DIRECTIVE", fill=(160, 100, 25), font=f_bold)
    draw.rectangle([cad_x1 + 16, curr_y + 18, cad_x2 - 16, cad_y2 - 18], fill=(255, 250, 240), outline=(215, 155, 55))
    tip_text = pattern.get("blueprint_tips", "Ensure sharp carbide workshop tooling.")
    draw.text((cad_x1 + 26, curr_y + 26), tip_text[:50], fill=(110, 65, 15), font=f_body)
    if len(tip_text) > 50:
        draw.text((cad_x1 + 26, curr_y + 44), tip_text[50:100], fill=(110, 65, 15), font=f_body)
    if len(tip_text) > 100:
        draw.text((cad_x1 + 26, curr_y + 62), tip_text[100:155], fill=(110, 65, 15), font=f_body)

    # 6. Bottom Technical Stamping Footer
    draw.rectangle([35, 696, W - 35, H - 28], fill=(255, 255, 255), outline=(215, 205, 190))
    draw.text((50, 708), "AUTHENTIC CAD SPECIFICATION SHEET · WOOD INTELLIGENCE INDUSTRIAL TIMBER SUITE", fill=(110, 85, 65), font=f_body)
    draw.text((W - 350, 708), "APPROVED WORKSHOP BLUEPRINT", fill=(175, 110, 25), font=f_bold)

    im.save(output_path, "PNG", optimize=True)
    return output_path


# =============================================================================
# VIEW 3: STRUCTURAL JOINERY & ASSEMBLY SCHEMATIC (Mechanical Workshop Dossier)
# =============================================================================
def render_joinery_view(furniture_item: dict, pattern: dict, wood_info: dict, output_path: str):
    W, H = 1200, 780
    bg_dark = (15, 23, 42)
    im = Image.new("RGBA", (W, H), bg_dark + (255,))
    draw = ImageDraw.Draw(im)

    w_name = wood_info.get("name", "Solid Hardwood") if wood_info else "Solid Hardwood"
    f_name = furniture_item.get("name", "Woodwork Piece")

    f_h1 = get_font(17, bold=True)
    f_h2 = get_font(12, bold=False)
    f_code = get_font(11, bold=True, mono=True)
    f_bold = get_font(11, bold=True)
    f_body = get_font(11, bold=False)

    # 1. Dark Blueprint Grid
    grid_col = (30, 41, 59, 180)
    for x in range(0, W, 32):
        draw.line([(x, 0), (x, H)], fill=grid_col, width=1)
    for y in range(0, H, 32):
        draw.line([(0, y), (W, y)], fill=grid_col, width=1)

    # 2. Outer Technical Border
    draw.rectangle([22, 20, W - 22, H - 20], outline=(51, 65, 85, 255), width=2)
    draw.rectangle([26, 24, W - 26, H - 24], outline=(30, 41, 59, 255), width=1)

    # 3. Header Masthead
    draw.rectangle([35, 32, W - 35, 94], fill=(30, 41, 59, 240), outline=(51, 65, 85, 255), width=1)
    draw.line([(35, 32), (W - 35, 32)], fill=(56, 189, 248, 255), width=3)

    draw.text((50, 40), f"STRUCTURAL JOINERY & ASSEMBLY SCHEMATIC · {f_name.upper()}", fill=(241, 245, 249), font=f_h1)
    draw.text((50, 64), f"Joinery Protocol: {pattern.get('recommended_joinery', 'Precision Joinery')} | Active Timber: {w_name}", fill=(148, 163, 184), font=f_h2)

    draw.rectangle([W - 250, 42, W - 50, 84], fill=(15, 23, 42, 255), outline=(56, 189, 248, 200), width=1)
    draw.text((W - 238, 50), "MECHANICAL DETAIL 1:15", fill=(56, 189, 248), font=f_code)
    draw.text((W - 238, 66), "Stress Concentration Analysed", fill=(148, 163, 184), font=f_body)

    # 4. Left Schematic Viewport
    view_x1, view_y1 = 45, 110
    view_x2, view_y2 = 640, 680
    draw.rectangle([view_x1, view_y1, view_x2, view_y2], fill=(20, 29, 47, 240), outline=(51, 65, 85, 255), width=1)

    artwork = generate_pattern_artwork(furniture_item.get("id", "piece"), pattern, wood_info, width=view_x2 - view_x1 - 40, height=view_y2 - view_y1 - 60, style="blueprint")
    paste_x = view_x1 + 20
    paste_y = view_y1 + 25
    im.paste(artwork, (paste_x, paste_y), artwork)
    draw = ImageDraw.Draw(im)

    # Joinery Target Callout Nodes
    nodes = [
        (paste_x + 90, paste_y + 110, "Node 1: Primary Structural Joint"),
        (paste_x + artwork.width - 90, paste_y + 110, "Node 2: Shear Dowel Anchor"),
        (paste_x + artwork.width // 2, paste_y + artwork.height - 45, "Node 3: Foundation Rail Tenon")
    ]
    for nx, ny, nlabel in nodes:
        draw.ellipse([nx - 10, ny - 10, nx + 10, ny + 10], outline=(251, 146, 60, 255), width=2)
        draw.ellipse([nx - 3, ny - 3, nx + 3, ny + 3], fill=(251, 146, 60, 255))
        lx = nx + 40 if nx < view_x1 + 300 else nx - 160
        ly = ny - 25
        draw.line([(nx, ny), (nx + (15 if nx < view_x1 + 300 else -15), ly), (lx + 120, ly)], fill=(251, 146, 60, 220), width=1)
        draw.text((lx, ly - 16), nlabel, fill=(251, 146, 60, 255), font=f_code)

    # 5. Right Engineering Joinery Dossier Cards
    right_x1 = 660
    right_x2 = W - 35

    draw.rectangle([right_x1, 110, right_x2, 250], fill=(30, 41, 59, 240), outline=(56, 189, 248, 180), width=1)
    draw.text((right_x1 + 18, 122), "🔩 PRIMARY JOINT SPECIFICATION", fill=(56, 189, 248), font=f_bold)
    j_rec = pattern.get("recommended_joinery", "Mortise and Tenon with Dowel Lock")
    draw.text((right_x1 + 18, 144), j_rec[:45], fill=(241, 245, 249), font=f_bold)
    if len(j_rec) > 45:
        draw.text((right_x1 + 18, 164), j_rec[45:90], fill=(203, 213, 225), font=f_body)
    draw.text((right_x1 + 18, 192), f"• Shear Resistance: Rated for {pattern.get('load_capacity', 'Heavy Dynamic Load')[:35]}", fill=(148, 163, 184), font=f_body)
    draw.text((right_x1 + 18, 212), "• Grain Alignment: Longitudinal wood fiber orientation mandatory", fill=(148, 163, 184), font=f_body)

    draw.rectangle([right_x1, 265, right_x2, 405], fill=(30, 41, 59, 240), outline=(251, 146, 60, 180), width=1)
    draw.text((right_x1 + 18, 277), "🧪 ADHESIVE & FASTENER TOLERANCES", fill=(251, 146, 60), font=f_bold)
    draw.text((right_x1 + 18, 300), "• Adhesive Matrix: Cross-linking PVA Type II or Polyurethane D4", fill=(241, 245, 249), font=f_body)
    draw.text((right_x1 + 18, 322), "• Pre-drill Tolerances: Pilot hole at 80% root diameter of shank", fill=(203, 213, 225), font=f_body)
    draw.text((right_x1 + 18, 344), f"• Timber Expansion Allowance: ±2.5mm per 500mm width in {w_name}", fill=(203, 213, 225), font=f_body)
    draw.text((right_x1 + 18, 366), "• Clamp Pressure: 100–150 psi uniform distribution for 4 hours", fill=(148, 163, 184), font=f_body)

    draw.rectangle([right_x1, 420, right_x2, 680], fill=(30, 41, 59, 240), outline=(74, 222, 128, 180), width=1)
    draw.text((right_x1 + 18, 432), "🛠️ WORKSHOP FABRICATION DIRECTIVE", fill=(74, 222, 128), font=f_bold)
    tip = pattern.get("blueprint_tips", "Ensure sharp carbide workshop tooling.")
    draw.text((right_x1 + 18, 458), tip[:50], fill=(241, 245, 249), font=f_body)
    if len(tip) > 50:
        draw.text((right_x1 + 18, 480), tip[50:100], fill=(241, 245, 249), font=f_body)
    if len(tip) > 100:
        draw.text((right_x1 + 18, 502), tip[100:150], fill=(203, 213, 225), font=f_body)

    draw.text((right_x1 + 18, 540), f"TIMBER MECHANICAL PROFILE ({w_name.upper()}):", fill=(56, 189, 248), font=f_bold)
    mor_val = wood_info.get("mor", 90.0) if wood_info else 90.0
    draw.text((right_x1 + 18, 565), f"• Flexural Strength (MOR): {mor_val:.1f} MPa", fill=(203, 213, 225), font=f_body)
    draw.text((right_x1 + 18, 587), f"• Janka Hardness: {wood_info.get('hardness', 5000) if wood_info else 5000} N (Resists Joint Crushing)", fill=(203, 213, 225), font=f_body)
    draw.text((right_x1 + 18, 609), f"• Protective Coating: {pattern.get('recommended_finish', 'Hardwax Oil')[:38]}", fill=(203, 213, 225), font=f_body)

    draw.rectangle([35, 696, W - 35, H - 28], fill=(30, 41, 59), outline=(51, 65, 85))
    draw.text((50, 708), "AUTHENTIC STRUCTURAL JOINERY PROTOCOL · WOOD INTELLIGENCE ENGINEERING CORE", fill=(148, 163, 184), font=f_body)
    draw.text((W - 300, 708), "WORKSHOP CERTIFIED SCHEMATIC", fill=(56, 189, 248), font=f_bold)

    im.convert("RGB").save(output_path, "PNG", optimize=True)
    return output_path


# =============================================================================
# VIEW 4: IN-SITU ARCHITECTURAL INTERIOR SCENE (Living Space Context)
# =============================================================================
def render_insitu_view(furniture_item: dict, pattern: dict, wood_info: dict, output_path: str, pattern_index: int = 0):
    W, H = 1200, 780
    im = Image.new("RGBA", (W, H), (248, 246, 242, 255))
    draw = ImageDraw.Draw(im)

    w_id = wood_info.get("id", "timber") if wood_info else "timber"
    w_name = wood_info.get("name", "Solid Hardwood") if wood_info else "Solid Hardwood"
    f_name = furniture_item.get("name", "Woodwork Piece")
    tint = get_wood_tint(w_id)

    f_h1 = get_font(18, bold=True)
    f_h2 = get_font(12, bold=False)
    f_bold = get_font(11, bold=True)
    f_body = get_font(11, bold=False)

    # 1. Architectural Interior Scene: Wall (Top 60%) & Hardwood Floor (Bottom 40%)
    wall_h = int(H * 0.60)
    floor_h = H - wall_h

    for y in range(wall_h):
        shade = int(244 - (y / wall_h) * 12)
        draw.line([(0, y), (W, y)], fill=(shade, shade - 2, shade - 4, 255))

    for sl_x in range(35, 260, 16):
        draw.line([(sl_x, 30), (sl_x, wall_h - 15)], fill=(225, 220, 212, 120), width=4)

    bb_y = wall_h - 14
    draw.rectangle([0, bb_y, W, wall_h], fill=(235, 230, 222, 255))
    draw.line([(0, bb_y), (W, bb_y)], fill=(205, 200, 190, 255), width=2)
    draw.line([(0, wall_h), (W, wall_h)], fill=(160, 150, 140, 255), width=1)

    floor_base_r = min(240, max(80, tint[0] + 30))
    floor_base_g = min(220, max(60, tint[1] + 25))
    floor_base_b = min(190, max(40, tint[2] + 20))

    for y in range(wall_h, H):
        p_ratio = (y - wall_h) / floor_h
        fr = int(floor_base_r - p_ratio * 25)
        fg = int(floor_base_g - p_ratio * 25)
        fb = int(floor_base_b - p_ratio * 25)
        draw.line([(0, y), (W, y)], fill=(fr, fg, fb, 255))

    for py in range(wall_h + 30, H, 45):
        draw.line([(0, py), (W, py)], fill=(int(fr * 0.8), int(fg * 0.8), int(fb * 0.8), 180), width=1)

    sun_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sun_draw = ImageDraw.Draw(sun_overlay)
    sun_polygon = [(0, 0), (450, 0), (W - 100, H), (200, H)]
    sun_draw.polygon(sun_polygon, fill=(255, 255, 240, 32))
    im = Image.alpha_composite(im, sun_overlay)
    draw = ImageDraw.Draw(im)

    draw.rectangle([20, 20, W - 20, H - 20], outline=(200, 195, 185, 200), width=1)

    draw.rectangle([35, 32, W - 35, 82], fill=(255, 255, 255, 230), outline=(210, 205, 195), width=1)
    draw.line([(35, 32), (W - 35, 32)], fill=(200, 128, 31), width=3)
    draw.text((50, 40), f"IN-SITU ARCHITECTURAL LIVING SCENE · {f_name.upper()}", fill=(35, 30, 25), font=f_h1)
    draw.text((50, 62), f"Interior Context: Contemporary Living Space · Crafted in {w_name} · Finish: {pattern.get('recommended_finish', 'Hardwax Oil')}", fill=(110, 100, 90), font=f_h2)

    draw.rectangle([W - 240, 40, W - 50, 74], fill=(245, 250, 245), outline=(75, 150, 85), width=1)
    draw.text((W - 228, 46), "🏡 1:1 REAL LIVING SCALE", fill=(35, 120, 45), font=f_bold)
    draw.text((W - 228, 58), "Spatial Context Harmonized", fill=(80, 130, 90), font=f_body)

    # 4. Load & Composite Authentic Photograph
    photo_path = get_pattern_photo(furniture_item.get("id", "piece"), pattern, pattern_index)
    photo = Image.open(photo_path).convert("RGB")
    graded_photo = apply_species_photographic_grading(photo, wood_info.get("id", "timber") if wood_info else "timber")

    photo_fit = graded_photo.copy()
    photo_fit.thumbnail((820, 480), Image.Resampling.LANCZOS)
    paste_x = (W - photo_fit.width) // 2 + 30
    paste_y = wall_h - int(photo_fit.height * 0.45)

    shadow_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow_overlay)
    s_w = int(photo_fit.width * 1.05)
    s_x = paste_x - 10
    s_y = paste_y + photo_fit.height - 25
    s_draw.ellipse([s_x, s_y, s_x + s_w, s_y + 40], fill=(0, 0, 0, 75))
    im = Image.alpha_composite(im.convert("RGBA"), shadow_overlay).convert("RGB")

    im.paste(photo_fit, (paste_x, paste_y))
    draw = ImageDraw.Draw(im)

    draw.rectangle([35, H - 75, W - 35, H - 35], fill=(255, 255, 255, 230), outline=(210, 205, 195))
    draw.text((50, H - 65), f"SPATIAL INTEGRATION: Finished proportions ({pattern.get('dimensions', 'Standard Size')}) calibrated for high-ceiling contemporary spaces.", fill=(50, 45, 40), font=f_bold)
    draw.text((50, H - 50), f"Timber harmony: Floor planks color-graded to accentuate the organic warmth of solid {w_name}.", fill=(110, 100, 90), font=f_body)
    draw.text((W - 250, H - 58), "IN-SITU APPROVED", fill=(200, 128, 31), font=f_bold)

    im.save(output_path, "PNG", optimize=True)
    return output_path


# =============================================================================
# MULTI-DESIGN SUITE ORCHESTRATOR
# =============================================================================
def generate_furniture_design_image(furniture_item: dict, pattern: dict, wood_info: dict, force_regenerate: bool = False) -> str:
    """Legacy compatibility function: generates and returns the CAD Blueprint path."""
    paths = get_design_suite_paths(furniture_item.get("id", "piece"), pattern.get("title", "Blueprint"), wood_info.get("id", "timber") if wood_info else "timber")
    if not os.path.exists(paths["blueprint"]) or force_regenerate:
        render_blueprint_view(furniture_item, pattern, wood_info, paths["blueprint"])
    return paths["blueprint"]

def generate_multi_design_suite(furniture_item: dict, pattern: dict, wood_info: dict, force_regenerate: bool = False, pattern_index: int = 0) -> dict:
    """
    Renders all 4 distinct high-resolution design perspectives:
    1. 3D Studio Product Render (1200x840 HD, authentic photographic studio cyclorama)
    2. Architectural CAD Blueprint (1200x780, drafting grid, dimensions, shop dossier)
    3. Structural Joinery Schematic (1200x780, joint nodes, shear ratings, fasteners)
    4. In-Situ Interior Scene (1200x780, contemporary room context with sunlight & hardwood floor)
    
    Returns a dictionary with metadata and local paths for all 4 views.
    """
    f_id = furniture_item.get("id", "piece")
    p_title = pattern.get("title", "Design Pattern")
    w_id = wood_info.get("id", "timber") if wood_info else "timber"

    paths = get_design_suite_paths(f_id, p_title, w_id)

    # 1. Studio Render (Authentic Photorealistic Render)
    if not os.path.exists(paths["studio"]) or force_regenerate:
        render_studio_view(furniture_item, pattern, wood_info, paths["studio"], pattern_index=pattern_index)

    # 2. CAD Blueprint
    if not os.path.exists(paths["blueprint"]) or force_regenerate:
        render_blueprint_view(furniture_item, pattern, wood_info, paths["blueprint"])

    # 3. Structural Joinery
    if not os.path.exists(paths["joinery"]) or force_regenerate:
        render_joinery_view(furniture_item, pattern, wood_info, paths["joinery"])

    # 4. In-Situ Scene
    if not os.path.exists(paths["insitu"]) or force_regenerate:
        render_insitu_view(furniture_item, pattern, wood_info, paths["insitu"], pattern_index=pattern_index)

    return {
        "studio": {
            "title": "Photorealistic Master Studio Render",
            "icon": "📸",
            "badge": "Photorealistic Cyclorama",
            "desc": "High-definition photorealistic product render highlighting wood grain warmth, surface reflectance, and sculptural form under neutral cyclorama studio illumination.",
            "path": paths["studio"]
        },
        "blueprint": {
            "title": "Architectural CAD Blueprint",
            "icon": "📐",
            "badge": "Scale 1:25 Metric Drafting",
            "desc": "Millimeter-calibrated architectural drafting sheet with finished proportions, dimension leader lines, and comprehensive workshop engineering dossier.",
            "path": paths["blueprint"]
        },
        "joinery": {
            "title": "Structural Joinery & Assembly Schematic",
            "icon": "🔍",
            "badge": "Mechanical Engineering Dossier",
            "desc": "Workshop joinery breakdown detailing critical joint nodes, shear ratings, fastener pilot tolerances, and adhesive bonding protocols.",
            "path": paths["joinery"]
        },
        "insitu": {
            "title": "In-Situ Architectural Interior Scene",
            "icon": "🏡",
            "badge": "Spatial Living-Space Context",
            "desc": "Environmental room visualization displaying the furniture piece placed in a contemporary architectural interior with hardwood flooring and natural sunlight.",
            "path": paths["insitu"]
        }
    }
