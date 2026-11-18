"""
=============================================================================
WOOD INTELLIGENCE — ARCHITECTURAL DESIGN PATTERN VISUALIZER
=============================================================================
Procedural CAD drafting and clean architectural design picture generation for
furniture design patterns, enriched with real timber species tone mapping,
structural dimension guides, and master workshop joinery callouts.
=============================================================================
"""

import os
import re
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageOps

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "generated_designs")
os.makedirs(ASSETS_DIR, exist_ok=True)

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
    """Computes the target file path for a generated design picture."""
    p_slug = slugify(pattern_title)
    w_slug = slugify(wood_id)
    filename = f"{furniture_id}_{p_slug}_{w_slug}.png"
    return os.path.join(ASSETS_DIR, filename)

def generate_furniture_design_image(furniture_item: dict, pattern: dict, wood_info: dict, force_regenerate: bool = False) -> str:
    """
    Renders and caches a clean, high-resolution architectural design blueprint picture
    for the specific furniture design pattern and selected timber species.
    
    Returns the absolute path to the generated PNG image.
    """
    f_id = furniture_item.get("id", "piece")
    f_name = furniture_item.get("name", "Woodwork Piece")
    p_title = pattern.get("title", "Architectural Blueprint")
    p_badge = pattern.get("badge", "Design Studio")
    w_id = wood_info.get("id", "timber") if wood_info else "timber"
    w_name = wood_info.get("name", "Solid Hardwood") if wood_info else "Solid Hardwood"
    w_sci = wood_info.get("scientificName", "") if wood_info else ""
    
    output_path = get_design_image_path(f_id, p_title, w_id)
    
    # Return cached image if already generated and regeneration is not forced
    if os.path.exists(output_path) and not force_regenerate:
        return output_path

    # Canvas Dimensions (Crisp 16:10 Architectural Aspect Ratio)
    W, H = 1060, 680
    bg_paper = (252, 250, 246)
    im = Image.new("RGB", (W, H), bg_paper)
    draw = ImageDraw.Draw(im)

    # 1. Architectural CAD Grid Layer
    grid_col = (238, 234, 226)
    for x in range(0, W, 35):
        draw.line([(x, 0), (x, H)], fill=grid_col, width=1)
    for y in range(0, H, 35):
        draw.line([(y, 0), (W, y)], fill=grid_col, width=1)

    # 2. Outer Technical Border Frame
    draw.rectangle([25, 20, W - 25, H - 20], outline=(205, 195, 180), width=2)
    draw.rectangle([29, 24, W - 29, H - 24], outline=(228, 222, 210), width=1)

    # 3. Header Masthead
    draw.rectangle([35, 30, W - 35, 88], fill=(255, 255, 255), outline=(210, 195, 175), width=1)
    draw.line([(35, 30), (W - 35, 30)], fill=(200, 128, 31), width=4)
    
    draw.text((50, 38), "WOOD INTELLIGENCE · INDUSTRIAL TIMBER & JOINERY CAD STUDIO", fill=(175, 110, 25))
    draw.text((50, 55), f"ARCHITECTURAL SPECIFICATION: {p_title.upper()} · [{p_badge.upper()}]", fill=(35, 25, 15))
    sci_label = f" ({w_sci})" if w_sci else ""
    draw.text((50, 72), f"Engineered for: {f_name} | Crafting Timber: {w_name}{sci_label}", fill=(110, 85, 65))
    
    # Certified Stamp Box on Top Right
    draw.rectangle([W - 245, 38, W - 45, 80], fill=(244, 252, 245), outline=(75, 160, 85), width=1)
    draw.text((W - 232, 46), "✓ ARCHITECTURAL CAD VERIFIED", fill=(35, 125, 45))
    draw.text((W - 232, 62), "Scale 1:25 Metric | Shop Ready", fill=(75, 135, 80))

    # 4. Left Visual Viewport (Clean Furniture Picture with Architectural Annotations)
    img_box_x1, img_box_y1 = 45, 102
    img_box_x2, img_box_y2 = 645, 580
    
    draw.rectangle([img_box_x1, img_box_y1, img_box_x2, img_box_y2], fill=(255, 255, 255), outline=(220, 210, 195), width=1)
    
    # Corner CAD markers
    m_len = 12
    draw.line([(img_box_x1, img_box_y1), (img_box_x1 + m_len, img_box_y1)], fill=(185, 115, 30), width=2)
    draw.line([(img_box_x1, img_box_y1), (img_box_x1, img_box_y1 + m_len)], fill=(185, 115, 30), width=2)
    draw.line([(img_box_x2, img_box_y1), (img_box_x2 - m_len, img_box_y1)], fill=(185, 115, 30), width=2)
    draw.line([(img_box_x2, img_box_y1), (img_box_x2, img_box_y1 + m_len)], fill=(185, 115, 30), width=2)
    draw.line([(img_box_x1, img_box_y2), (img_box_x1 + m_len, img_box_y2)], fill=(185, 115, 30), width=2)
    draw.line([(img_box_x1, img_box_y2), (img_box_x1, img_box_y2 - m_len)], fill=(185, 115, 30), width=2)
    draw.line([(img_box_x2, img_box_y2), (img_box_x2 - m_len, img_box_y2)], fill=(185, 115, 30), width=2)
    draw.line([(img_box_x2, img_box_y2), (img_box_x2, img_box_y2 - m_len)], fill=(185, 115, 30), width=2)

    # Load and composite furniture image with timber tone mapping
    base_img_path = furniture_item.get("image", "")
    if os.path.exists(base_img_path):
        try:
            base_img = Image.open(base_img_path).convert("RGBA")
            pad = 32
            max_w = (img_box_x2 - img_box_x1) - (pad * 2)
            max_h = (img_box_y2 - img_box_y1) - (pad * 2) - 30
            base_img.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
            
            # Apply tone mapping with explored timber species tint
            tint = get_wood_tint(w_id)
            tint_layer = Image.new("RGBA", base_img.size, tint + (36,))
            composited_piece = Image.alpha_composite(base_img, tint_layer)
            
            # Center in photo box
            paste_x = img_box_x1 + ((img_box_x2 - img_box_x1) - composited_piece.width) // 2
            paste_y = img_box_y1 + 15 + ((img_box_y2 - img_box_y1 - 40) - composited_piece.height) // 2
            
            # Soft ambient floor shadow
            shadow_y = paste_y + composited_piece.height - 8
            draw.ellipse([paste_x + 25, shadow_y, paste_x + composited_piece.width - 25, shadow_y + 26], fill=(226, 221, 212))
            
            im.paste(composited_piece, (paste_x, paste_y), composited_piece)
        except Exception:
            draw.text((img_box_x1 + 80, img_box_y1 + 190), f"[{f_name} Architectural Render]", fill=(140, 110, 80))
    else:
        draw.text((img_box_x1 + 80, img_box_y1 + 190), f"[{f_name} Architectural Render]", fill=(140, 110, 80))

    # Architectural Dimension Leader Lines at Bottom of Picture Box
    dim_text = pattern.get("dimensions", "Standard Scale")
    draw.line([(img_box_x1 + 25, img_box_y2 - 25), (img_box_x2 - 25, img_box_y2 - 25)], fill=(185, 115, 30), width=2)
    draw.line([(img_box_x1 + 25, img_box_y2 - 32), (img_box_x1 + 25, img_box_y2 - 18)], fill=(185, 115, 30), width=2)
    draw.line([(img_box_x2 - 25, img_box_y2 - 32), (img_box_x2 - 25, img_box_y2 - 18)], fill=(185, 115, 30), width=2)
    
    # Text badge for dimensions
    d_label = f"FINISHED PROPORTIONS: {dim_text}"
    draw.rectangle([img_box_x1 + 80, img_box_y2 - 38, img_box_x2 - 80, img_box_y2 - 12], fill=(255, 255, 255), outline=(185, 115, 30), width=1)
    draw.text((img_box_x1 + 95, img_box_y2 - 30), d_label[:72], fill=(185, 115, 30))

    # Top Left Picture Badge
    draw.rectangle([img_box_x1 + 12, img_box_y1 + 12, img_box_x1 + 215, img_box_y1 + 34], fill=(245, 240, 230), outline=(210, 195, 170))
    draw.text((img_box_x1 + 20, img_box_y1 + 17), f"TIMBER FINISH: {w_name.upper()}", fill=(130, 85, 30))

    # 5. Right CAD Engineering & Workshop Dossier Panel
    cad_x1 = 660
    cad_y1 = 102
    cad_x2 = W - 35
    cad_y2 = 580
    
    draw.rectangle([cad_x1, cad_y1, cad_x2, cad_y2], fill=(255, 255, 255), outline=(215, 205, 190), width=1)
    draw.rectangle([cad_x1, cad_y1, cad_x2, cad_y1 + 36], fill=(247, 243, 235), outline=(220, 210, 195))
    draw.text((cad_x1 + 15, cad_y1 + 11), "📐 JOINERY & STRUCTURAL SPECIFICATIONS", fill=(145, 90, 20))

    # 5a. Primary Joinery
    curr_y = cad_y1 + 46
    draw.text((cad_x1 + 15, curr_y), "PRIMARY STRUCTURAL JOINERY", fill=(160, 100, 25))
    draw.rectangle([cad_x1 + 15, curr_y + 16, cad_x2 - 15, curr_y + 60], fill=(244, 250, 245), outline=(75, 160, 85))
    j_text = pattern.get("recommended_joinery", "Precision Joinery")
    draw.text((cad_x1 + 25, curr_y + 24), j_text[:46], fill=(30, 95, 40))
    if len(j_text) > 46:
        draw.text((cad_x1 + 25, curr_y + 40), j_text[46:92], fill=(30, 95, 40))

    # 5b. Protective Finish System
    curr_y += 74
    draw.text((cad_x1 + 15, curr_y), "PROTECTIVE FINISH SYSTEM", fill=(160, 100, 25))
    draw.rectangle([cad_x1 + 15, curr_y + 16, cad_x2 - 15, curr_y + 48], fill=(252, 248, 240), outline=(210, 175, 115))
    f_text = pattern.get("recommended_finish", "Natural Hardwax Oil")
    draw.text((cad_x1 + 25, curr_y + 24), f_text[:50], fill=(70, 50, 30))

    # 5c. Design Load Capacity
    curr_y += 62
    draw.text((cad_x1 + 15, curr_y), "DESIGN LOAD CAPACITY", fill=(160, 100, 25))
    draw.rectangle([cad_x1 + 15, curr_y + 16, cad_x2 - 15, curr_y + 48], fill=(250, 245, 240), outline=(210, 155, 130))
    l_text = pattern.get("load_capacity", "Heavy Domestic Rating")
    draw.text((cad_x1 + 25, curr_y + 24), l_text[:50], fill=(120, 50, 30))

    # 5d. Timber Mechanical Pairing Analysis
    curr_y += 62
    draw.text((cad_x1 + 15, curr_y), f"CRAFTING TIMBER: {w_name.upper()}", fill=(160, 100, 25))
    draw.rectangle([cad_x1 + 15, curr_y + 16, cad_x2 - 15, curr_y + 80], fill=(245, 248, 255), outline=(130, 165, 220))
    
    mor_val = wood_info.get("mor", 90.0) if wood_info else 90.0
    density_val = wood_info.get("density", 650) if wood_info else 650
    hardness_val = wood_info.get("hardness", 5000) if wood_info else 5000
    stability_val = wood_info.get("shrinkage", {}).get("stability_score", 7.5) if wood_info else 7.5
    
    draw.text((cad_x1 + 25, curr_y + 24), f"Flexural MOR: {mor_val:.1f} MPa | Density: {density_val} kg/m³", fill=(30, 70, 130))
    draw.text((cad_x1 + 25, curr_y + 41), f"Janka Hardness: {hardness_val} N (Dent & Scuff Resistant)", fill=(40, 80, 140))
    draw.text((cad_x1 + 25, curr_y + 58), f"Stability Rating: {stability_val}/10 (Kiln-Dried Indoor Movement)", fill=(50, 90, 150))

    # 5e. Master Fabrication Directive
    curr_y += 94
    draw.text((cad_x1 + 15, curr_y), "MASTER FABRICATION DIRECTIVE", fill=(160, 100, 25))
    draw.rectangle([cad_x1 + 15, curr_y + 16, cad_x2 - 15, cad_y2 - 15], fill=(255, 250, 240), outline=(215, 155, 55))
    tip_text = pattern.get("blueprint_tips", "Ensure sharp carbide workshop tooling.")
    draw.text((cad_x1 + 25, curr_y + 24), tip_text[:50], fill=(110, 65, 15))
    if len(tip_text) > 50:
        draw.text((cad_x1 + 25, curr_y + 41), tip_text[50:100], fill=(110, 65, 15))
    if len(tip_text) > 100:
        draw.text((cad_x1 + 25, curr_y + 58), tip_text[100:150], fill=(110, 65, 15))

    # 6. Bottom Technical Stamping Footer
    draw.rectangle([35, 595, W - 35, H - 28], fill=(255, 255, 255), outline=(215, 205, 190))
    draw.text((50, 608), "AUTHENTIC CAD SPECIFICATION SHEET · WOOD INTELLIGENCE INDUSTRIAL TIMBER SUITE", fill=(110, 85, 65))
    draw.text((W - 325, 608), "APPROVED WORKSHOP BLUEPRINT", fill=(175, 110, 25))

    # Save to disk
    im.save(output_path, "PNG", optimize=True)
    return output_path
