"""
=============================================================================
WOOD INTELLIGENCE — MULTI-PERSPECTIVE ARCHITECTURAL DESIGN VISUALIZER
=============================================================================
Bespoke architectural furniture visualization engine powered by Generative AI
(Google Imagen 3 & OpenAI Image Models) with fallback to dynamic high-definition
Photographic Atelier variations calibrated to camera perspectives, studio lighting,
timber finishes, and authentic species tone mapping.
=============================================================================
"""

import os
import re
import io
import json
import base64
import urllib.request
import urllib.error
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageOps, ImageFilter

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "generated_designs")
os.makedirs(ASSETS_DIR, exist_ok=True)

ROOT_PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ASSETS_DIR = os.path.join(ROOT_PROJECT_DIR, "assets")

# Authentic color grading palettes for all commercial timbers in Wood Intelligence
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

def get_design_suite_paths(furniture_id: str, pattern_title: str, wood_id: str) -> dict:
    """Returns paths for design views in the design suite."""
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
    """Returns True if the primary master studio view exists on disk."""
    paths = get_design_suite_paths(furniture_id, pattern_title, wood_id)
    return os.path.exists(paths["studio"])

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
    direct_jpg = os.path.join(PROJECT_ASSETS_DIR, "furniture_patterns", f"{furniture_id}_{pattern_index}.jpg")
    if os.path.exists(direct_jpg):
        return direct_jpg
    direct_png = os.path.join(PROJECT_ASSETS_DIR, "furniture_patterns", f"{furniture_id}_{pattern_index}.png")
    if os.path.exists(direct_png):
        return direct_png

    candidates = [
        os.path.join(PROJECT_ASSETS_DIR, "furniture_patterns", f"{furniture_id}_0.jpg"),
        os.path.join(PROJECT_ASSETS_DIR, "furniture", f"{furniture_id}.jpg"),
        os.path.join(PROJECT_ASSETS_DIR, "furniture", f"{furniture_id}.webp"),
        os.path.join(PROJECT_ASSETS_DIR, "furniture", f"{furniture_id}.png")
    ]

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
# 1. GENERATIVE AI ENGINE (Google Imagen 3 & OpenAI Image API)
# =============================================================================
def generate_ai_furniture_image(
    furniture_item: dict,
    pattern: dict,
    wood_info: dict,
    api_key: str = None,
    perspective: str = "Hero Three-Quarter",
    lighting: str = "4500K Neutral Studio",
    finish: str = "Natural Hardwax Oil",
    custom_prompt: str = "",
    seed: int = 1
) -> tuple:
    """
    Calls Google Imagen 3 or OpenAI Image API to generate a brand-new, unique,
    photorealistic 8K architectural product photograph matching the selected options.
    
    Returns (PIL.Image, provider_name_or_error_str).
    """
    f_name = furniture_item.get("name", "Furniture Piece")
    p_title = pattern.get("title", "Contemporary Architectural Design")
    w_name = wood_info.get("name", "Solid Hardwood") if wood_info else "Solid Hardwood"
    w_sci = wood_info.get("scientificName", "") if wood_info else ""
    p_joinery = pattern.get("recommended_joinery", "traditional mortise and tenon")

    prompt_parts = [
        f"A hyper-realistic, award-winning 8k architectural product photograph of a {p_title} ({f_name}).",
        f"Expertly handcrafted from solid {w_name} timber ({w_sci}).",
        f"Camera perspective: {perspective}.",
        f"Studio illumination: {lighting}.",
        f"Timber surface: {finish} with authentic natural wood grain and precision {p_joinery} joinery."
    ]
    if custom_prompt and custom_prompt.strip():
        prompt_parts.append(f"Architectural directive: {custom_prompt.strip()}.")
    prompt_parts.append(f"Exhibition catalog photography, sharp focus, 8k resolution, architectural digest, seed {seed}.")
    prompt = " ".join(prompt_parts)

    key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not key:
        env_path = os.path.join(ROOT_PROJECT_DIR, ".env")
        if os.path.exists(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if "=" in line and not line.strip().startswith("#"):
                            k, v = line.strip().split("=", 1)
                            if k.strip() in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "OPENAI_API_KEY"):
                                key = v.strip("'\" \r\n")
                                break
            except Exception:
                pass

    if not key:
        return None, "No API key configured"

    # 1. Google Gemini / Imagen 3 API
    if key.startswith("AIza") or (len(key) == 39 and not key.startswith("sk-")):
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict?key={key}"
            payload = {
                "instances": [{"prompt": prompt}],
                "parameters": {
                    "sampleCount": 1,
                    "aspectRatio": "1:1",
                    "outputMimeType": "image/jpeg"
                }
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                predictions = result.get("predictions", [])
                if predictions and "bytesBase64Encoded" in predictions[0]:
                    img_data = base64.b64decode(predictions[0]["bytesBase64Encoded"])
                    im = Image.open(io.BytesIO(img_data)).convert("RGB")
                    return im, "Google Imagen 3"
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            return None, f"Google Imagen API ({e.code}): {err_body[:100]}"
        except Exception as e:
            return None, f"Google Imagen error: {e}"

    # 2. OpenAI Image Generation API
    if key.startswith("sk-"):
        models_to_try = ["chatgpt-image-latest", "gpt-image-1.5", "gpt-image-1-mini", "dall-e-3", "dall-e-2"]
        last_error = ""
        for mod in models_to_try:
            try:
                url = "https://api.openai.com/v1/images/generations"
                payload = {
                    "model": mod,
                    "prompt": prompt,
                    "n": 1,
                    "size": "1024x1024"
                }
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {key}"
                    }
                )
                with urllib.request.urlopen(req, timeout=35) as resp:
                    result = json.loads(resp.read().decode("utf-8"))
                    data = result.get("data", [])
                    if data:
                        first_item = data[0]
                        if "b64_json" in first_item:
                            img_data = base64.b64decode(first_item["b64_json"])
                            im = Image.open(io.BytesIO(img_data)).convert("RGB")
                            return im, f"OpenAI ({mod})"
                        elif "url" in first_item:
                            img_url = first_item["url"]
                            img_req = urllib.request.Request(img_url, headers={"User-Agent": "Mozilla/5.0"})
                            with urllib.request.urlopen(img_req, timeout=20) as img_resp:
                                im = Image.open(io.BytesIO(img_resp.read())).convert("RGB")
                                return im, f"OpenAI ({mod})"
            except urllib.error.HTTPError as e:
                err_body = e.read().decode("utf-8", errors="ignore")
                if "insufficient_quota" in err_body or e.code == 429:
                    return None, "OpenAI Quota Exhausted (0 credits remaining on account). Add credits at platform.openai.com or enter a free Google Gemini key."
                last_error = f"OpenAI ({e.code}): {err_body[:100]}"
            except Exception as e:
                last_error = f"OpenAI error: {e}"
        return None, last_error

    return None, "Unrecognized API key type (expected Google AI Studio 'AIza...' or OpenAI 'sk-...')"


# =============================================================================
# 2. DYNAMIC PHOTOGRAPHIC ATELIER VARIATIONS ENGINE
# =============================================================================
def generate_photographic_variation(
    furniture_item: dict,
    pattern: dict,
    wood_info: dict,
    pattern_index: int = 0,
    perspective: str = "Hero Three-Quarter",
    lighting: str = "4500K Neutral Studio",
    finish: str = "Natural Hardwax Oil",
    seed: int = 1
) -> Image.Image:
    """
    Renders a distinct photographic studio variation calibrated dynamically to:
    - Camera perspective (3/4 Isometric, Front Elevation, Side Profile, Macro Grain)
    - Lighting & atmosphere (Neutral 4500K, Nordic Warm Sunlight, Dramatic High-Contrast, Clean High-Key)
    - Timber finish sheen (Hardwax Oil, Danish Amber Oil, Satin Polyurethane, Raw Sawn)
    - Authentic species tone mapping
    - Variation seed
    Guarantees every generation option produces a visibly different, realistic render.
    """
    f_id = furniture_item.get("id", "piece")
    
    # 1. Base photographic model selection
    # Use pattern_index or seed variation to choose distinct model if available
    target_idx = (pattern_index + (seed - 1)) % 4
    photo_path = get_pattern_photo(f_id, pattern, target_idx)
    base_img = Image.open(photo_path).convert("RGB")
    W, H = base_img.size

    # 2. Dynamic Perspective Transformation & Framing
    if "Macro" in perspective or "Close" in perspective:
        # Macro zoom on joinery and timber grain with subtle depth vignette
        cw, ch = int(W * 0.72), int(H * 0.72)
        cx, cy = (W - cw) // 2, int(H * 0.15)
        framed = base_img.crop((cx, cy, cx + cw, cy + ch)).resize((W, H), Image.Resampling.LANCZOS)
    elif "Side" in perspective or "Profile" in perspective:
        # Profile crop with asymmetric framing
        cw, ch = int(W * 0.88), int(H * 0.88)
        cx = int(W * 0.10)
        cy = (H - ch) // 2
        framed = base_img.crop((cx, cy, cx + cw, cy + ch)).resize((W, H), Image.Resampling.LANCZOS)
    elif "Front" in perspective or "Elevation" in perspective:
        # Centered symmetrical framing
        cw, ch = int(W * 0.94), int(H * 0.94)
        cx = (W - cw) // 2
        cy = (H - ch) // 2
        framed = base_img.crop((cx, cy, cx + cw, cy + ch)).resize((W, H), Image.Resampling.LANCZOS)
    else:
        # Standard Hero 3/4 Isometric framing
        framed = base_img.copy()

    # 3. Dynamic Studio Lighting Grading
    if "Warm" in lighting or "Nordic" in lighting or "Golden" in lighting:
        # Warm golden-hour daylight grading
        enh_col = ImageEnhance.Color(framed).enhance(1.22)
        warm_amber = Image.new("RGB", framed.size, (255, 232, 205))
        lit = Image.blend(enh_col, warm_amber, alpha=0.10)
        lit = ImageEnhance.Contrast(lit).enhance(1.06)
    elif "Dramatic" in lighting or "Contrast" in lighting:
        # Architectural Digest dramatic contrast with deep floor shadow
        lit = ImageEnhance.Contrast(framed).enhance(1.30)
        lit = ImageEnhance.Brightness(lit).enhance(0.93)
    elif "High-Key" in lighting or "White" in lighting:
        # Scandinavian bright minimalist high-key clarity
        lit = ImageEnhance.Brightness(framed).enhance(1.08)
        lit = ImageEnhance.Contrast(lit).enhance(1.05)
    else:
        # 4500K Neutral Studio daylight balanced
        lit = ImageEnhance.Contrast(framed).enhance(1.03)

    # 4. Surface Finish & Timber Sheen Grading
    if "Danish" in finish or "Amber" in finish:
        # Deep hand-rubbed amber oil: rich warm saturation
        enh_sat = ImageEnhance.Color(lit).enhance(1.20)
        oil_tint = Image.new("RGB", framed.size, (210, 140, 65))
        finished = Image.blend(enh_sat, oil_tint, alpha=0.07)
    elif "Polyurethane" in finish or "Satin" in finish:
        # Satin clear coat: specular crispness
        finished = ImageEnhance.Sharpness(lit).enhance(1.25)
        finished = ImageEnhance.Contrast(finished).enhance(1.05)
    elif "Raw" in finish or "Sanded" in finish:
        # Raw planed natural timber: organic matte desaturation
        finished = ImageEnhance.Color(lit).enhance(0.88)
        finished = ImageEnhance.Contrast(finished).enhance(0.98)
    else:
        # Natural Hardwax Oil: micro-contrast highlighting natural grain texture
        finished = ImageEnhance.Sharpness(lit).enhance(1.15)

    # 5. Authentic Timber Species Tone Mapping
    w_id = wood_info.get("id", "timber") if wood_info else "timber"
    final_render = apply_species_photographic_grading(finished, w_id)

    return final_render


# =============================================================================
# 3. MASTER STUDIO VIEW RENDERER & SUITE ORCHESTRATOR
# =============================================================================
def render_studio_view(
    furniture_item: dict,
    pattern: dict,
    wood_info: dict,
    output_path: str,
    pattern_index: int = 0,
    api_key: str = None,
    perspective: str = "Hero Three-Quarter",
    lighting: str = "4500K Neutral Studio",
    finish: str = "Natural Hardwax Oil",
    custom_prompt: str = "",
    seed: int = 1
) -> tuple:
    """
    Renders the master product visualization:
    1. Calls Generative AI (Google Imagen 3 or OpenAI) if API key is active.
    2. Falls back to bespoke dynamic Photographic Atelier variations if AI is unavailable
       or quota is exhausted, returning clear status metadata.
    
    Returns (output_path, status_label, error_detail).
    """
    ai_img, ai_status = generate_ai_furniture_image(
        furniture_item, pattern, wood_info,
        api_key=api_key,
        perspective=perspective,
        lighting=lighting,
        finish=finish,
        custom_prompt=custom_prompt,
        seed=seed
    )

    if ai_img is not None:
        ai_img.save(output_path, "PNG", optimize=True)
        return output_path, f"Generative AI · {ai_status}", None
    else:
        # Generate bespoke photographic variation matching the exact selected options
        photo = generate_photographic_variation(
            furniture_item, pattern, wood_info,
            pattern_index=pattern_index,
            perspective=perspective,
            lighting=lighting,
            finish=finish,
            seed=seed
        )
        photo.save(output_path, "PNG", optimize=True)
        
        status_label = f"Photographic Atelier · {perspective} · {lighting}"
        error_detail = ai_status if ai_status and "No API key" not in ai_status else None
        return output_path, status_label, error_detail


def generate_multi_design_suite(
    furniture_item: dict,
    pattern: dict,
    wood_info: dict,
    force_regenerate: bool = False,
    pattern_index: int = 0,
    api_key: str = None,
    perspective: str = "Hero Three-Quarter",
    lighting: str = "4500K Neutral Studio",
    finish: str = "Natural Hardwax Oil",
    custom_prompt: str = "",
    seed: int = 1
) -> dict:
    """
    Orchestrates the generation of the master studio visualization and maintains
    compatibility with downstream test and export tools.
    """
    f_id = furniture_item.get("id", "piece")
    p_title = pattern.get("title", "Design Pattern")
    w_id = wood_info.get("id", "timber") if wood_info else "timber"

    paths = get_design_suite_paths(f_id, p_title, w_id)

    status_label = "Photographic Studio Master"
    error_detail = None

    if not os.path.exists(paths["studio"]) or force_regenerate:
        out_path, status_label, error_detail = render_studio_view(
            furniture_item, pattern, wood_info, paths["studio"],
            pattern_index=pattern_index,
            api_key=api_key,
            perspective=perspective,
            lighting=lighting,
            finish=finish,
            custom_prompt=custom_prompt,
            seed=seed
        )

    return {
        "studio": {
            "title": "Master Product Studio Render",
            "icon": "📸",
            "badge": "Studio Master",
            "status": status_label,
            "error": error_detail,
            "desc": f"High-definition master product render of {p_title} crafted in solid {wood_info.get('name', 'Hardwood')}.",
            "path": paths["studio"]
        }
    }


def generate_furniture_design_image(furniture_item: dict, pattern: dict, wood_info: dict, force_regenerate: bool = False) -> str:
    """Legacy compatibility helper."""
    suite = generate_multi_design_suite(furniture_item, pattern, wood_info, force_regenerate=force_regenerate)
    return suite["studio"]["path"]
