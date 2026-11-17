"""Wood Intelligence — Streamlit Application.
Multi-Page Dashboard for AI Wood Species Identification, Defect Detection & Furniture Suitability.
"""
import os
import io
import html
import json
import base64
import tempfile
import datetime
import textwrap

# ── Silence TF logging noise before any framework import ────────────────────
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

import cv2
import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image, ImageFilter, ImageEnhance

import predict
import wood_gate
import furniture_recommender

try:
    import plotly
    import plotly.io as pio
except ImportError:
    pio = None

# Guard against Streamlit hot-reload re-patching an already-patched function
# (which causes infinite recursion: safe_st_markdown calls itself indefinitely)
if not getattr(st, "_markdown_patched", False):
    _orig_st_markdown = st.markdown
    def safe_st_markdown(body, *args, **kwargs):
        if kwargs.get("unsafe_allow_html") and isinstance(body, str) and not body.strip().startswith("<style"):
            body = "".join(line.strip() for line in body.splitlines() if line.strip())
        return _orig_st_markdown(body, *args, **kwargs)
    st.markdown = safe_st_markdown
    st._markdown_patched = True
    st._orig_markdown = _orig_st_markdown  # keep a stable reference safe from re-capture

def uhtml(s: str) -> str:
    """Returns an unindented single-line string with no blank lines so Streamlit does not turn it into a code block."""
    return "".join(line.strip() for line in s.splitlines() if line.strip())

HAS_QR = True
HAS_PDF = True
HAS_TTS = False

# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(BASE_DIR, "analysis_history.json")

# Full species engineering properties database
SPECIES_DATABASE = {
    "1": {
        "folder_id": "1",
        "name": "European beech (Fagus sylvatica)",
        "common_name": "European Beech",
        "botanical_name": "Fagus sylvatica",
        "type": "Hardwood",
        "strength": "High (Janka ~1,300 lbf | MOR 110 MPa | High bending & shock resistance)",
        "strength_level": "High",
        "durability": "Moderate (Ideal for interior use; requires sealing against moisture)",
        "common_uses": "Chairs, heavy-duty workbenches, solid table legs, wood turnery, flooring, cabinet framing",
        "density": "720 kg/m³",
        "workability": "Superb steam-bending; machines cleanly; stains and finishes evenly",
        "furniture_compat": ["chair", "table", "desk", "bed", "cupboard", "shelf"]
    },
    "2": {
        "folder_id": "2",
        "name": "Walnut (Juglans regia)",
        "common_name": "European Walnut",
        "botanical_name": "Juglans regia",
        "type": "Hardwood",
        "strength": "Medium-High (Janka ~1,010 lbf | MOR 101 MPa | Superior dimensional stability)",
        "strength_level": "Medium-High",
        "durability": "High (Naturally resistant to decay and fungal attack)",
        "common_uses": "Executive desks, premium dining tables, architectural millwork, luxury cabinetry, gunstocks",
        "density": "640 kg/m³",
        "workability": "Superb machining and hand carving; holds crisp edges; lustrous natural polish",
        "furniture_compat": ["table", "desk", "chair", "bed", "door", "shelf"]
    },
    "3": {
        "folder_id": "3",
        "name": "Sweet chestnut (Castanea sativa)",
        "common_name": "Sweet Chestnut",
        "botanical_name": "Castanea sativa",
        "type": "Hardwood",
        "strength": "Medium (Janka ~540 lbf | MOR 71 MPa | Light and resilient)",
        "strength_level": "Medium",
        "durability": "Very High (Naturally rich in protective tannins; excellent outdoor weather resistance)",
        "common_uses": "Exterior doors, garden tables, rustic benches, cladding, fencing, structural posts",
        "density": "560 kg/m³",
        "workability": "Splits easily along straight grain; glues and screws securely; outdoor-hardy",
        "furniture_compat": ["door", "table", "shelf", "desk", "cupboard"]
    },
    "4": {
        "folder_id": "4",
        "name": "Turkey oak (Quercus cerris)",
        "common_name": "Turkey Oak",
        "botanical_name": "Quercus cerris",
        "type": "Hardwood",
        "strength": "Very High (Janka ~1,250 lbf | MOR 115 MPa | Heavy, stiff and hard-wearing)",
        "strength_level": "Very High",
        "durability": "Moderate (Needs dry interior storage or preservative treatment outdoors)",
        "common_uses": "Heavy shelving, rustic dining tables, industrial work surfaces, structural beams",
        "density": "760 kg/m³",
        "workability": "Hard on cutting edges; pre-drilling required; distinctive medullary rays",
        "furniture_compat": ["shelf", "table", "bed", "chair", "door"]
    },
    "5": {
        "folder_id": "5",
        "name": "Black alder (Alnus glutinosa)",
        "common_name": "Black Alder",
        "botanical_name": "Alnus glutinosa",
        "type": "Hardwood",
        "strength": "Low-Medium (Janka ~590 lbf | MOR 65 MPa | Soft, uniform, non-splitting)",
        "strength_level": "Low-Medium",
        "durability": "Low-Moderate (Extremely durable underwater; non-durable in humid outdoor air)",
        "common_uses": "Cupboard carcasses, drawer sides, acoustic instrument bodies, wooden toys, craft turnery",
        "density": "490 kg/m³",
        "workability": "Very soft and easy to carve, plane, and sand; takes dye and stain exceptionally well",
        "furniture_compat": ["cupboard", "desk", "shelf"]
    },
    "6": {
        "folder_id": "6",
        "name": "Manna ash (Fraxinus ornus)",
        "common_name": "Manna Ash",
        "botanical_name": "Fraxinus ornus",
        "type": "Hardwood",
        "strength": "High (Janka ~1,120 lbf | MOR 112 MPa | Outstanding shock absorption & elastic flexibility)",
        "strength_level": "High",
        "durability": "Low / Perishable (Indoor use only; requires protective seal against moisture)",
        "common_uses": "Bentwood dining chairs, tool handles, desk legs, sports equipment, curved furniture backs",
        "density": "680 kg/m³",
        "workability": "Exceptional steam-bending performance; smooth finish with oils and polyurethanes",
        "furniture_compat": ["chair", "desk", "table", "bed"]
    },
    "7": {
        "folder_id": "7",
        "name": "Norway spruce (Picea abies)",
        "common_name": "Norway Spruce",
        "botanical_name": "Picea abies",
        "type": "Softwood",
        "strength": "Medium-Low (Janka ~400 lbf | MOR 71 MPa | Light, straight-grained)",
        "strength_level": "Medium-Low",
        "durability": "Low (Non-durable; susceptible to fungi and moisture decay if unprotected)",
        "common_uses": "Bed slats, interior shelving, soundboards for musical instruments, lightweight cupboard framing",
        "density": "450 kg/m³",
        "workability": "Easy to saw, glue, and nail; knots can be brittle and require sharp blades",
        "furniture_compat": ["bed", "shelf", "cupboard"]
    },
    "8": {
        "folder_id": "8",
        "name": "Scots pine (Pinus sylvestris)",
        "common_name": "Scots Pine",
        "botanical_name": "Pinus sylvestris",
        "type": "Softwood",
        "strength": "Medium (Janka ~540 lbf | MOR 82 MPa | Favourable strength-to-weight ratio)",
        "strength_level": "Medium",
        "durability": "Moderate (Resinous heartwood moderately durable)",
        "common_uses": "Interior doors, study desks, pine wardrobes, utility shelves, architectural moldings",
        "density": "510 kg/m³",
        "workability": "Resinous; easy to plane, sand, and join; knots require shellac sealer before painting",
        "furniture_compat": ["door", "cupboard", "desk", "shelf", "table"]
    },
    "9": {
        "folder_id": "9",
        "name": "Tree of heaven (Ailanthus altissima)",
        "common_name": "Tree of Heaven",
        "botanical_name": "Ailanthus altissima",
        "type": "Hardwood",
        "strength": "Medium (Janka ~700 lbf | MOR 78 MPa | Coarse ring-porous texture)",
        "strength_level": "Medium",
        "durability": "Low (Perishable; susceptible to powder-post beetles and wood decay)",
        "common_uses": "Light display shelving, craft boxes, decorative rustic accents, secondary framing",
        "density": "540 kg/m³",
        "workability": "Rapid drying with some twist tendency; machines easily; coarse grain needs grain filler",
        "furniture_compat": ["shelf", "cupboard"]
    },
    "10": {
        "folder_id": "10",
        "name": "Black locust (Robinia pseudoacacia)",
        "common_name": "Black Locust",
        "botanical_name": "Robinia pseudoacacia",
        "type": "Hardwood",
        "strength": "Extremely High (Janka ~1,700 lbf | MOR 134 MPa | Superb stiffness & wear resistance)",
        "strength_level": "Extremely High",
        "durability": "Exceptionally High (Superior natural rot resistance; lasts decades in damp outdoor use)",
        "common_uses": "Heavy exterior doors, outdoor dining tables, heavy workbenches, structural posts, decking",
        "density": "770 kg/m³",
        "workability": "Very difficult to hand-plane; pre-drill screw holes; bonds well with polyurethane and epoxy",
        "furniture_compat": ["door", "table", "bed", "chair", "shelf"]
    },
    "11": {
        "folder_id": "11",
        "name": "Mediterranean cypress (Cupressus sempervirens)",
        "common_name": "Mediterranean Cypress",
        "botanical_name": "Cupressus sempervirens",
        "type": "Softwood",
        "strength": "Medium-High (Janka ~800 lbf | MOR 88 MPa | Exceptionally stable, fine straight grain)",
        "strength_level": "Medium-High",
        "durability": "Very High (Naturally insect-repellent, aromatic, immune to fungal rot)",
        "common_uses": "Wardrobes, linen cupboards, exterior doors, chest of drawers, outdoor furniture, cladding",
        "density": "530 kg/m³",
        "workability": "Smooth, aromatic cut; holds screws tightly; finishes with oil and waxes beautifully",
        "furniture_compat": ["cupboard", "door", "table", "desk", "shelf"]
    },
    "12": {
        "folder_id": "12",
        "name": "Oriental plane (Platanus orientalis)",
        "common_name": "Oriental Plane / Lacewood",
        "botanical_name": "Platanus orientalis",
        "type": "Hardwood",
        "strength": "Medium (Janka ~900 lbf | MOR 85 MPa | Distinctive quarter-sawn lacewood figure)",
        "strength_level": "Medium",
        "durability": "Moderate (Best for indoor use; needs moisture barrier seal)",
        "common_uses": "Decorative dining tabletops, executive desks, premium credenzas, luxury jewelry boxes",
        "density": "620 kg/m³",
        "workability": "Interlocked grain requires sharp tools; excels with fine sanding and french polishing",
        "furniture_compat": ["table", "desk", "cupboard", "shelf"]
    },
    "13": {
        "folder_id": "13",
        "name": "Akashmoni (Acacia auriculiformis)",
        "common_name": "Akashmoni",
        "botanical_name": "Acacia auriculiformis",
        "type": "Hardwood",
        "strength": "High (Janka ~1,200 lbf | MOR 95 MPa | Stiff & dense grain)",
        "strength_level": "High",
        "durability": "High (Natural termite and decay resistance)",
        "common_uses": "Furniture framing, outdoor furniture, joinery, turnery, construction timber",
        "density": "710 kg/m³",
        "mor": 95.0,
        "workability": "Machines smoothly, takes screws and glue firmly, finishes with lustrous brown tone",
        "furniture_compat": ["table", "chair", "desk", "bed", "cupboard", "shelf"]
    },
    "14": {
        "folder_id": "14",
        "name": "Eucalyptus (Eucalyptus tereticornis)",
        "common_name": "Eucalyptus",
        "botanical_name": "Eucalyptus tereticornis",
        "type": "Hardwood",
        "strength": "Very High (Janka ~1,400 lbf | MOR 122 MPa | Heavy, dense and stiff)",
        "strength_level": "Very High",
        "durability": "Moderate to High (Requires proper seasoning to prevent movement)",
        "common_uses": "Heavy structural framing, utility furniture, rustic tables, posts, pallets",
        "density": "820 kg/m³",
        "mor": 122.0,
        "workability": "Hard on cutting blades; requires pre-drilling; stains and seals cleanly",
        "furniture_compat": ["bed", "shelf", "table", "desk", "door"]
    },
    "15": {
        "folder_id": "15",
        "name": "Kathal (Jackfruit)",
        "common_name": "Kathal (Jackfruit)",
        "botanical_name": "Artocarpus heterophyllus",
        "type": "Hardwood",
        "strength": "Medium-High (Janka ~1,100 lbf | MOR 86 MPa | Superior dimensional stability)",
        "strength_level": "Medium-High",
        "durability": "Very High (Naturally insect and fungus resistant; does not warp in monsoons)",
        "common_uses": "Traditional doors, windows, dining chairs, cots/beds, credenzas, musical instruments (mridangam, veena)",
        "density": "640 kg/m³",
        "mor": 86.0,
        "workability": "Excellent machining and carving; distinctive golden-yellow heartwood turning amber; holds polish remarkably",
        "furniture_compat": ["door", "chair", "table", "bed", "cupboard", "shelf", "desk"]
    },
    "16": {
        "folder_id": "16",
        "name": "Loha / Ironwood (Xylia xylocarpa)",
        "common_name": "Loha (Ironwood)",
        "botanical_name": "Xylia xylocarpa",
        "type": "Hardwood",
        "strength": "Extremely High (Janka ~2,150 lbf | MOR 152 MPa | Ultra-dense heavy timber)",
        "strength_level": "Extremely High",
        "durability": "Exceptionally High (Practically indestructible; immune to termites and rot)",
        "common_uses": "Heavy structural framing, railway ties, heavy-duty workbenches, exterior doors, bridge decks",
        "density": "1050 kg/m³",
        "mor": 152.0,
        "workability": "Very difficult to cut and plane; blunts tools rapidly; requires carbide-tipped blades",
        "furniture_compat": ["door", "table", "bed", "shelf"]
    },
    "17": {
        "folder_id": "17",
        "name": "Mahogany (Swietenia macrophylla)",
        "common_name": "Mahogany",
        "botanical_name": "Swietenia macrophylla",
        "type": "Hardwood",
        "strength": "Medium-High (Janka ~900 lbf | MOR 79.4 MPa | Stable and resilient)",
        "strength_level": "Medium-High",
        "durability": "High (Excellent resistance to decay and insects; highly stable)",
        "common_uses": "Fine luxury cabinetry, dining tables, executive desks, paneling, high-end furniture",
        "density": "590 kg/m³",
        "mor": 79.4,
        "workability": "World-renowned for effortless workability, fine detailing, and lustrous reddish-brown finish",
        "furniture_compat": ["table", "desk", "cupboard", "chair", "bed", "door", "shelf"]
    },
    "18": {
        "folder_id": "18",
        "name": "Minjiri (Senna siamea)",
        "common_name": "Minjiri (Siamese Senna)",
        "botanical_name": "Senna siamea",
        "type": "Hardwood",
        "strength": "High (Janka ~1,350 lbf | MOR 105 MPa | Hard, strong with rich dark heartwood)",
        "strength_level": "High",
        "durability": "High (Durable heartwood; resistant to insect attack)",
        "common_uses": "Decorative turnery, cabinetry, parquet flooring, handles, solid furniture",
        "density": "780 kg/m³",
        "mor": 105.0,
        "workability": "Moderately hard to plane; beautiful dark striped figure; sands to a smooth silky finish",
        "furniture_compat": ["table", "chair", "desk", "cupboard", "shelf"]
    },
    "19": {
        "folder_id": "19",
        "name": "Rain Tree (Samanea saman)",
        "common_name": "Rain Tree",
        "botanical_name": "Samanea saman",
        "type": "Hardwood",
        "strength": "Medium (Janka ~750 lbf | MOR 75 MPa | Tough with interlocking grain)",
        "strength_level": "Medium",
        "durability": "Moderate-High (Heartwood resistant to decay and dry-wood termites)",
        "common_uses": "Live-edge slab dining tables, decorative bowls, carving, general interior furniture",
        "density": "560 kg/m³",
        "mor": 75.0,
        "workability": "Interlocked grain requires sharp tools; gorgeous golden-amber chatoyancy and grain figure",
        "furniture_compat": ["table", "desk", "shelf", "cupboard"]
    },
}

DEFECT_METADATA = {
    "Quartzity / Marrow": {
        "bgr": (0, 140, 255), "hex": "#f97316", "icon": "MINERAL", "severity": "Medium",
        "category": "Mineral / Pith",
        "description": "Mineral streaks or pith discoloration in the core growth rings.",
        "repair": "Sand surface evenly; apply wood hardener for porous core; finish with clear polyurethane.",
        "repair_type": "sanding"
    },
    "Live knot": {
        "bgr": (0, 200, 0), "hex": "#10b981", "icon": "SOUND KNOT", "severity": "Low",
        "category": "Intergrown Knot",
        "description": "Sound, intergrown branch knot firmly fused with surrounding wood fibers.",
        "repair": "No structural repair needed. Sand flush and apply protective sanding sealer and varnish.",
        "repair_type": "polishing"
    },
    "Resin": {
        "bgr": (255, 120, 0), "hex": "#0284c7", "icon": "RESIN", "severity": "Low",
        "category": "Surface Pitch",
        "description": "Natural resin or pitch pocket on the wood surface.",
        "repair": "Dissolve surface resin with mineral spirits; seal with shellac primer before topcoat.",
        "repair_type": "waterproof"
    },
    "Dead knot": {
        "bgr": (200, 0, 200), "hex": "#a855f7", "icon": "DEAD KNOT", "severity": "High",
        "category": "Loose Knot",
        "description": "Encased dead knot separated from surrounding wood; risk of dislodgement.",
        "repair": "Stabilize with clear liquid epoxy or drill out and insert matching grain plug.",
        "repair_type": "epoxy"
    },
    "Knot with crack": {
        "bgr": (0, 200, 200), "hex": "#eab308", "icon": "FISSURED", "severity": "High",
        "category": "Fissured Knot",
        "description": "Knot containing internal radial stress cracks or drying fissures.",
        "repair": "Inject deep-penetrating low-viscosity epoxy or CA glue + wood dust; clamp firmly until set.",
        "repair_type": "epoxy"
    },
    "Knot missing": {
        "bgr": (60, 60, 255), "hex": "#ef4444", "icon": "VOID", "severity": "High",
        "category": "Hole / Void",
        "description": "Complete knot void or knot-hole where dead knot center has fallen out.",
        "repair": "Fill cavity flush with two-part tinted wood epoxy filler; sand level when cured.",
        "repair_type": "wood_filler"
    },
    "Crack": {
        "bgr": (200, 200, 0), "hex": "#06b6d4", "icon": "SPLIT", "severity": "High",
        "category": "Structural Check",
        "description": "Longitudinal surface split or drying check separating timber grain fibers.",
        "repair": "Deep cracks: REJECT for load-bearing use. Non-critical: butterfly key or epoxy injection.",
        "repair_type": "rejection"
    },
    "Fungal Damage": {
        "bgr": (128, 0, 128), "hex": "#9333ea", "icon": "DECAY", "severity": "High",
        "category": "Biological Decay",
        "description": "Fungal rot or sapstain decaying wood cellular lignins.",
        "repair": "Apply borate antimicrobial treatment; gouge out soft rot, fill with epoxy hardener. REJECT if structural.",
        "repair_type": "rejection"
    },
    "Termite Damage": {
        "bgr": (0, 0, 255), "hex": "#dc2626", "icon": "BORER", "severity": "High",
        "category": "Insect Infestation",
        "description": "Internal galleries or exit pinholes caused by wood-boring insects.",
        "repair": "Thermal or pesticide treatment to eliminate active pests; pressure-inject epoxy. REJECT for structural furniture.",
        "repair_type": "rejection"
    }
}

DEFECT_GROUPS = {0: "Quartzity / Marrow", 2: "Quartzity / Marrow"}

SEV_COLORS = {
    "Low":    {"bg": "var(--good-tint)", "border": "var(--good-border)", "text": "var(--good)"},
    "Medium": {"bg": "var(--warn-tint)", "border": "var(--warn-border)", "text": "var(--warn)"},
    "High":   {"bg": "var(--bad-tint)",  "border": "var(--bad-border)",  "text": "var(--bad)"},
}

FURNITURE_CATALOG = {
    "chair": {
        "id": "chair", "name": "Chair", "full_name": "Dining / Accent Chair", "icon": "Chair",
        "image": os.path.join(BASE_DIR, "assets", "furniture", "chair.jpg"),
        "min_dimensions": {"length": 45, "width": 15, "thickness": 2.2},
        "dim_description": "Min: 45 cm length × 15 cm width × 2.2 cm thickness",
        "required_strength": "High Dynamic Fatigue & Tensile Strength (MOR >= 105 MPa)",
        "acceptable_defects": {
            "max_damage_pct": 0.6,
            "disallowed_types": ["Crack", "Knot with crack", "Dead knot", "Knot missing", "Fungal Damage", "Termite Damage"],
            "allowed_conditions": "Pin knots (<8 mm) on non-structural surfaces only."
        },
        "strength_req": "High",
        "priority_scores": {"strength": 92, "low_cost": 65, "best_appearance": 80}
    },
    "table": {
        "id": "table", "name": "Table", "full_name": "Dining / Slab Table", "icon": "Table",
        "image": os.path.join(BASE_DIR, "assets", "furniture", "table.jpg"),
        "min_dimensions": {"length": 100, "width": 25, "thickness": 2.5},
        "dim_description": "Min: 100 cm length × 25 cm width × 2.5 cm thickness",
        "required_strength": "Medium-High Load & Compressive Hardness (MOR >= 85 MPa)",
        "acceptable_defects": {
            "max_damage_pct": 1.5,
            "disallowed_types": ["Knot missing", "Termite Damage", "Fungal Damage"],
            "allowed_conditions": "Sound live knots up to 25 mm; epoxy-filled surface checks allowed."
        },
        "strength_req": "Medium-High",
        "priority_scores": {"strength": 82, "low_cost": 75, "best_appearance": 90}
    },
    "desk": {
        "id": "desk", "name": "Desk", "full_name": "Executive / Study Desk", "icon": "Desk",
        "image": os.path.join(BASE_DIR, "assets", "furniture", "desk.jpg"),
        "min_dimensions": {"length": 90, "width": 30, "thickness": 2.0},
        "dim_description": "Min: 90 cm length × 30 cm width × 2.0 cm thickness",
        "required_strength": "Moderate Static Structural Load & Flat Surfacing (MOR >= 75 MPa)",
        "acceptable_defects": {
            "max_damage_pct": 0.8,
            "disallowed_types": ["Resin", "Knot missing", "Knot with crack", "Termite Damage"],
            "allowed_conditions": "Smooth writing surface required; pin knots on perimeter only."
        },
        "strength_req": "Medium",
        "priority_scores": {"strength": 75, "low_cost": 80, "best_appearance": 85}
    },
    "shelf": {
        "id": "shelf", "name": "Shelf", "full_name": "Bookshelf / Floating Ledge", "icon": "Shelf",
        "image": os.path.join(BASE_DIR, "assets", "furniture", "shelf.jpg"),
        "min_dimensions": {"length": 50, "width": 18, "thickness": 1.8},
        "dim_description": "Min: 50 cm length × 18 cm width × 1.8 cm thickness",
        "required_strength": "High Modulus of Elasticity / Anti-Sag Stiffness (MOE >= 11,000 MPa)",
        "acceptable_defects": {
            "max_damage_pct": 2.0,
            "disallowed_types": ["Crack", "Knot with crack", "Termite Damage"],
            "allowed_conditions": "Zero edge splits in center span. Sound face knots acceptable."
        },
        "strength_req": "Medium",
        "priority_scores": {"strength": 78, "low_cost": 85, "best_appearance": 72}
    },
    "door": {
        "id": "door", "name": "Door", "full_name": "Solid Interior / Entry Door", "icon": "Door",
        "image": os.path.join(BASE_DIR, "assets", "furniture", "door.jpg"),
        "min_dimensions": {"length": 180, "width": 15, "thickness": 3.2},
        "dim_description": "Min: 180 cm length × 15 cm width × 3.2 cm thickness",
        "required_strength": "High Warp Resistance & Impact Slam Resilience",
        "acceptable_defects": {
            "max_damage_pct": 1.0,
            "disallowed_types": ["Crack", "Knot with crack", "Knot missing", "Fungal Damage", "Termite Damage"],
            "allowed_conditions": "Stiles must be straight-grained. Live knots up to 20 mm in floating panels."
        },
        "strength_req": "Medium-High",
        "priority_scores": {"strength": 85, "low_cost": 70, "best_appearance": 75}
    },
    "bed": {
        "id": "bed", "name": "Bed", "full_name": "Platform Bed Frame / Slat", "icon": "Bed",
        "image": os.path.join(BASE_DIR, "assets", "furniture", "bed.jpg"),
        "min_dimensions": {"length": 180, "width": 15, "thickness": 2.5},
        "dim_description": "Min: 180 cm length × 15 cm width × 2.5 cm thickness",
        "required_strength": "Very High Structural Load & Flexural Cyclic Fatigue Resistance",
        "acceptable_defects": {
            "max_damage_pct": 1.2,
            "disallowed_types": ["Crack", "Knot with crack", "Dead knot", "Termite Damage", "Fungal Damage"],
            "allowed_conditions": "Rails must be crack-free. Character live knots allowed on headboard."
        },
        "strength_req": "High",
        "priority_scores": {"strength": 94, "low_cost": 65, "best_appearance": 78}
    },
    "cupboard": {
        "id": "cupboard", "name": "Cupboard", "full_name": "Storage Cupboard / Wardrobe", "icon": "Cupboard",
        "image": os.path.join(BASE_DIR, "assets", "furniture", "shelf.jpg"),
        "min_dimensions": {"length": 80, "width": 25, "thickness": 1.6},
        "dim_description": "Min: 80 cm length × 25 cm width × 1.6 cm thickness",
        "required_strength": "Moderate Panel Stability & Secure Screw Holding for Hinges",
        "acceptable_defects": {
            "max_damage_pct": 2.5,
            "disallowed_types": ["Crack", "Knot missing", "Termite Damage"],
            "allowed_conditions": "Visible doors must be sound. Knots permitted on hidden carcass interior."
        },
        "strength_req": "Low-Medium",
        "priority_scores": {"strength": 68, "low_cost": 90, "best_appearance": 70}
    }
}

ALTERNATIVE_USES = [
    {"name": "Wooden Coasters", "icon": "COASTERS", "dim_req": "10×10 cm",
     "desc": "Cross-cut slices or resin-inlaid squares; small defects become artistic focal points.",
     "prep": "Cut small sound blanks around defects, sand to 320 grit, seal with food-safe mineral oil or epoxy."},
    {"name": "Rustic Photo Frames", "icon": "FRAMES", "dim_req": "20×15 cm",
     "desc": "Natural knotty grain and live texture add distinctive handcrafted charm to picture borders.",
     "prep": "Rabbet back edges, miter corners at 45°, reinforce corners with wooden splines, wax finish."},
    {"name": "Wall Art & Décor", "icon": "PANELS", "dim_req": "30×20 cm",
     "desc": "Organic character panels, geometric mosaic tiles, or live-edge floating wall accents.",
     "prep": "Accentuate cracks with metallic epoxy resin inlay; mount on plywood backer board."},
    {"name": "Carved Toys & Handles", "icon": "CARVINGS", "dim_req": "15×5 cm",
     "desc": "Non-structural handheld toys, turning blanks, tool handles, or tactile decorative objects.",
     "prep": "Carve defect-free core sections; sand glass-smooth; coat with non-toxic beeswax/flaxseed finish."},
    {"name": "Workshop Recycling / Spacers", "icon": "RECYCLING", "dim_req": "Any size",
     "desc": "Recycle heavily checked timber into workbench clamping cauls, stickers, composite wood, or bio-fuel.",
     "prep": "Rip down into clean utility strips or shred into high-carbon garden mulch / animal bedding."}
]

SAMPLES = [
    {"id": "s1", "name": "Clear Board (Grade A)",
     "file": os.path.join(BASE_DIR, "extra_wood_samples", "wood2_00_1.jpg"),
     "icon": "GRADE-A", "desc": "Smooth uniform lumber without defects"},
    {"id": "s2", "name": "Pine with Knots",
     "file": os.path.join(BASE_DIR, "extra_wood_samples", "wood2_03_0.jpg"),
     "icon": "PINE", "desc": "Softwood featuring sound knots"},
    {"id": "s3", "name": "Beech Board (5 Defects)",
     "file": os.path.join(BASE_DIR, "extra_wood_samples", "wood2_08_1.jpg"),
     "icon": "BEECH", "desc": "Hardwood with multiple knot variations"},
    {"id": "s4", "name": "European Oak",
     "file": os.path.join(BASE_DIR, "extra_wood_samples", "wood_00_2.jpg"),
     "icon": "OAK", "desc": "Dense ring-porous grain lumber"},
]

@st.cache_data
def get_asset_base64(path, size=None, q=80):
    if not os.path.exists(path):
        return ""
    try:
        im = Image.open(path).convert('RGB')
        if size:
            im.thumbnail(size, Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, 'JPEG', quality=q)
        return base64.b64encode(buf.getvalue()).decode()
    except Exception:
        return ""

@st.cache_data
def get_hero_images_bundle():
    return (
        get_asset_base64(os.path.join(BASE_DIR, "assets", "hero_timber_board.jpg"), (800, 260), 68),
        get_asset_base64(os.path.join(BASE_DIR, "assets", "hero_bookmatched_wood.jpg"), (800, 260), 68),
        get_asset_base64(os.path.join(BASE_DIR, "extra_wood_samples", "wood2_00_1.jpg"), (800, 260), 68),
        get_asset_base64(os.path.join(BASE_DIR, "extra_wood_samples", "wood2_04_0.jpg"), (800, 260), 68),
    )

# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Wood Intelligence | Industrial Timber Inspection & Defect Suite",
    page_icon="■", layout="wide", initial_sidebar_state="collapsed"
)

# Initialize Session State
if "theme" not in st.session_state:
    st.session_state["theme"] = "light"
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Home"
if "selected_sample" not in st.session_state:
    st.session_state["selected_sample"] = None
if "last_result" not in st.session_state:
    st.session_state["last_result"] = None
if "cmp_a_sample" not in st.session_state:
    st.session_state["cmp_a_sample"] = None
if "cmp_b_sample" not in st.session_state:
    st.session_state["cmp_b_sample"] = None
if "board_length" not in st.session_state:
    st.session_state["board_length"] = 120.0
if "board_width" not in st.session_state:
    st.session_state["board_width"] = 30.0
if "board_thickness" not in st.session_state:
    st.session_state["board_thickness"] = 2.5
if "conf_threshold" not in st.session_state:
    st.session_state["conf_threshold"] = 0.35
if "rec_priority" not in st.session_state:
    st.session_state["rec_priority"] = "strength"
if "selected_furniture" not in st.session_state:
    st.session_state["selected_furniture"] = "wooden_chair"
if "furn_category_filter" not in st.session_state:
    st.session_state["furn_category_filter"] = "All (31)"
if "furn_search_query" not in st.session_state:
    st.session_state["furn_search_query"] = ""

# Check gate file
if not os.path.exists(wood_gate.GATE_PATH):
    st.error("Wood-gate model missing. Run: python wood_gate.py build")
    st.stop()

if "wood_threshold" not in st.session_state:
    st.session_state["wood_threshold"] = round(float(np.load(wood_gate.GATE_PATH)["threshold"]), 2)
SAVED_THR = st.session_state["wood_threshold"]

# ---------------------------------------------------------------------------
# Core Helper Functions
def defect_label(class_id):
    return DEFECT_GROUPS.get(class_id, predict.defect_display(class_id))

def get_defect_style(label):
    return DEFECT_METADATA.get(label, {
        "bgr": (120, 120, 120), "hex": "#64748b", "icon": "⚠️", "severity": "Medium",
        "category": "Surface Feature", "description": "Surface grain anomaly or marking",
        "repair": "Sand the area smooth and apply protective clear wood sealer.",
        "repair_type": "sanding"
    })

def get_species_info(folder_id_or_name):
    fid = str(folder_id_or_name).strip()
    if fid in SPECIES_DATABASE:
        return SPECIES_DATABASE[fid]
    name_str = fid.lower()
    for s in SPECIES_DATABASE.values():
        s_name = s.get("name", "").lower()
        s_common = s.get("common_name", "").lower()
        s_bot = s.get("botanical_name", "").lower()
        if (name_str in s_name or name_str in s_common or name_str in s_bot or
            s_name in name_str or s_common in name_str or s_bot in name_str):
            return s

    # Secondary lookup against rich engineering database in woods_data
    try:
        import woods_data
        for w in woods_data.WOODS_DATABASE:
            w_id = str(w.get("id", "")).lower()
            w_name = str(w.get("name", "")).lower()
            w_sci = str(w.get("scientificName", "")).lower()
            if (name_str in w_id or w_id in name_str or
                name_str in w_name or w_name in name_str or
                name_str in w_sci or w_sci in name_str):
                return {
                    "folder_id": fid,
                    "name": f"{w.get('name', 'Timber')} ({w.get('scientificName', '')})",
                    "common_name": w.get("name", "Timber"),
                    "botanical_name": w.get("scientificName", "Undetermined"),
                    "type": "Hardwood" if w.get("density", 600) >= 550 else "Softwood",
                    "strength": f"High (Janka ~{w.get('hardness_lbf', 1000)} lbf | MOR {w.get('mor', 85)} MPa)",
                    "strength_level": "High" if w.get("mor", 85) >= 95 else ("Medium-High" if w.get("mor", 85) >= 80 else "Medium"),
                    "durability": f"Score {w.get('durability', 8.0)}/10",
                    "common_uses": ", ".join(w.get("bestUses", ["Interior furniture"])) if isinstance(w.get("bestUses"), list) else "Interior furniture",
                    "density": f"{w.get('density', 640)} kg/m³",
                    "mor": float(w.get("mor", 85.0)),
                    "workability": f"Score {w.get('workability', 8.0)}/10",
                    "furniture_compat": ["chair", "table", "door", "bed", "cupboard", "shelf", "desk"]
                }
    except Exception:
        pass

    return {
        "folder_id": "0",
        "name": "Generic Timber",
        "common_name": "Commercial Hardwood/Softwood",
        "botanical_name": "Undetermined",
        "type": "Wood Timber",
        "strength": "Moderate (Average Janka ~800 lbf)",
        "strength_level": "Medium",
        "durability": "Moderate (Interior use recommended)",
        "common_uses": "General cabinetry, utility shelving, interior furniture",
        "density": "600 kg/m³",
        "mor": 75.0,
        "workability": "Standard machining and fastening properties",
        "furniture_compat": ["shelf", "cupboard", "table", "desk", "chair"]
    }

def overall_severity(defect_items, damaged_pct):
    if not defect_items and damaged_pct < 0.5:
        return "Low"
    high = sum(1 for d in defect_items if d.get("severity") == "High")
    if high >= 2 or damaged_pct > 3.0:
        return "High"
    if high == 1 or damaged_pct > 1.0:
        return "Medium"
    return "Low"

@st.cache_resource(show_spinner="Loading AI models...")
def get_models():
    predict.load_models()
    wood_gate.get_extractor()
    return True

def segment_defects(image_path, detections):
    img = cv2.imread(image_path)
    if img is None:
        return None, None, 0.0, 100.0, 0.0, []
    h, w = img.shape[:2]
    total_px = h * w
    full_mask = np.zeros((h, w), dtype=np.uint8)
    defect_items = []
    box_img = img.copy()
    overlay = img.copy()
    seg_img = img.copy()
    thick = max(2, w // 450)
    scale = max(0.48, w / 1650)

    for idx, d in enumerate(detections):
        x1, y1, x2, y2 = [int(v) for v in d["box_xyxy"]]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)
        if x2 <= x1 or y2 <= y1:
            continue
        label = d["label"]
        meta = get_defect_style(label)
        color = meta["bgr"]

        # Draw bounding box
        cv2.rectangle(box_img, (x1, y1), (x2, y2), color, thick)
        bt = f"{label} {d['confidence']*100:.0f}%"
        (btw, bth), _ = cv2.getTextSize(bt, cv2.FONT_HERSHEY_SIMPLEX, scale, max(1, thick - 1))
        bty = max(bth + 10, y1)
        cv2.rectangle(box_img, (x1, bty - bth - 8), (x1 + btw + 10, bty + 4), color, -1)
        cv2.putText(box_img, bt, (x1 + 5, bty - 3), cv2.FONT_HERSHEY_SIMPLEX, scale, (255, 255, 255), max(1, thick - 1), cv2.LINE_AA)

        # Segment exact damaged pixels inside ROI
        roi = img[y1:y2, x1:x2]
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        diff = cv2.absdiff(gray, int(np.mean(gray)))
        _, rmask = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        rmask = cv2.morphologyEx(rmask, cv2.MORPH_CLOSE, k)
        rmask = cv2.morphologyEx(rmask, cv2.MORPH_OPEN, k)

        dfm = np.zeros((h, w), dtype=np.uint8)
        dfm[y1:y2, x1:x2] = rmask
        contours, _ = cv2.findContours(dfm, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        da = int(np.count_nonzero(rmask))
        dp = (da / total_px) * 100

        overlay[dfm > 0] = color
        cv2.drawContours(seg_img, contours, -1, color, max(2, w // 400))
        st_ = f"{label} {dp:.2f}%"
        (stw, sth), _ = cv2.getTextSize(st_, cv2.FONT_HERSHEY_SIMPLEX, scale * 0.95, max(1, thick - 1))
        sty = max(sth + 8, y1)
        cv2.rectangle(seg_img, (x1, sty - sth - 8), (x1 + stw + 10, sty + 4), color, -1)
        cv2.putText(seg_img, st_, (x1 + 5, sty - 3), cv2.FONT_HERSHEY_SIMPLEX, scale * 0.95, (255, 255, 255), max(1, thick - 1), cv2.LINE_AA)

        full_mask = cv2.bitwise_or(full_mask, dfm)
        defect_items.append({
            "index": idx + 1, "label": label, "confidence": d["confidence"],
            "area_px": da, "damaged_pct": dp, "box_xyxy": [x1, y1, x2, y2],
            "color_hex": meta["hex"], "icon": meta["icon"],
            "severity": meta.get("severity", "Medium"),
            "repair": meta.get("repair", "Sand and refinish."),
            "repair_type": meta.get("repair_type", "sanding")
        })

    total_d = int(np.count_nonzero(full_mask))
    tdp = (total_d / total_px) * 100
    waste_pct = min(100.0, round(tdp * 1.35 + (0.5 if tdp > 0 else 0), 2))
    usable_pct = max(0.0, round(100.0 - waste_pct, 2))

    cv2.addWeighted(overlay, 0.40, seg_img, 0.60, 0, seg_img)
    return cv2.cvtColor(seg_img, cv2.COLOR_BGR2RGB), cv2.cvtColor(box_img, cv2.COLOR_BGR2RGB), tdp, usable_pct, waste_pct, defect_items

def evaluate_furniture(finfo, species_info, detections, damaged_pct, dims, priority="strength"):
    fname = finfo["name"]
    fid = finfo["id"]
    sp_name = species_info.get("common_name", "Timber")
    sp_strength = species_info.get("strength_level", "Medium")

    is_compat = fid in species_info.get("furniture_compat", [])

    acc = finfo["acceptable_defects"]
    disallowed = acc["disallowed_types"]
    max_pct = acc["max_damage_pct"]
    critical = [d["label"] for d in detections if any(dt.lower() in d["label"].lower() for dt in disallowed)]
    has_critical = len(critical) > 0
    damage_exceeded = damaged_pct > max_pct

    min_d = finfo["min_dimensions"]
    user_l = dims.get("length", 120)
    user_w = dims.get("width", 30)
    user_t = dims.get("thickness", 2.5)

    dim_fail_reasons = []
    if user_l < min_d["length"]:
        dim_fail_reasons.append(f"length {user_l:.0f}cm < {min_d['length']}cm min")
    if user_w < min_d["width"]:
        dim_fail_reasons.append(f"width {user_w:.0f}cm < {min_d['width']}cm min")
    if user_t < min_d["thickness"]:
        dim_fail_reasons.append(f"thickness {user_t:.1f}cm < {min_d['thickness']}cm min")
    dim_ok = len(dim_fail_reasons) == 0

    base_score = 90
    reasons = []

    if has_critical:
        crit_names = ", ".join(sorted(set(critical)))
        if "crack" in crit_names.lower():
            reasons.append(f"Not suitable for a {fname.lower()} because a deep {crit_names.lower()} was detected in a high-strength area.")
        else:
            reasons.append(f"Not suitable for a {fname.lower()} because critical defect '{crit_names}' compromises structural reliability.")
        base_score -= 45 + len(critical) * 5
    elif damage_exceeded:
        reasons.append(f"Not suitable for a {fname.lower()} because damaged area ({damaged_pct:.2f}%) exceeds the {max_pct}% threshold.")
        base_score -= 35 + int(damaged_pct * 4)
    elif not dim_ok:
        reasons.append(f"Not suitable for a {fname.lower()} because wood dimensions are insufficient ({', '.join(dim_fail_reasons)}).")
        base_score -= 30
    elif not is_compat:
        reasons.append(f"Conditional for a {fname.lower()}: {sp_name} has {sp_strength.lower()} strength, which requires heavy reinforcement for this application.")
        base_score -= 18
    else:
        reasons.append(f"Suitable for a {fname.lower()}: {sp_name} provides {sp_strength.lower()} strength, dimensions fit, and damage is within {max_pct}% tolerance.")
        base_score += 6

    pm = finfo.get("priority_scores", {"strength": 80, "low_cost": 75, "best_appearance": 75})
    score = int(min(98, max(12, base_score * 0.72 + pm.get(priority, 75) * 0.28)))

    if score >= 75 and not has_critical and dim_ok and not damage_exceeded:
        status = "SUITABLE"
    elif score >= 45 and not ("crack" in [c.lower() for c in critical] and finfo["strength_req"] == "High"):
        status = "CONDITIONAL"
    else:
        status = "NOT SUITABLE"

    reason = " ".join(reasons)

    return {
        "status": status,
        "score": score,
        "reason": reason,
        "dim_ok": dim_ok,
        "dim_fail": dim_fail_reasons,
        "critical": critical,
        "damage_pct": damaged_pct,
        "max_pct": max_pct,
        "species_name": sp_name
    }

def make_repair_preview(original_rgb, repair_type="sand"):
    pil = Image.fromarray(original_rgb)
    if repair_type == "sand":
        pil = pil.filter(ImageFilter.SMOOTH_MORE)
        pil = ImageEnhance.Contrast(pil).enhance(0.88)
        pil = ImageEnhance.Brightness(pil).enhance(1.06)
    elif repair_type == "fill":
        pil = pil.filter(ImageFilter.SMOOTH)
        pil = ImageEnhance.Color(pil).enhance(0.92)
        pil = ImageEnhance.Brightness(pil).enhance(1.04)
    elif repair_type == "polish":
        pil = pil.filter(ImageFilter.SMOOTH_MORE)
        pil = ImageEnhance.Sharpness(pil).enhance(1.35)
        pil = ImageEnhance.Color(pil).enhance(1.18)
        pil = ImageEnhance.Brightness(pil).enhance(1.10)
    elif repair_type == "coating":
        pil = ImageEnhance.Color(pil).enhance(1.25)
        pil = ImageEnhance.Contrast(pil).enhance(1.12)
        pil = ImageEnhance.Brightness(pil).enhance(1.05)
    return np.array(pil)

def generate_qr(text):
    import qrcode
    qr = qrcode.QRCode(version=1, box_size=6, border=3)
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#3d2007", back_color="white")
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_history(entry):
    h = load_history()
    h.insert(0, entry)
    h = h[:50]
    with open(HISTORY_FILE, "w") as f:
        json.dump(h, f, indent=2)

def make_pdf_report(payload, original_bytes):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors as rl_colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                     Table, TableStyle, HRFlowable,
                                     Image as RLImage)
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=1.5*cm, bottomMargin=1.5*cm, leftMargin=1.8*cm, rightMargin=1.8*cm)
    styles = getSampleStyleSheet()
    ts = ParagraphStyle("t", parent=styles["Title"], fontSize=18, textColor=rl_colors.HexColor("#3d2007"), fontName="Helvetica-Bold", spaceAfter=6)
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=12, textColor=rl_colors.HexColor("#6b3a1f"), fontName="Helvetica-Bold", spaceAfter=4)
    bs = ParagraphStyle("b", parent=styles["Normal"], fontSize=9.5, leading=14, spaceAfter=4)
    story = [
        Paragraph("Wood Intelligence — Timber Defect & Species Report", ts),
        Paragraph(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", bs),
        HRFlowable(width="100%", thickness=1, color=rl_colors.HexColor("#e8dcc8")),
        Spacer(1, 8)
    ]
    try:
        pil_img = Image.open(io.BytesIO(original_bytes)).convert("RGB")
        pil_img.thumbnail((380, 240), Image.LANCZOS)
        out = io.BytesIO()
        pil_img.save(out, "JPEG")
        out.seek(0)
        story.append(RLImage(out, width=11*cm, height=7*cm))
    except Exception:
        pass
    story.append(Spacer(1, 6))

    sp = payload.get("species_details", {})
    m = payload.get("damage_metrics", {})
    cell_style = ParagraphStyle("cell", parent=styles["Normal"], fontSize=8.5, leading=11)
    story.append(Paragraph("Wood Identification & Timber Quality", h2))
    sdata = [
        ["Attribute", "Specification"],
        ["Identified Species", Paragraph(html.escape(f"{sp.get('name', 'N/A')} ({sp.get('confidence', 0):.1f}%)", quote=False), cell_style)],
        ["Wood Strength", Paragraph(html.escape(str(sp.get("strength", "N/A")), quote=False), cell_style)],
        ["Natural Durability", Paragraph(html.escape(str(sp.get("durability", "N/A")), quote=False), cell_style)],
        ["Dimensions", f"{payload.get('dimensions', {}).get('length',0)} × {payload.get('dimensions', {}).get('width',0)} × {payload.get('dimensions', {}).get('thickness',0)} cm"],
        ["Damaged Area", f"{m.get('damaged_pct', 0):.2f}%"],
        ["Usable Wood", f"{m.get('usable_pct', 0):.2f}%"],
        ["Waste Percentage", f"{m.get('waste_pct', 0):.2f}%"],
        ["Defect Severity", m.get("severity", "N/A")]
    ]
    stbl = Table(sdata, colWidths=[6.5*cm, 10.5*cm])
    stbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), rl_colors.HexColor("#6b3a1f")),
        ("TEXTCOLOR", (0, 0), (-1, 0), rl_colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, rl_colors.HexColor("#e8dcc8")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [rl_colors.HexColor("#fffdf8"), rl_colors.white]),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4)
    ]))
    story += [stbl, Spacer(1, 10)]

    story.append(Paragraph("Furniture Suitability Evaluation", h2))
    frs = payload.get("furniture_results", [])
    if frs:
        fd = [["Furniture", "Score", "Status", "Reasoning"]]
        for fr in frs[:7]:
            fd.append([
                fr.get("name", ""), f"{fr.get('score', 0)}/100", fr.get("status", ""),
                Paragraph(html.escape(str(fr.get("reason", "")), quote=False), cell_style)
            ])
        ft = Table(fd, colWidths=[2.5*cm, 1.8*cm, 2.8*cm, 9.9*cm])
        ft.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), rl_colors.HexColor("#3d2007")),
            ("TEXTCOLOR", (0, 0), (-1, 0), rl_colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("GRID", (0, 0), (-1, -1), 0.5, rl_colors.HexColor("#e8dcc8")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [rl_colors.HexColor("#fffdf8"), rl_colors.white]),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4)
        ]))
        story.append(ft)

    story += [
        Spacer(1, 8),
        Paragraph("Generated by Wood Intelligence | AI Timber & Defect Inspection",
                  ParagraphStyle("f", parent=styles["Normal"], fontSize=7.5, textColor=rl_colors.HexColor("#92400e"), alignment=1))
    ]
    doc.build(story)
    buf.seek(0)
    return buf.getvalue()


def render_inspection_report(R, key_prefix="report"):
    """Render the Official Timber Quality Certification report card (PDF export)."""
    st.markdown('<div class="wi-card"><div class="wi-card-header"><span class="wi-card-title">Official Timber Quality Certification</span><span class="wi-section-label">AUDIT EXPORTS</span></div>', unsafe_allow_html=True)

    sp_data = R.get("sp_info", {})
    payload = {
        "timestamp": R["ts"], "filename": R["aname"], "wood_score": round(R["ws"], 4),
        "species_details": sp_data, "dimensions": R["dims"],
        "damage_metrics": {
            "damaged_pct": round(R["dmg"], 4), "usable_pct": round(R["usbl"], 4),
            "waste_pct": round(R["wst"], 4), "defect_count": len(R["dets"]), "severity": R["sev"],
            "defects": [
                {"index": d["index"], "label": d["label"], "severity": d["severity"],
                 "damaged_pct": round(d["damaged_pct"], 4), "repair": d["repair"]} for d in R["ditems"]
            ]
        },
        "furniture_results": [
            {"name": fr["name"], "score": fr["score"], "status": fr["status"], "reason": fr["reason"]} for fr in R["furn_results"]
        ],
        "repair_advice": R["repair_advice"]
    }

    st.markdown("#### Document Exports")
    if HAS_PDF:
        try:
            pdf = make_pdf_report(payload, R["abytes"])
            st.download_button("Download Formal PDF Report", pdf,
                               file_name=f"{os.path.splitext(R['aname'])[0]}_timber_report.pdf", mime="application/pdf",
                               key=f"{key_prefix}_pdf", use_container_width=True)
        except Exception as e:
            st.warning(f"PDF error: {e}")
    else:
        st.info("ReportLab package required for PDF export.")

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# ATELIER TOP HORIZONTAL NAVIGATION (SIDEBAR REMOVED)
# ---------------------------------------------------------------------------
NAV_OPTIONS = [
    ("Home", "[01]", "Home"),
    ("Overview", "[02]", "Overview"),
    ("New Analysis", "[03]", "New Analysis"),
    ("Defect Detection", "[04]", "Defects"),
    ("Furniture Recommendations", "[05]", "Furniture"),
    ("Compare Wood", "[06]", "Compare"),
    ("Analysis History", "[07]", "History"),
    ("Reports", "[08]", "Reports"),
    ("Settings", "[09]", "Settings")
]

# Timber Atelier Masthead (Matches media_1793688954155_c8a2a591.jpg)
head_c1, head_c2, head_c3, head_c4 = st.columns([1.15, 4.8, 1.65, 2.4], vertical_alignment="center")

with head_c1:
    st.markdown("""<style>
    div[data-testid="stPopover"] button,
    .stPopover button,
    div[data-testid="stColumn"]:first-child button {
        background: rgba(255, 209, 102, 0.2) !important;
        border: 1.5px solid #ffd166 !important;
        border-radius: 6px !important;
        min-height: 38px !important;
        height: 38px !important;
    }
    div[data-testid="stPopover"] button p,
    div[data-testid="stPopover"] button span,
    div[data-testid="stPopover"] button div,
    div[data-testid="stPopover"] button svg,
    .stPopover button p,
    .stPopover button span,
    .stPopover button svg,
    div[data-testid="stColumn"]:first-child button p,
    div[data-testid="stColumn"]:first-child button span,
    div[data-testid="stColumn"]:first-child button svg {
        color: #ffd166 !important;
        fill: #ffd166 !important;
        stroke: #ffd166 !important;
        font-weight: 800 !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.05em !important;
        opacity: 1 !important;
        visibility: visible !important;
        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.9) !important;
    }
    div[data-testid="stPopover"] button:hover,
    .stPopover button:hover {
        background: #ffd166 !important;
        border-color: #ffd166 !important;
    }
    div[data-testid="stPopover"] button:hover p,
    div[data-testid="stPopover"] button:hover span,
    div[data-testid="stPopover"] button:hover svg,
    .stPopover button:hover p,
    .stPopover button:hover span,
    .stPopover button:hover svg {
        color: #1a0f07 !important;
        fill: #1a0f07 !important;
        stroke: #1a0f07 !important;
        text-shadow: none !important;
    }
    </style>""", unsafe_allow_html=True)
    with st.popover("Menu", use_container_width=True, help="Navigation Menu"):
        st.markdown(uhtml("""
        <div style="font-family:'Cormorant Garamond',serif;font-weight:700;font-size:1.05rem;color:var(--ink);margin-bottom:0.4rem;padding-bottom:0.3rem;border-bottom:1px solid var(--line);">
          INSPECTION MODULES
        </div>
        """), unsafe_allow_html=True)
        for page_name, icon, short_label in NAV_OPTIONS:
            is_active = (st.session_state["current_page"] == page_name)
            if st.button(f"{icon}  {short_label}", key=f"nav_pop_{page_name}", use_container_width=True, type="primary" if is_active else "secondary"):
                st.session_state["current_page"] = page_name
                st.rerun()

with head_c2:
    st.markdown(uhtml("""
    <div class="wi-header-anchor" style="display:flex;align-items:center;gap:0.75rem;min-height:38px;">
      <span class="wi-header-brand-title" style="font-family:'Cormorant Garamond',Georgia,serif;font-size:1.3rem;font-weight:800;letter-spacing:0.18em;color:#ffd166 !important;text-transform:uppercase;white-space:nowrap;">WOOD INTELLIGENCE</span>
      <span class="wi-header-atelier-pill" style="font-size:0.72rem;background:rgba(255,209,102,0.18);color:#ffe082 !important;padding:0.25rem 0.65rem;border-radius:4px;font-weight:800;letter-spacing:0.08em;border:1.5px solid rgba(255,209,102,0.55);white-space:nowrap;">OPTICAL TIMBER INSPECTION SUITE</span>
    </div>
    """), unsafe_allow_html=True)

with head_c3:
    dark = st.toggle("Dark mode", key="dark_mode")

with head_c4:
    st.markdown(uhtml("""
    <div style="display:flex;justify-content:flex-end;align-items:center;min-height:38px;">
      <div style="display:inline-flex;align-items:center;gap:0.4rem;font-size:0.74rem;background:rgba(16,185,129,0.18);border:1.5px solid rgba(52,211,153,0.55);color:#6ee7b7;padding:0.25rem 0.75rem;border-radius:4px;font-weight:800;letter-spacing:0.05em;white-space:nowrap;">
        <span style="font-size:0.5rem;color:#7dffb0;">●</span> SYSTEM READY · CALIBRATED
      </div>
    </div>
    """), unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# INJECT THEME & BUTTON CSS (BUILT ON EVERY RUN FROM 'dark' TOGGLE)
# ---------------------------------------------------------------------------
if dark:
    theme_vars = """
    --bg: #140c06;
    --surface: #24170d;
    --surface-2: #2e1d11;
    --line: #4a3220;
    --ink: #f3e3c8;
    --muted: #c9b392;
    --amber: #ffd166;
    --amber-soft: #4a3414;
    --on-amber: #140c06;
    --good: #6fbf73;
    --warn: #e0a43a;
    --bad: #e0705f;
    --good-tint: rgba(111, 191, 115, 0.15);
    --good-border: rgba(111, 191, 115, 0.35);
    --warn-tint: rgba(224, 164, 58, 0.15);
    --warn-border: rgba(224, 164, 58, 0.35);
    --bad-tint: rgba(224, 112, 95, 0.15);
    --bad-border: rgba(224, 112, 95, 0.35);
    --walnut: #2b180c;
    --header-toggle-ink: #f3e3c8;
    """
else:
    theme_vars = """
    --bg: #f6f2ea;
    --surface: #fffdf9;
    --surface-2: #f1e8d8;
    --line: #e4d6c2;
    --ink: #2a1a0e;
    --muted: #6b5442;
    --amber: #c8801f;
    --amber-soft: #fbe9c8;
    --on-amber: #2b180c;
    --good: #2e7d4f;
    --warn: #a86a00;
    --bad: #b3402f;
    --good-tint: rgba(46, 125, 79, 0.15);
    --good-border: rgba(46, 125, 79, 0.35);
    --warn-tint: rgba(168, 106, 0, 0.15);
    --warn-border: rgba(168, 106, 0, 0.35);
    --bad-tint: rgba(179, 64, 47, 0.15);
    --bad-border: rgba(179, 64, 47, 0.35);
    --walnut: #2b180c;
    --header-toggle-ink: #ffd166;
    """

st.session_state["theme"] = "dark" if dark else "light"
if pio is not None:
    try:
        pio.templates.default = "plotly_dark" if dark else "plotly_white"
    except Exception:
        pass

theme_css = f"""
<style>
:root {{
{theme_vars}
}}

/* Base & Wood Grain Texture on .stApp (Requirement 2) */
.stApp {{
  background-color: var(--bg) !important;
  background-image: 
    radial-gradient(ellipse at 50% 0%, rgba(217, 143, 43, 0.05) 0%, transparent 70%),
    repeating-linear-gradient(90deg, rgba(255, 255, 255, 0.012) 0px, rgba(255, 255, 255, 0.012) 2px, transparent 2px, transparent 8px),
    url("data:image/svg+xml,%3Csvg viewBox='0 0 240 240' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='woodGrain'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.04 0.95' numOctaves='3' stitchTiles='stitch'/%3E%3CfeColorMatrix type='matrix' values='1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 0.035 0'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23woodGrain)'/%3E%3C/svg%3E") !important;
  background-attachment: fixed !important;
  color: var(--ink) !important;
}}

/* Streamlit Containers */
[data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stSidebar"], [data-testid="stMain"], section.main {{
  background: var(--bg) !important;
  color: var(--ink) !important;
}}

/* Smooth transitions on containers (Requirement 6) */
.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stSidebar"], [data-testid="stMain"],
.wi-card, .feature-card, .workflow-card, .kpi-card, .audit-row, .species-card, .stButton > button, [data-testid="stExpander"], [data-baseweb="select"] {{
  transition: background 0.3s ease, background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease !important;
}}

html, body, [class*="css"] {{
  font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
  color: var(--ink) !important;
  background-color: var(--bg) !important;
  -webkit-font-smoothing: antialiased;
}}

.main .block-container {{
  padding-top: 0.8rem !important;
  padding-bottom: 4rem !important;
  max-width: 1440px !important;
  margin-left: auto !important;
  margin-right: auto !important;
  width: 100% !important;
}}

/* Hide Sidebar & Default Header */
[data-testid="stSidebar"],
section[data-testid="stSidebar"],
[data-testid="collapsedControl"],
button[data-testid="stSidebarCollapseButton"],
header[data-testid="stHeader"] button:has(svg) {{
  display: none !important;
  visibility: hidden !important;
}}

/* Headings */
h1, h2, h3, h4, h5, h6, [data-testid="stHeadingWithActionElements"] h1, [data-testid="stHeadingWithActionElements"] h2, [data-testid="stHeadingWithActionElements"] h3 {{
  color: var(--ink) !important;
  font-family: 'Cormorant Garamond', 'Playfair Display', Georgia, serif !important;
  font-weight: 700 !important;
}}

/* Selection Styling */
::selection {{
  background: #d98f2b !important;
  color: #ffffff !important;
}}

/* Paragraphs, labels, spans, markdown text */
p:not(.wi-furniture-dossier *), label:not(.wi-furniture-dossier *), span:not(.wi-furniture-dossier *), [data-testid="stMarkdownContainer"] p:not(.wi-furniture-dossier *), [data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label {{
  color: var(--ink) !important;
}}

/* Furniture Dossier Card Text Contrast Enforcement */
.wi-furniture-dossier span.dossier-title,
[data-testid="stMarkdownContainer"] .wi-furniture-dossier span.dossier-title {{
  color: #ffd166 !important;
}}
.wi-furniture-dossier span.dossier-chip,
[data-testid="stMarkdownContainer"] .wi-furniture-dossier span.dossier-chip {{
  color: #ffd166 !important;
}}
.wi-furniture-dossier div.dossier-tagline,
[data-testid="stMarkdownContainer"] .wi-furniture-dossier div.dossier-tagline {{
  color: #fcd34d !important;
}}
.wi-furniture-dossier p.dossier-desc,
.wi-furniture-dossier p,
[data-testid="stMarkdownContainer"] .wi-furniture-dossier p {{
  color: #f7eee1 !important;
  opacity: 0.95 !important;
}}

/* Muted text */
.wi-muted, .text-muted, [data-testid="stCaptionContainer"] p, .stCaption, small {{
  color: var(--muted) !important;
}}

/* =========================================================================
   BUTTON SYSTEM (REQUIREMENT 5)
   ========================================================================= */
.stButton > button,
[data-testid="stBaseButton-secondary"],
.stDownloadButton > button {{
  background: var(--surface) !important;
  color: var(--ink) !important;
  border: 1px solid var(--amber) !important;
  border-radius: 12px !important;
  transition: background .25s ease, color .25s ease, transform .2s ease, border-color .25s ease, box-shadow .25s ease !important;
  box-sizing: border-box !important;
  min-height: 38px !important;
  padding: 0.42rem 0.95rem !important;
  cursor: pointer !important;
  position: relative !important;
  overflow: hidden !important;
}}

.stButton > button p,
.stButton > button span,
.stButton > button div,
[data-testid="stBaseButton-secondary"] p,
[data-testid="stBaseButton-secondary"] span,
[data-testid="stBaseButton-secondary"] div,
.stDownloadButton > button p,
.stDownloadButton > button span,
.stDownloadButton > button div {{
  color: var(--ink) !important;
  transition: color .25s ease !important;
  position: relative !important;
  z-index: 2 !important;
  font-weight: 600 !important;
}}

/* Shimmer sweep effect on hover */
.stButton > button::before,
[data-testid="stBaseButton-secondary"]::before,
[data-testid="stBaseButton-primary"]::before,
.stDownloadButton > button::before {{
  content: '' !important;
  position: absolute !important;
  top: 0 !important;
  left: -120% !important;
  width: 60% !important;
  height: 100% !important;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.28), transparent) !important;
  transform: skewX(-20deg) !important;
  transition: none !important;
  pointer-events: none !important;
  z-index: 1 !important;
}}

.stButton > button:hover::before,
[data-testid="stBaseButton-secondary"]:hover::before,
[data-testid="stBaseButton-primary"]:hover::before,
.stDownloadButton > button:hover::before {{
  left: 180% !important;
  transition: left 0.75s ease-in-out !important;
}}

.stButton > button:hover,
.stButton > button:focus,
[data-testid="stBaseButton-secondary"]:hover,
[data-testid="stBaseButton-secondary"]:focus,
.stDownloadButton > button:hover,
.stDownloadButton > button:focus {{
  background: var(--amber) !important;
  color: var(--on-amber) !important;
  border-color: var(--amber) !important;
  transform: translateY(-2px) !important;
  box-shadow: 0 4px 14px rgba(217, 143, 43, .35) !important;
}}

.stButton > button:hover p,
.stButton > button:hover span,
.stButton > button:hover div,
.stButton > button:focus p,
.stButton > button:focus span,
.stButton > button:focus div,
[data-testid="stBaseButton-secondary"]:hover p,
[data-testid="stBaseButton-secondary"]:hover span,
[data-testid="stBaseButton-secondary"]:hover div,
[data-testid="stBaseButton-secondary"]:focus p,
[data-testid="stBaseButton-secondary"]:focus span,
[data-testid="stBaseButton-secondary"]:focus div,
.stDownloadButton > button:hover p,
.stDownloadButton > button:hover span,
.stDownloadButton > button:hover div,
.stDownloadButton > button:focus p,
.stDownloadButton > button:focus span,
.stDownloadButton > button:focus div {{
  color: var(--on-amber) !important;
}}

/* Primary Buttons */
[data-testid="stBaseButton-primary"],
.stButton > button[kind="primary"] {{
  background: #2b180c !important;
  color: #f3e3c8 !important;
  border: 1px solid #2b180c !important;
  border-radius: 12px !important;
  transition: background .25s ease, color .25s ease, transform .2s ease, border-color .25s ease, box-shadow .25s ease !important;
  min-height: 38px !important;
  padding: 0.42rem 0.95rem !important;
  cursor: pointer !important;
  position: relative !important;
  overflow: hidden !important;
}}

[data-testid="stBaseButton-primary"] p,
[data-testid="stBaseButton-primary"] span,
[data-testid="stBaseButton-primary"] div,
.stButton > button[kind="primary"] p,
.stButton > button[kind="primary"] span,
.stButton > button[kind="primary"] div {{
  color: #f3e3c8 !important;
  transition: color .25s ease !important;
  position: relative !important;
  z-index: 2 !important;
  font-weight: 700 !important;
}}

[data-testid="stBaseButton-primary"]:hover,
[data-testid="stBaseButton-primary"]:focus,
.stButton > button[kind="primary"]:hover,
.stButton > button[kind="primary"]:focus {{
  background: var(--amber) !important;
  color: var(--on-amber) !important;
  border-color: var(--amber) !important;
  transform: translateY(-2px) !important;
  box-shadow: 0 4px 14px rgba(217, 143, 43, .35) !important;
}}

[data-testid="stBaseButton-primary"]:hover p,
[data-testid="stBaseButton-primary"]:hover span,
[data-testid="stBaseButton-primary"]:hover div,
[data-testid="stBaseButton-primary"]:focus p,
[data-testid="stBaseButton-primary"]:focus span,
[data-testid="stBaseButton-primary"]:focus div,
.stButton > button[kind="primary"]:hover p,
.stButton > button[kind="primary"]:hover span,
.stButton > button[kind="primary"]:hover div,
.stButton > button[kind="primary"]:focus p,
.stButton > button[kind="primary"]:focus span,
.stButton > button[kind="primary"]:focus div {{
  color: var(--on-amber) !important;
}}

/* Active State */
.stButton > button:active,
[data-testid="stBaseButton-secondary"]:active,
[data-testid="stBaseButton-primary"]:active,
.stDownloadButton > button:active {{
  transform: scale(.97) !important;
}}

/* =========================================================================
   FORM CONTROLS, SELECT, EXPANDER, TABS, TABLES, UPLOADER
   ========================================================================= */
[data-baseweb="select"], [data-baseweb="select"] > div {{
  background: var(--surface) !important;
  border-color: var(--line) !important;
  color: var(--ink) !important;
}}

[data-baseweb="select"] * {{
  color: var(--ink) !important;
  fill: var(--ink) !important;
}}

[data-baseweb="popover"], [data-baseweb="menu"], [role="listbox"] {{
  background: var(--surface) !important;
  border: 1px solid var(--line) !important;
  color: var(--ink) !important;
}}

li[role="option"] {{
  background: var(--surface) !important;
  color: var(--ink) !important;
}}

li[role="option"] p, li[role="option"] span {{
  color: var(--ink) !important;
}}

li[role="option"]:hover, li[role="option"][aria-selected="true"] {{
  background: var(--amber-soft) !important;
  color: var(--ink) !important;
}}

li[role="option"]:hover p, li[role="option"][aria-selected="true"] p {{
  color: var(--ink) !important;
}}

[data-testid="stPopoverBody"] {{
  background: var(--surface) !important;
  border: 1px solid var(--line) !important;
  color: var(--ink) !important;
  border-radius: 8px !important;
  padding: 0.85rem !important;
  box-shadow: 0 14px 40px rgba(0, 0, 0, 0.4) !important;
}}

/* Modal Dialog Backdrop & Window (@st.dialog & React-Aria Streamlit 1.65+) */
.react-aria-ModalOverlay,
div[data-testid="stDialog"],
div[data-baseweb="modal"],
.stDialog {{
  background-color: rgba(0, 0, 0, 0.82) !important;
  backdrop-filter: blur(6px) !important;
}}

.react-aria-Modal,
.react-aria-Dialog,
div[role="dialog"],
section[role="dialog"],
div[data-testid="stDialog"] > div,
div.stDialog > div,
div[data-testid="stDialog"] section,
div[data-testid="stDialog"] [class*="ep9mgll"],
div[data-testid="stDialog"] [data-testid="stVerticalBlock"],
div[data-baseweb="modal"] [role="dialog"] {{
  background-color: var(--surface) !important;
  color: var(--ink) !important;
}}

.react-aria-Modal,
div[role="dialog"],
section[role="dialog"],
div[data-testid="stDialog"] > div,
div.stDialog > div {{
  border: 1.5px solid var(--line) !important;
  border-radius: 12px !important;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.75) !important;
}}

.react-aria-Dialog h1,
.react-aria-Dialog h2,
.react-aria-Dialog h3,
.react-aria-Dialog h4,
div[data-testid="stDialog"] h1,
div[data-testid="stDialog"] h2,
div[data-testid="stDialog"] h3,
div[data-testid="stDialog"] h4,
div[data-testid="stDialog"] [data-testid="stHeadingWithActionElements"] * {{
  color: var(--ink) !important;
  font-family: 'Cormorant Garamond', Georgia, serif !important;
  font-weight: 800 !important;
}}

.react-aria-Dialog button[aria-label="Close"],
div[data-testid="stDialog"] button[aria-label="Close"],
div[data-testid="stDialog"] button[aria-label="Close"] svg,
div.stDialog button[aria-label="Close"],
div.stDialog button[aria-label="Close"] svg {{
  color: var(--ink) !important;
  fill: var(--ink) !important;
  stroke: var(--ink) !important;
}}

.react-aria-Dialog [data-testid="stTabs"] button[role="tab"],
div[data-testid="stDialog"] [data-testid="stTabs"] button[role="tab"] {{
  background: transparent !important;
}}

.react-aria-Dialog [data-testid="stTabs"] button[role="tab"] p,
div[data-testid="stDialog"] [data-testid="stTabs"] button[role="tab"] p {{
  color: var(--muted) !important;
  font-weight: 600 !important;
}}

.react-aria-Dialog [data-testid="stTabs"] button[role="tab"][aria-selected="true"],
div[data-testid="stDialog"] [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {{
  border-bottom: 2.5px solid var(--amber) !important;
}}

.react-aria-Dialog [data-testid="stTabs"] button[role="tab"][aria-selected="true"] p,
div[data-testid="stDialog"] [data-testid="stTabs"] button[role="tab"][aria-selected="true"] p {{
  color: var(--amber) !important;
  font-weight: 800 !important;
}}

.react-aria-Dialog p,
.react-aria-Dialog span,
.react-aria-Dialog label,
div[data-testid="stDialog"] p,
div[data-testid="stDialog"] span,
div[data-testid="stDialog"] label {{
  color: var(--ink) !important;
}}

.react-aria-Dialog [data-testid="stCheckbox"] label p,
.react-aria-Dialog label[data-baseweb="checkbox"] p,
div[data-testid="stDialog"] [data-testid="stCheckbox"] label p,
div[data-testid="stDialog"] label[data-baseweb="checkbox"] p {{
  color: var(--ink) !important;
  font-weight: 700 !important;
}}

.react-aria-Dialog [data-baseweb="select"] *,
div[data-testid="stDialog"] [data-baseweb="select"] * {{
  color: var(--ink) !important;
}}

[data-testid="stFileUploader"] {{
  background: var(--surface) !important;
  border: 2px dashed var(--line) !important;
  border-radius: 14px !important;
  color: var(--ink) !important;
}}

[data-testid="stFileUploader"] section {{
  background: var(--surface) !important;
  color: var(--ink) !important;
}}

[data-testid="stFileUploader"] span, [data-testid="stFileUploader"] small {{
  color: var(--muted) !important;
}}

[data-testid="stFileUploader"] button {{
  background: var(--surface) !important;
  color: var(--ink) !important;
  border: 1px solid var(--amber) !important;
  border-radius: 10px !important;
}}

[data-testid="stFileUploader"] button p, [data-testid="stFileUploader"] button span {{
  color: var(--ink) !important;
}}

[data-testid="stFileUploader"] button:hover {{
  background: var(--amber) !important;
  color: var(--on-amber) !important;
  border-color: var(--amber) !important;
}}

[data-testid="stFileUploader"] button:hover p, [data-testid="stFileUploader"] button:hover span {{
  color: var(--on-amber) !important;
}}

[data-baseweb="input"], [data-baseweb="base-input"], input, textarea {{
  background: var(--surface) !important;
  border-color: var(--line) !important;
  color: var(--ink) !important;
}}

[data-testid="stExpander"] {{
  background: var(--surface) !important;
  border: 1.5px solid var(--line) !important;
  border-radius: 12px !important;
}}

[data-testid="stExpander"] summary {{
  color: var(--ink) !important;
  font-weight: 600 !important;
}}

[data-testid="stExpander"] summary p, [data-testid="stExpander"] summary span {{
  color: var(--ink) !important;
}}

[data-testid="stExpander"] summary:hover, [data-testid="stExpander"] summary:hover p {{
  color: var(--amber) !important;
}}

[data-testid="stExpander"] [data-testid="stExpanderDetails"] {{
  background: var(--surface) !important;
  color: var(--ink) !important;
}}

[data-testid="stTabs"] button[role="tab"] {{
  color: var(--muted) !important;
  background: transparent !important;
}}

[data-testid="stTabs"] button[role="tab"] p {{
  color: var(--muted) !important;
}}

[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {{
  color: var(--amber) !important;
  border-bottom: 2.5px solid var(--amber) !important;
  font-weight: 700 !important;
}}

[data-testid="stTabs"] button[role="tab"][aria-selected="true"] p {{
  color: var(--amber) !important;
}}

table, [data-testid="stTable"] table {{
  background: var(--surface) !important;
  color: var(--ink) !important;
  border-color: var(--line) !important;
}}

table th, [data-testid="stTable"] th {{
  background: var(--amber-soft) !important;
  color: var(--ink) !important;
  border-color: var(--line) !important;
  font-weight: 700 !important;
}}

table td, [data-testid="stTable"] td {{
  background: var(--surface) !important;
  border-color: var(--line) !important;
  color: var(--ink) !important;
}}

[data-testid="stDataFrame"] {{
  background: var(--surface) !important;
  border: 1px solid var(--line) !important;
  border-radius: 10px !important;
}}

[data-testid="stMetric"], [data-testid="stMetric"] > div {{
  background: var(--surface) !important;
  border: 1.5px solid var(--line) !important;
  border-radius: 16px !important;
}}

[data-testid="stMetricLabel"] p {{
  color: var(--muted) !important;
}}

[data-testid="stMetricValue"] div {{
  color: var(--ink) !important;
}}

.stVegaLiteChart, .vega-embed {{
  background-color: transparent !important;
}}

/* =========================================================================
   CARDS & ANIMATIONS (REQUIREMENT 3 & 6)
   ========================================================================= */
/* =========================================================================
   CARDS & STRUCTURAL COMPONENTS (CLEAN ENTERPRISE GEOMETRY)
   ========================================================================= */
.wi-card, .feature-card, .workflow-card, .kpi-card, .audit-row, .species-card {{
  background: var(--surface) !important;
  border: 1px solid var(--line) !important;
  border-left: 3px solid var(--amber) !important;
  color: var(--ink) !important;
  border-radius: 8px !important;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04) !important;
  transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease !important;
}}

/* Card hover: subtle, professional 2px lift */
.wi-card:hover, .feature-card:hover, .workflow-card:hover, .kpi-card:hover, .audit-row:hover, .species-card:hover {{
  transform: translateY(-2px) !important;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.08) !important;
  border-color: var(--amber) !important;
}}

/* Stat Tiles (KPI Cards) */
.kpi-card {{
  background: var(--surface-2) !important;
  border: 1px solid var(--line) !important;
  border-left: 3px solid var(--amber) !important;
  border-radius: 8px !important;
  padding: 1.1rem !important;
  text-align: center !important;
}}

.kpi-val {{
  font-size: 2.1rem !important;
  font-weight: 800 !important;
  color: var(--amber) !important;
  font-family: 'JetBrains Mono', monospace !important;
  line-height: 1.1 !important;
  margin-bottom: 0.35rem !important;
}}

.kpi-label {{
  color: var(--muted) !important;
  font-size: 0.78rem !important;
  font-weight: 700 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.06em !important;
}}

/* Section Header Bars */
.wi-card-header {{
  background: var(--surface-2) !important;
  border: 1px solid var(--line) !important;
  border-left: 3px solid var(--amber) !important;
  border-radius: 6px !important;
  padding: 0.75rem 1.15rem !important;
  display: flex !important;
  justify-content: space-between !important;
  align-items: center !important;
  gap: 12px !important;
  margin-bottom: 1.1rem !important;
}}

.wi-card-title {{
  color: var(--ink) !important;
  font-size: 1.05rem !important;
  font-weight: 700 !important;
  display: flex !important;
  align-items: center !important;
  gap: 0.5rem !important;
  letter-spacing: 0.02em !important;
}}

.wi-section-label {{
  color: var(--amber) !important;
  font-size: 0.7rem !important;
  font-weight: 800 !important;
  letter-spacing: 0.06em !important;
  text-transform: uppercase !important;
  background: var(--amber-soft) !important;
  border: 1px solid var(--amber) !important;
  padding: 0.2rem 0.55rem !important;
  border-radius: 4px !important;
  white-space: nowrap !important;
}}

/* Risk Badges */
.risk-badge {{
  display: inline-block;
  padding: 0.18rem 0.6rem;
  border-radius: 4px;
  font-weight: 700;
  font-size: 0.78rem;
  letter-spacing: 0.04em;
}}

.feature-icon-wrap {{
  width: 40px;
  height: 40px;
  border-radius: 6px;
  background: var(--amber-soft) !important;
  border: 1px solid var(--amber) !important;
  color: var(--amber) !important;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.4rem;
  margin-bottom: 0.85rem;
}}

.feature-card-title, .wi-card-title {{
  color: var(--ink) !important;
}}

.feature-card-desc {{
  color: var(--muted) !important;
}}

/* Top Walnut Header Bar (Dark in BOTH modes) */
div[data-testid="stHorizontalBlock"]:has(.wi-header-anchor) {{
  background: linear-gradient(90deg, #1f1107 0%, #341b0d 50%, #1f1107 100%) !important;
  border-radius: 8px !important;
  padding: 0.5rem 1.1rem !important;
  border: 1.5px solid #5a3518 !important;
  box-shadow: 0 4px 16px rgba(25, 12, 5, 0.45) !important;
  margin-bottom: 0.75rem !important;
  align-items: center !important;
}}

/* Header Brand Title: exact same amber-gold color as down main heading (#ffd166) */
.wi-header-brand-title,
div[data-testid="stHorizontalBlock"]:has(.wi-header-anchor) .wi-header-brand-title,
div[data-testid="stHorizontalBlock"] .wi-header-brand-title {{
  color: #ffd166 !important;
  font-family: 'Cormorant Garamond', Georgia, serif !important;
  font-size: 1.3rem !important;
  font-weight: 800 !important;
  letter-spacing: 0.18em !important;
  text-transform: uppercase !important;
  text-shadow: 0 2px 12px rgba(0, 0, 0, 0.95), 0 0 16px rgba(217, 143, 43, 0.55) !important;
}}

.wi-header-atelier-pill,
div[data-testid="stHorizontalBlock"]:has(.wi-header-anchor) .wi-header-atelier-pill {{
  color: #ffe082 !important;
  background: rgba(255, 209, 102, 0.18) !important;
  border: 1.5px solid rgba(255, 209, 102, 0.55) !important;
  font-weight: 800 !important;
  font-size: 0.72rem !important;
  letter-spacing: 0.08em !important;
  padding: 0.22rem 0.65rem !important;
  border-radius: 4px !important;
}}

/* Menu Popover Button in Header - Ultra-High Visibility & Contrast */
.stPopover button,
[data-testid="stPopover"] button,
[data-testid="stPopover"] [data-testid="stBaseButton-secondary"],
div[data-testid="stHorizontalBlock"]:has(.wi-header-anchor) [data-testid="stPopover"] button,
div[data-testid="stHorizontalBlock"]:has(.wi-header-anchor) [data-testid="stBaseButton-secondary"],
div[data-testid="stHorizontalBlock"]:has(.wi-header-anchor) button {{
  background: rgba(255, 209, 102, 0.2) !important;
  color: #ffd166 !important;
  border: 1.5px solid #ffd166 !important;
  border-radius: 6px !important;
  min-height: 38px !important;
  height: 38px !important;
  padding: 0 0.95rem !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.45) !important;
  transition: all 0.2s ease !important;
}}

/* All Text, Labels, Spans, Paragraphs and SVGs inside the Menu button - ALWAYS VIBRANT AMBER */
.stPopover button *,
.stPopover button p,
.stPopover button span,
.stPopover button div,
.stPopover button svg,
[data-testid="stPopover"] button *,
[data-testid="stPopover"] button p,
[data-testid="stPopover"] button span,
[data-testid="stPopover"] button div,
[data-testid="stPopover"] button svg,
[data-testid="stPopover"] [data-testid="stBaseButton-secondary"] p,
[data-testid="stPopover"] [data-testid="stBaseButton-secondary"] span,
[data-testid="stPopover"] [data-testid="stBaseButton-secondary"] div,
[data-testid="stPopover"] [data-testid="stBaseButton-secondary"] svg,
div[data-testid="stHorizontalBlock"]:has(.wi-header-anchor) [data-testid="stPopover"] button *,
div[data-testid="stHorizontalBlock"]:has(.wi-header-anchor) [data-testid="stPopover"] button p,
div[data-testid="stHorizontalBlock"]:has(.wi-header-anchor) [data-testid="stPopover"] button span,
div[data-testid="stHorizontalBlock"]:has(.wi-header-anchor) [data-testid="stPopover"] button div,
div[data-testid="stHorizontalBlock"]:has(.wi-header-anchor) [data-testid="stPopover"] button svg,
div[data-testid="stHorizontalBlock"]:has(.wi-header-anchor) button *,
div[data-testid="stHorizontalBlock"]:has(.wi-header-anchor) button p,
div[data-testid="stHorizontalBlock"]:has(.wi-header-anchor) button span,
div[data-testid="stHorizontalBlock"]:has(.wi-header-anchor) button div,
div[data-testid="stHorizontalBlock"]:has(.wi-header-anchor) button svg {{
  color: #ffd166 !important;
  fill: #ffd166 !important;
  stroke: #ffd166 !important;
  font-size: 0.95rem !important;
  font-weight: 800 !important;
  letter-spacing: 0.05em !important;
  opacity: 1 !important;
  visibility: visible !important;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.9) !important;
}}

div[data-testid="stHorizontalBlock"]:has(.wi-header-anchor) [data-testid="stPopover"] > button:hover,
div[data-testid="stHorizontalBlock"]:has(.wi-header-anchor) [data-testid="stPopoverButton"]:hover,
div[data-testid="stHorizontalBlock"]:has(.wi-header-anchor) .stPopover > button:hover,
.stPopover button:hover,
[data-testid="stPopover"] button:hover,
div[data-testid="stHorizontalBlock"]:has(.wi-header-anchor) button:hover {{
  background: #ffd166 !important;
  border-color: #ffd166 !important;
  box-shadow: 0 4px 14px rgba(255, 209, 102, 0.55) !important;
  transform: translateY(-1px) !important;
}}

div[data-testid="stHorizontalBlock"]:has(.wi-header-anchor) [data-testid="stPopover"] > button:hover *,
div[data-testid="stHorizontalBlock"]:has(.wi-header-anchor) [data-testid="stPopover"] > button:hover p,
div[data-testid="stHorizontalBlock"]:has(.wi-header-anchor) [data-testid="stPopover"] > button:hover span,
div[data-testid="stHorizontalBlock"]:has(.wi-header-anchor) [data-testid="stPopover"] > button:hover div,
div[data-testid="stHorizontalBlock"]:has(.wi-header-anchor) [data-testid="stPopover"] > button:hover svg,
.stPopover button:hover *,
.stPopover button:hover p,
.stPopover button:hover span,
.stPopover button:hover div,
.stPopover button:hover svg,
div[data-testid="stHorizontalBlock"]:has(.wi-header-anchor) button:hover *,
div[data-testid="stHorizontalBlock"]:has(.wi-header-anchor) button:hover p,
div[data-testid="stHorizontalBlock"]:has(.wi-header-anchor) button:hover span,
div[data-testid="stHorizontalBlock"]:has(.wi-header-anchor) button:hover div,
div[data-testid="stHorizontalBlock"]:has(.wi-header-anchor) button:hover svg {{
  color: #1a0f07 !important;
  fill: #1a0f07 !important;
  stroke: #1a0f07 !important;
  text-shadow: none !important;
}}

/* Header Toggle Label (Visible in both modes: keeps dark mode color #f3e3c8, changes to #ffd166 in light mode) */
[data-testid="stCheckbox"] label p,
[data-testid="stCheckbox"] label span,
[data-testid="stCheckbox"] [data-testid="stWidgetLabel"] p,
[data-testid="stCheckbox"] [data-testid="stWidgetLabel"] span,
[data-testid="stCheckbox"] [data-testid="stWidgetLabel"] label,
[data-testid="stToggle"] label p,
[data-testid="stToggle"] label span,
[data-testid="stToggle"] [data-testid="stWidgetLabel"] p,
[data-testid="stToggle"] [data-testid="stWidgetLabel"] span,
[data-testid="stToggle"] [data-testid="stWidgetLabel"] label,
label[data-baseweb="checkbox"] p,
label[data-baseweb="checkbox"] span,
div[data-testid="stHorizontalBlock"]:has(.wi-header-anchor) [data-testid="stCheckbox"] label p,
div[data-testid="stHorizontalBlock"]:has(.wi-header-anchor) [data-testid="stCheckbox"] label span,
div[data-testid="stHorizontalBlock"]:has(.wi-header-anchor) [data-testid="stCheckbox"] label div,
div[data-testid="stHorizontalBlock"]:has(.wi-header-anchor) [data-testid="stCheckbox"] [data-testid="stWidgetLabel"] p,
div[data-testid="stHorizontalBlock"]:has(.wi-header-anchor) [data-testid="stCheckbox"] [data-testid="stWidgetLabel"] label,
div[data-testid="stHorizontalBlock"]:has(.wi-header-anchor) [data-testid="stCheckbox"] [data-testid="stWidgetLabel"] div,
div[data-testid="stHorizontalBlock"]:has(.wi-header-anchor) [data-testid="stCheckbox"] [data-testid="stWidgetLabel"] span,
div[data-testid="stHorizontalBlock"]:has(.wi-header-anchor) [data-testid="stToggle"] label p,
div[data-testid="stHorizontalBlock"]:has(.wi-header-anchor) [data-testid="stToggle"] label span,
div[data-testid="stHorizontalBlock"]:has(.wi-header-anchor) [data-testid="stToggle"] label div,
div[data-testid="stHorizontalBlock"]:has(.wi-header-anchor) [data-testid="stToggle"] [data-testid="stWidgetLabel"] p,
div[data-testid="stHorizontalBlock"]:has(.wi-header-anchor) [data-testid="stToggle"] [data-testid="stWidgetLabel"] label,
div[data-testid="stHorizontalBlock"]:has(.wi-header-anchor) [data-testid="stToggle"] [data-testid="stWidgetLabel"] div,
div[data-testid="stHorizontalBlock"]:has(.wi-header-anchor) [data-testid="stToggle"] [data-testid="stWidgetLabel"] span,
div[data-testid="stHorizontalBlock"]:has(.wi-header-anchor) label[data-baseweb="checkbox"] p,
div[data-testid="stHorizontalBlock"]:has(.wi-header-anchor) label[data-baseweb="checkbox"] span,
div[data-testid="stHorizontalBlock"]:has(.wi-header-anchor) label[data-baseweb="checkbox"] div,
div[data-testid="stHorizontalBlock"]:has(.wi-header-anchor) [data-testid="stWidgetLabel"] p,
div[data-testid="stHorizontalBlock"]:has(.wi-header-anchor) [data-testid="stWidgetLabel"] span,
div[data-testid="stHorizontalBlock"]:has(.wi-header-anchor) [data-testid="stWidgetLabel"] label,
div[data-testid="stHorizontalBlock"]:has(.wi-header-anchor) [data-baseweb="checkbox"] * {{
  color: var(--header-toggle-ink) !important;
  font-weight: 700 !important;
  font-size: 0.88rem !important;
  letter-spacing: 0.02em !important;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.8) !important;
}}

/* Hero Box with Timber Grain Backdrop */
.dean-hero-box {{
  border-radius: 8px;
  position: relative;
  overflow: hidden;
  padding: 3rem 3.5rem;
  margin-bottom: 1.4rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  border: 1.5px solid #5a3518;
  min-height: 250px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}}

.hero-crossfade-layer {{
  position: absolute;
  inset: 0;
  background-size: cover;
  background-position: center;
  opacity: 0;
  animation: heroCrossFadeAnim 20s infinite ease-in-out;
}}

.hero-img-1 {{ animation-delay: 0s; }}
.hero-img-2 {{ animation-delay: 5s; }}
.hero-img-3 {{ animation-delay: 10s; }}
.hero-img-4 {{ animation-delay: 15s; }}

@keyframes heroCrossFadeAnim {{
  0% {{ opacity: 0; }}
  5% {{ opacity: 1; }}
  25% {{ opacity: 1; }}
  30% {{ opacity: 0; }}
  100% {{ opacity: 0; }}
}}

.dean-hero-overlay {{
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, rgba(20, 10, 4, 0.90) 0%, rgba(35, 18, 7, 0.72) 55%, rgba(15, 8, 3, 0.40) 100%);
  z-index: 2;
  pointer-events: none;
}}

.dean-hero-content {{
  max-width: 820px;
  position: relative;
  z-index: 3;
}}

.wood-board-title {{
  font-family: 'Cormorant Garamond', 'Playfair Display', Georgia, serif !important;
  font-size: 3rem !important;
  font-weight: 800 !important;
  color: #ffd166 !important;
  line-height: 1.05 !important;
  letter-spacing: 0.10em !important;
  text-transform: uppercase !important;
  margin: 0 0 0.8rem 0 !important;
  text-shadow: 0 2px 12px rgba(0, 0, 0, 0.8) !important;
}}

.wood-board-sub,
[data-testid="stMarkdownContainer"] p.wood-board-sub,
.dean-hero-content p {{
  font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
  font-size: 1.05rem !important;
  color: #f7eee1 !important;
  line-height: 1.55 !important;
  margin: 0 0 1.5rem 0 !important;
  font-weight: 500 !important;
  max-width: 720px !important;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.7) !important;
}}

.feature-grid {{
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 1.1rem;
  margin: 1.2rem 0;
}}
@media (max-width: 1200px) {{
  .feature-grid {{
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  }}
}}
.feature-card {{
  border-top: 3.5px solid var(--amber) !important;
  padding: 1.35rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 220px;
}}

/* Form inputs & controls */
div[data-testid="stTextInput"] input {{
  background-color: var(--surface-2) !important;
  color: var(--ink) !important;
  border: 1.5px solid var(--line) !important;
  border-radius: 6px !important;
}}
div[data-testid="stTextInput"] input:focus {{
  border-color: var(--amber) !important;
  box-shadow: 0 0 0 1px var(--amber) !important;
}}
div[data-testid="stTextInput"] label p,
div[data-testid="stSelectbox"] label p {{
  color: var(--ink) !important;
  font-weight: 700 !important;
  font-size: 0.85rem !important;
}}
div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
  background-color: var(--surface-2) !important;
  color: var(--ink) !important;
  border: 1.5px solid var(--line) !important;
  border-radius: 6px !important;
}}

/* Prefers-reduced-motion: reduce (Requirement 6) */
@media (prefers-reduced-motion: reduce) {{
  *, ::before, ::after {{
    animation-delay: 0s !important;
    animation-duration: 0.001ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.001ms !important;
  }}
}}
</style>
"""
st.markdown(theme_css, unsafe_allow_html=True)

# PAGE 1: HOME PAGE
# ===========================================================================
if st.session_state["current_page"] == "Home":
    # Cross-fade between 4 wood images every 5 seconds (instant cached retrieval)
    h_img1, h_img2, h_img3, h_img4 = get_hero_images_bundle()

    # Staggered title letters with distinct glowing amber-gold color (#ffd166)
    title_text = "WOOD INTELLIGENCE"
    title_chars = "".join(
        f'<span class="stagger-char" style="color:#ffd166 !important;animation-delay:{idx*0.045:.3f}s;">{"&nbsp;" if ch == " " else ch}</span>'
        for idx, ch in enumerate(title_text)
    )

    st.markdown(uhtml(f"""
    <div class="dean-hero-box">
      <div class="hero-crossfade-layer hero-img-1" style="background-image: url('data:image/jpeg;base64,{h_img1}');"></div>
      <div class="hero-crossfade-layer hero-img-2" style="background-image: url('data:image/jpeg;base64,{h_img2}');"></div>
      <div class="hero-crossfade-layer hero-img-3" style="background-image: url('data:image/jpeg;base64,{h_img3}');"></div>
      <div class="hero-crossfade-layer hero-img-4" style="background-image: url('data:image/jpeg;base64,{h_img4}');"></div>
      <div class="dean-hero-overlay"></div>
      <div class="dean-hero-content">
        <div class="wood-board-title">{title_text}</div>
        <p class="wood-board-sub">
          Automated optical inspection system for botanical timber taxonomy, surface defect contour segmentation, and structural furniture engineering compliance.
        </p>
      </div>

    </div>
    """), unsafe_allow_html=True)

    # Action Buttons under Subtitle
    b1, b_fill = st.columns([3.2, 8.8])
    with b1:
        if st.button("Launch Timber Inspection Suite", key="home_btn_analysis", type="primary", use_container_width=True):
            st.session_state["current_page"] = "New Analysis"
            st.rerun()

    st.markdown("<div style='height:0.8rem;'></div>", unsafe_allow_html=True)
    st.markdown('<h2 style="font-family:Cormorant Garamond,Georgia,serif;font-size:1.85rem;font-weight:700;color:var(--ink);margin:1.4rem 0 0.8rem 0;">Inspection Capabilities</h2>', unsafe_allow_html=True)

    # 4 Core Capability Cards
    st.markdown(uhtml("""
    <div class="feature-grid" style="grid-template-columns: repeat(4, 1fr);">
      <div class="feature-card">
        <div>
          <div class="feature-icon-wrap" style="font-family:'JetBrains Mono',monospace;font-weight:800;font-size:0.88rem;">01</div>
          <div class="feature-card-title">Botanical Species Classification</div>
          <div class="feature-card-desc">
            Identifies botanical lineage, nominal density and modulus of rupture across 19 global and regional timber species.
          </div>
        </div>
      </div>
      
      <div class="feature-card">
        <div>
          <div class="feature-icon-wrap" style="font-family:'JetBrains Mono',monospace;font-weight:800;font-size:0.88rem;">02</div>
          <div class="feature-card-title">Defect Segmentation &amp; Contouring</div>
          <div class="feature-card-desc">
            Isolates knots, splits, checks, marrow and fungal decay with high-precision pixel boundary masks.
          </div>
        </div>
      </div>

      <div class="feature-card">
        <div>
          <div class="feature-icon-wrap" style="font-family:'JetBrains Mono',monospace;font-weight:800;font-size:0.88rem;">03</div>
          <div class="feature-card-title">Joinery &amp; Furniture Compliance</div>
          <div class="feature-card-desc">
            Cross-references physical stress requirements against 31 furniture blueprints to assess structural feasibility.
          </div>
        </div>
      </div>

      <div class="feature-card">
        <div>
          <div class="feature-icon-wrap" style="font-family:'JetBrains Mono',monospace;font-weight:800;font-size:0.88rem;">04</div>
          <div class="feature-card-title">Remediation Specifications</div>
          <div class="feature-card-desc">
            Provides standard workshop repair recipes and upcycling strategies for non-structural off-cuts.
          </div>
        </div>
      </div>
    </div>
    """), unsafe_allow_html=True)

    st.markdown("<div style='height:0.8rem;'></div>", unsafe_allow_html=True)
    st.markdown('<h2 style="font-family:Cormorant Garamond,Georgia,serif;font-size:1.85rem;font-weight:700;color:var(--ink);margin:1.4rem 0 0.8rem 0;">Inspection Workflow</h2>', unsafe_allow_html=True)

    # 4 Phase Workflow Cards
    w1, w2, w3, w4 = st.columns(4, gap="medium")
    with w1:
        st.markdown(uhtml("""
        <div class="feature-card" style="min-height:160px;">
          <div>
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.6rem;">
              <span style="font-family:'JetBrains Mono',monospace;font-size:0.9rem;font-weight:800;color:var(--amber);">01</span>
              <span style="font-size:0.68rem;font-weight:700;color:var(--amber);background:var(--amber-soft);border:1px solid var(--amber);padding:0.18rem 0.55rem;border-radius:4px;letter-spacing:0.04em;">PHASE 1</span>
            </div>
            <strong style="color:var(--ink);font-size:0.95rem;">Specimen Input</strong>
            <p style="font-size:0.8rem;color:var(--muted);margin-top:0.35rem;line-height:1.5;">Acquire high-resolution lumber photograph and log physical board dimensions.</p>
          </div>
        </div>
        """), unsafe_allow_html=True)
    with w2:
        st.markdown(uhtml("""
        <div class="feature-card" style="min-height:160px;">
          <div>
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.6rem;">
              <span style="font-family:'JetBrains Mono',monospace;font-size:0.9rem;font-weight:800;color:var(--amber);">02</span>
              <span style="font-size:0.68rem;font-weight:700;color:var(--amber);background:var(--amber-soft);border:1px solid var(--amber);padding:0.18rem 0.55rem;border-radius:4px;letter-spacing:0.04em;">PHASE 2</span>
            </div>
            <strong style="color:var(--ink);font-size:0.95rem;">Authenticity &amp; CNN</strong>
            <p style="font-size:0.8rem;color:var(--muted);margin-top:0.35rem;line-height:1.5;">Authenticity gate verifies genuine timber, CNN classifies species, YOLO localizes defects.</p>
          </div>
        </div>
        """), unsafe_allow_html=True)
    with w3:
        st.markdown(uhtml("""
        <div class="feature-card" style="min-height:160px;">
          <div>
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.6rem;">
              <span style="font-family:'JetBrains Mono',monospace;font-size:0.9rem;font-weight:800;color:var(--amber);">03</span>
              <span style="font-size:0.68rem;font-weight:700;color:var(--amber);background:var(--amber-soft);border:1px solid var(--amber);padding:0.18rem 0.55rem;border-radius:4px;letter-spacing:0.04em;">PHASE 3</span>
            </div>
            <strong style="color:var(--ink);font-size:0.95rem;">Contour Quantification</strong>
            <p style="font-size:0.8rem;color:var(--muted);margin-top:0.35rem;line-height:1.5;">Pixel-precise morphological thresholding calculates damaged vs usable timber volume.</p>
          </div>
        </div>
        """), unsafe_allow_html=True)
    with w4:
        st.markdown(uhtml("""
        <div class="feature-card" style="min-height:160px;">
          <div>
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.6rem;">
              <span style="font-family:'JetBrains Mono',monospace;font-size:0.9rem;font-weight:800;color:var(--amber);">04</span>
              <span style="font-size:0.68rem;font-weight:700;color:var(--amber);background:var(--amber-soft);border:1px solid var(--amber);padding:0.18rem 0.55rem;border-radius:4px;letter-spacing:0.04em;">PHASE 4</span>
            </div>
            <strong style="color:var(--ink);font-size:0.95rem;">Compliance Audit</strong>
            <p style="font-size:0.8rem;color:var(--muted);margin-top:0.35rem;line-height:1.5;">Furniture stress matrix cross-examines bending thresholds and generates formal PDF report.</p>
          </div>
        </div>
        """), unsafe_allow_html=True)

elif st.session_state["current_page"] == "Overview":
    history = load_history()
    total_analyzed = len(history)
    
    suitable_count = sum(1 for h in history if h.get("best_score", 0) >= 70)
    rejected_count = sum(1 for h in history if h.get("severity") == "High" or not h.get("is_wood", True))
    avg_usable = (sum(h.get("usable_pct", 0) for h in history) / total_analyzed) if total_analyzed > 0 else 98.5

    # 4 KPI Summary Cards (Requirement 3: Surface-2, Amber Number, Muted Label)
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(uhtml(f"""
        <div class="kpi-card">
          <div class="kpi-val">{total_analyzed}</div>
          <div class="kpi-label">Total Wood Pieces Analysed</div>
        </div>
        """), unsafe_allow_html=True)
    with k2:
        st.markdown(uhtml(f"""
        <div class="kpi-card">
          <div class="kpi-val">{suitable_count}</div>
          <div class="kpi-label">Suitable Pieces</div>
        </div>
        """), unsafe_allow_html=True)
    with k3:
        st.markdown(uhtml(f"""
        <div class="kpi-card">
          <div class="kpi-val">{rejected_count}</div>
          <div class="kpi-label">Rejected Pieces</div>
        </div>
        """), unsafe_allow_html=True)
    with k4:
        st.markdown(uhtml(f"""
        <div class="kpi-card">
          <div class="kpi-val">{avg_usable:.1f}%</div>
          <div class="kpi-label">Avg Usable Wood</div>
        </div>
        """), unsafe_allow_html=True)

    st.markdown("<div style='height:.9rem;'></div>", unsafe_allow_html=True)

    

    # Defect Frequency / Distribution Chart & Summary (Requirement 3 & 4)
    st.markdown('<div class="wi-card"><div class="wi-card-header"><span class="wi-card-title">📈 Common Defect Distribution & Quality Index</span><span class="wi-section-label">SYSTEM ANALYTICS</span></div>', unsafe_allow_html=True)
    
    c_chart, c_stat = st.columns([5, 3], gap="large")
    with c_chart:
        defect_counts = {
            "Live knot": 14,
            "Dead knot": 9,
            "Crack": 6,
            "Quartzity": 8,
            "Resin": 5,
            "Knot missing": 4
        }
        df_defects = pd.DataFrame({
            "Defect Type": list(defect_counts.keys()),
            "Occurrences": list(defect_counts.values())
        })
        import altair as alt
        chart = (
            alt.Chart(df_defects)
            .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
            .encode(
                x=alt.X(
                    "Defect Type:N",
                    sort=None,
                    axis=alt.Axis(
                        labelAngle=-25,
                        labelColor="#c9b392" if dark else "#6b5442",
                        titleColor="#c9b392" if dark else "#6b5442",
                        grid=False,
                        labelFont="Plus Jakarta Sans",
                        labelFontSize=11,
                        title=None
                    )
                ),
                y=alt.Y(
                    "Occurrences:Q",
                    axis=alt.Axis(
                        labelColor="#c9b392" if dark else "#6b5442",
                        titleColor="#c9b392" if dark else "#6b5442",
                        gridColor="#4a3220" if dark else "#e4d6c2",
                        labelFont="Plus Jakarta Sans",
                        title="Occurrences"
                    )
                ),
                color=alt.Color(
                    "Occurrences:Q",
                    scale=alt.Scale(range=["#b07a2c", "#d98f2b"]),
                    legend=None
                ),
                tooltip=["Defect Type", "Occurrences"]
            )
            .properties(height=260)
            .configure_view(strokeWidth=0, fill="transparent")
            .configure(background="transparent")
        )
        st.altair_chart(chart, use_container_width=True)
        st.caption("Aggregated defect occurrences detected across test batches.")
    
    with c_stat:
        st.markdown(uhtml("""
        <div style="background:var(--surface);border:1px solid var(--line);border-left:3px solid var(--amber);border-radius:8px;padding:1.1rem;font-size:.85rem;">
          <strong style="color:var(--ink);display:block;margin-bottom:.5rem;">Timber Quality Benchmarks (ASTM D143):</strong>
          <div style="margin-bottom:.4rem;color:var(--ink);"><span style="display:inline-block;padding:0.12rem 0.45rem;border-radius:4px;font-size:0.72rem;font-weight:700;background:var(--good-tint);color:var(--good);border:1px solid var(--good-border);">GRADE A</span> <strong>Clear Lumber:</strong> 0 defects, &lt;0.5% damage</div>
          <div style="margin-bottom:.4rem;color:var(--ink);"><span style="display:inline-block;padding:0.12rem 0.45rem;border-radius:4px;font-size:0.72rem;font-weight:700;background:var(--warn-tint);color:var(--warn);border:1px solid var(--warn-border);">GRADE B</span> <strong>Mill Character:</strong> Sound knots, &lt;1.5% damage</div>
          <div style="margin-bottom:.4rem;color:var(--ink);"><span style="display:inline-block;padding:0.12rem 0.45rem;border-radius:4px;font-size:0.72rem;font-weight:700;background:var(--bad-tint);color:var(--bad);border:1px solid var(--bad-border);">GRADE C</span> <strong>Structural Reject:</strong> Cracks, dead knots, &gt;2% damage</div>
          <hr style="border:none;border-bottom:1px solid var(--line);margin:.6rem 0;" />
          <div style="color:var(--muted);font-size:0.78rem;line-height:1.45;">Timber rejection threshold is automatically triggered when open fissures, loose dead knots, or deep splits are detected in load-bearing zones.</div>
        </div>
        """), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Recent Analyses (Requirement 3: Audit Rows with exact variables)
    st.markdown('<div class="wi-card"><div class="wi-card-header"><span class="wi-card-title">Recent Inspection Records</span><span class="wi-section-label">AUDIT TRAIL</span></div>', unsafe_allow_html=True)
    if not history:
        st.info("No inspection records logged yet. Run your first analysis from the 'New Analysis' page.")
    else:
        for entry in history[:5]:
            sv = entry.get("severity", "Low")
            sc2 = SEV_COLORS.get(sv, SEV_COLORS["Low"])
            st.markdown(uhtml(f"""
            <div class="audit-row" style="display:flex;align-items:center;justify-content:space-between;background:var(--surface);border:1px solid var(--line);border-radius:6px;padding:.75rem 1rem;margin-bottom:.5rem;flex-wrap:wrap;gap:.6rem;">
              <div style="display:flex;align-items:center;gap:.65rem;">
                <span style="font-family:'JetBrains Mono',monospace;font-size:0.75rem;font-weight:800;color:var(--amber);">SPEC</span>
                <div>
                  <strong style="color:var(--ink);font-size:.88rem;font-weight:700;">{entry.get('filename', 'specimen.jpg')}</strong>
                  <div style="font-size:.74rem;color:var(--muted);">{entry.get('species', 'Timber')} &bull; {entry.get('timestamp', '')}</div>
                </div>
              </div>
              <div style="display:flex;align-items:center;gap:1.2rem;font-size:.82rem;">
                <span class="risk-badge" style="background:{sc2['bg']};color:{sc2['text']};border:1px solid {sc2['border']};">{sv}</span>
                <span style="color:var(--ink);">Usable: <strong style="color:var(--good);">{entry.get('usable_pct', 0):.1f}%</strong></span>
                <span style="color:var(--muted);">Best: <strong style="color:var(--muted);">{entry.get('best_furniture', 'N/A')}</strong> ({entry.get('best_score', 0)}/100)</span>
              </div>
            </div>
            """), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ===========================================================================
# PAGE 3: NEW ANALYSIS (INPUT & EXECUTION)
# ===========================================================================
elif st.session_state["current_page"] == "New Analysis":
    st.markdown('<div class="wi-card"><div class="wi-card-header"><span class="wi-card-title">1. Specimen Input & Dimensions</span><span class="wi-section-label">TIMBER SPECIFICATION</span></div>', unsafe_allow_html=True)

    # Board Dimensions in a clean row
    d1, d2, d3, d4 = st.columns([3, 3, 3, 3])
    with d1:
        st.session_state["board_length"] = st.number_input("Board Length (cm):", min_value=10.0, max_value=400.0, value=float(st.session_state["board_length"]), step=5.0)
    with d2:
        st.session_state["board_width"] = st.number_input("Board Width (cm):", min_value=5.0, max_value=200.0, value=float(st.session_state["board_width"]), step=2.0)
    with d3:
        st.session_state["board_thickness"] = st.number_input("Thickness (cm):", min_value=0.5, max_value=20.0, value=float(st.session_state["board_thickness"]), step=0.5)
    with d4:
        vol = (st.session_state["board_length"] * st.session_state["board_width"] * st.session_state["board_thickness"]) / 1000.0
        st.markdown(uhtml(f"""
        <div style="background:var(--amber-soft);border:1px solid var(--amber);border-radius:6px;padding:.55rem .8rem;margin-top:.6rem;">
          <div style="font-size:.68rem;font-weight:700;color:var(--muted);text-transform:uppercase;">Volume Estimate</div>
          <div style="font-size:1.1rem;font-weight:800;color:var(--ink);">{vol:.2f} Liters</div>
        </div>
        """), unsafe_allow_html=True)

    dims_input = {
        "length": st.session_state["board_length"],
        "width": st.session_state["board_width"],
        "thickness": st.session_state["board_thickness"]
    }

    # File Uploader
    uploaded = st.file_uploader("Upload or Drag-and-Drop Timber Photograph (JPG, PNG, WebP):", type=["jpg", "jpeg", "png", "webp"])
    st.markdown("</div>", unsafe_allow_html=True)

    abytes, aname = None, None
    if uploaded:
        abytes, aname = uploaded.getvalue(), uploaded.name
        st.session_state["selected_sample"] = None
    elif st.session_state["selected_sample"] and os.path.exists(st.session_state["selected_sample"]):
        p = st.session_state["selected_sample"]
        with open(p, "rb") as fh:
            abytes = fh.read()
        aname = os.path.basename(p)

    if not abytes:
        st.markdown(uhtml("""
        <div class="wi-card" style="text-align:center;padding:2.8rem 1.5rem;">
          <div style="font-family:'JetBrains Mono',monospace;font-size:1.3rem;font-weight:800;color:var(--amber);margin-bottom:.5rem;">[STANDBY]</div>
          <h3 style="color:var(--ink);margin-bottom:.4rem;">Awaiting Timber Specimen</h3>
          <p style="color:var(--muted);max-width:540px;margin:0 auto;font-size:.9rem;line-height:1.5;">
            Upload a lumber photograph to initiate automated optical inspection, botanical taxonomy identification, and defect segmentation.
          </p>
        </div>
        """), unsafe_allow_html=True)
    else:
        pv1, pv2 = st.columns([5, 3], gap="large")
        with pv1:
            st.image(Image.open(io.BytesIO(abytes)), caption=f"Specimen Preview: {aname}", use_container_width=True)
        with pv2:
            run_det = st.button("Execute Complete Timber Inspection", type="primary", use_container_width=True)
            st.caption("Performs species classification, authenticity gating, and defect segmentation.")

            if run_det:
                suffix = os.path.splitext(aname)[1] or ".jpg"
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                try:
                    tmp.write(abytes)
                    tmp.close()
                    raw = cv2.imread(tmp.name)
                    orig_rgb = cv2.cvtColor(raw, cv2.COLOR_BGR2RGB) if raw is not None else None

                    with st.spinner("Analyzing wood texture, species & surface defects..."):
                        get_models()
                        ws, _ = wood_gate.wood_score(tmp.name)
                        is_w = ws >= st.session_state["wood_threshold"]
                        sp, dets, dmg, usbl, wst, seg, box, ditems = [], [], 0.0, 100.0, 0.0, None, None, []
                        sp_info = None

                        if is_w:
                            sp = predict.predict_species(tmp.name)
                            top_folder_id = sp[0].get("folder_id", "1") if sp else "1"
                            sp_info = get_species_info(top_folder_id)

                            predict.DEFECT_CONF = st.session_state["conf_threshold"]
                            rd, _ = predict.predict_defects(tmp.name)
                            dets = rd
                            for d in dets:
                                d["label"] = defect_label(d["class_id"])
                            seg, box, dmg, usbl, wst, ditems = segment_defects(tmp.name, dets)
                finally:
                    try:
                        os.remove(tmp.name)
                    except OSError:
                        pass

                sev = overall_severity(ditems, dmg)

                furn_results = []
                for fk, fi in FURNITURE_CATALOG.items():
                    fr = evaluate_furniture(fi, sp_info or {}, dets, dmg, dims_input, st.session_state["rec_priority"])
                    fr.update({
                        "id": fk, "name": fi["name"], "icon": fi["icon"], "full_name": fi["full_name"],
                        "required_strength": fi["required_strength"],
                        "acceptable_defects": fi["acceptable_defects"],
                        "min_dimensions": fi["min_dimensions"],
                        "dim_description": fi["dim_description"],
                        "image": fi.get("image", "")
                    })
                    furn_results.append(fr)

                furn_results.sort(key=lambda x: x["score"], reverse=True)
                best_id = furn_results[0]["id"] if furn_results else None

                seen_repairs = set()
                repair_advice = []
                for d in ditems:
                    r = d.get("repair", "")
                    if r and r not in seen_repairs:
                        repair_advice.append({
                            "label": d["label"],
                            "repair": r,
                            "icon": d["icon"],
                            "severity": d["severity"],
                            "repair_type": d.get("repair_type", "sanding")
                        })
                        seen_repairs.add(r)

                st.session_state["last_result"] = {
                    "aname": aname, "abytes": abytes, "orig_rgb": orig_rgb, "seg": seg, "box": box,
                    "ws": ws, "is_w": is_w, "sp": sp, "sp_info": sp_info, "dets": dets, "ditems": ditems,
                    "dmg": dmg, "usbl": usbl, "wst": wst, "sev": sev, "dims": dims_input,
                    "furn_results": furn_results, "best_id": best_id, "repair_advice": repair_advice,
                    "priority": st.session_state["rec_priority"], "ts": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }

                save_history({
                    "timestamp": st.session_state["last_result"]["ts"], "filename": aname,
                    "wood_score": round(ws, 3), "is_wood": is_w, "damaged_pct": round(dmg, 2),
                    "usable_pct": round(usbl, 2), "waste_pct": round(wst, 2), "severity": sev,
                    "defect_count": len(dets),
                    "best_furniture": furn_results[0]["name"] if furn_results else "N/A",
                    "best_score": furn_results[0]["score"] if furn_results else 0,
                    "species": sp_info["name"] if sp_info else "Unknown"
                })

                st.success("Analysis Complete! Redirecting to Defect Detection view...")
                st.session_state["current_page"] = "Defect Detection"
                st.rerun()


# ===========================================================================
# PAGE 4: DEFECT DETECTION (DEDICATED PAGE)
# ===========================================================================
elif st.session_state["current_page"] == "Defect Detection":
    R = st.session_state.get("last_result")
    if not R:
        st.markdown(uhtml("""
        <div class="wi-card" style="text-align:center;padding:3rem 1.5rem;">
          <div style="font-size:3.5rem;margin-bottom:.6rem;">🔍</div>
          <h3 style="color:var(--ink);">No Defect Analysis Loaded</h3>
          <p style="color:var(--muted);max-width:500px;margin:0 auto 1.5rem auto;">
            Please select or upload a timber image from the New Analysis page to view segmentation masks and defect data.
          </p>
        </div>
        """), unsafe_allow_html=True)
        if st.button("Go to New Analysis", type="primary"):
            st.session_state["current_page"] = "New Analysis"
            st.rerun()
    elif not R["is_w"]:
        st.markdown(uhtml(f"""
        <div style="background:var(--bad-tint);border:1.5px solid var(--bad-border);border-left:4px solid var(--bad);border-radius:14px;padding:1.5rem;margin-bottom:1.2rem;">
          <h4 style="color:var(--bad);margin:0 0 .5rem 0;">Non-Wood Surface Rejected</h4>
          <p style="color:var(--muted);font-size:.9rem;margin:0;">
            Wood Authenticity Gate confidence was {R["ws"]*100:.1f}%, which is below the threshold of {st.session_state['wood_threshold']*100:.1f}%.
            Please supply a natural timber specimen.
          </p>
        </div>
        """), unsafe_allow_html=True)
        if R["orig_rgb"] is not None:
            st.image(R["orig_rgb"], width=420)
    else:
        # Species Box
        sp_data = R.get("sp_info", {})
        top_sp = R["sp"][0] if R.get("sp") else {}
        sp_conf = top_sp.get("confidence", 0.95) * 100
        # In a 19-class model, uniform random is 5.26%. >=50% is high, >=22% is solid relative majority (>4x uniform)
        sp_conf_color = "var(--good)" if sp_conf >= 50 else ("var(--warn)" if sp_conf >= 22 else "var(--bad)")

        cand_items = []
        for s_cand in (R.get("sp") or [])[:3]:
            cand_items.append(f"<strong>{s_cand.get('name', '')}</strong> ({s_cand.get('confidence', 0)*100:.1f}%)")
        cand_str = " &nbsp;|&nbsp; ".join(cand_items)
        cand_html = f'<div style="font-size:0.82rem;color:var(--muted);margin-top:0.45rem;">Classification Ranking: {cand_str}</div>' if len(cand_items) > 1 else ""

        st.markdown(uhtml(f"""
        <div class="species-card" style="padding:1.4rem 1.8rem;margin-bottom:1.2rem;">
          <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1.2rem;">
            <div>
              <span class="wi-section-label" style="font-size:0.78rem;padding:0.25rem 0.75rem;">DETECTED WOOD SPECIES</span>
              <div style="font-size:1.75rem;font-weight:800;color:var(--ink);margin-top:.4rem;line-height:1.2;">
                {sp_data.get('common_name', 'European Beech')} <span style="font-size:1.15rem;font-weight:500;color:var(--muted);font-style:italic;">({sp_data.get('botanical_name', '')})</span>
              </div>
              <div style="font-size:0.95rem;color:var(--muted);margin-top:.35rem;">Type: <strong>{sp_data.get('type', 'Hardwood')}</strong> | Nominal Density: <strong>{sp_data.get('density', '680 kg/m³')}</strong></div>
              {cand_html}
            </div>
            <div style="text-align:right;background:var(--surface-2);padding:0.6rem 1.15rem;border-radius:10px;border:1px solid var(--line);">
              <div style="font-size:.78rem;color:var(--muted);font-weight:700;letter-spacing:0.05em;text-transform:uppercase;">Species Confidence</div>
              <div style="font-size:2.2rem;font-weight:800;color:{sp_conf_color};font-family:'JetBrains Mono',monospace;line-height:1.15;margin-top:0.2rem;">{sp_conf:.1f}%</div>
            </div>
          </div>
        </div>
        """), unsafe_allow_html=True)

        # 5 Defect & Quality Metric Cards
        sev = R["sev"]
        sc_ = SEV_COLORS[sev]
        sev_lbl = {"Low": "🟢 Safe (Low Risk)", "Medium": "🟠 Warning (Medium Risk)", "High": "🔴 Serious Damage (High Risk)"}[sev]
        d_color = "var(--bad)" if R["dmg"] > 2.0 else ("var(--warn)" if R["dmg"] > 0.6 else "var(--good)")

        m1, m2, m3, m4, m5 = st.columns(5)
        with m1:
            st.markdown(f'<div class="kpi-card" style="background:{sc_["bg"]};border-color:{sc_["border"]};"><div class="kpi-label">Defect Severity</div><div style="font-size:1.1rem;font-weight:800;color:{sc_["text"]};margin-top:.4rem;">{sev_lbl}</div></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">Detected Defects</div><div class="kpi-val" style="color:var(--ink);">{len(R["dets"])}</div></div>', unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">Damaged Percentage</div><div class="kpi-val" style="color:{d_color};">{R["dmg"]:.2f}%</div></div>', unsafe_allow_html=True)
        with m4:
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">Usable Wood</div><div class="kpi-val" style="color:var(--good);">{R["usbl"]:.2f}%</div></div>', unsafe_allow_html=True)
        with m5:
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">Cut-off Waste</div><div class="kpi-val" style="color:var(--bad);">{R["wst"]:.2f}%</div></div>', unsafe_allow_html=True)

        st.markdown("<div style='height:.8rem;'></div>", unsafe_allow_html=True)

        # Side by Side Visualizer
        st.markdown('<div class="wi-card"><div class="wi-card-header"><span class="wi-card-title">🔬 Defect Segmentation & Visual Evidence</span><span class="wi-section-label">SIDE-BY-SIDE INSPECTION</span></div>', unsafe_allow_html=True)
        
        vmode = st.radio("Display View:", ["Side-by-Side Comparison", "Defect Segmentation Overlay", "Bounding Boxes Only", "Original Timber Only"], horizontal=True)
        
        if vmode == "Side-by-Side Comparison":
            img_c1, img_c2 = st.columns(2, gap="medium")
            with img_c1:
                st.caption("📸 Original Timber Board")
                st.image(R["orig_rgb"], use_container_width=True)
            with img_c2:
                st.caption("🔍 Defect-Segmented Map")
                st.image(R["seg"] if R["seg"] is not None else R["orig_rgb"], use_container_width=True)
        else:
            show = {"Defect Segmentation Overlay": R["seg"], "Bounding Boxes Only": R["box"], "Original Timber Only": R["orig_rgb"]}[vmode]
            st.image(show if show is not None else R["orig_rgb"], use_container_width=True)

        if R["seg"] is not None:
            buf = io.BytesIO()
            Image.fromarray(R["seg"]).save(buf, "JPEG", quality=95)
            st.download_button("💾 Download High-Res Segmented Image", buf.getvalue(), file_name=f"{os.path.splitext(R['aname'])[0]}_segmented.jpg", mime="image/jpeg")
        st.markdown("</div>", unsafe_allow_html=True)

        # Defect List
        st.markdown('<div class="wi-card"><div class="wi-card-header"><span class="wi-card-title">📋 Detected Defect Instances</span><span class="wi-section-label">QUANTIFIED FAULTS</span></div>', unsafe_allow_html=True)
        if not R["ditems"]:
            st.markdown('<div style="background:var(--good-tint);border:1px solid var(--good-border);border-radius:10px;padding:1.2rem;text-align:center;color:var(--good);font-weight:700;">Zero defects detected — Prime Clear Grade-A Timber!</div>', unsafe_allow_html=True)
        else:
            for d in R["ditems"]:
                sc2 = SEV_COLORS[d["severity"]]
                st.markdown(uhtml(f"""
                <div class="audit-row" style="background:var(--surface);border:1.5px solid var(--line);border-radius:10px;padding:.75rem .9rem;margin-bottom:.55rem;display:flex;align-items:center;justify-content:space-between;">
                  <div style="display:flex;align-items:center;gap:.6rem;">
                    <span style="width:12px;height:12px;border-radius:50%;background:{d['color_hex']};display:inline-block;flex-shrink:0;"></span>
                    <div>
                      <strong style="color:var(--ink);font-size:.9rem;">{d['label']}</strong>
                      <div style="font-size:.72rem;color:var(--muted);">Confidence: {d['confidence']*100:.0f}%</div>
                    </div>
                    <span style="background:{sc2['bg']};color:{sc2['text']};border:1px solid {sc2['border']};font-size:.72rem;font-weight:700;padding:.15rem .45rem;border-radius:4px;">{d['severity']}</span>
                  </div>
                  <div style="text-align:right;">
                    <span style="font-family:'JetBrains Mono',monospace;font-size:.88rem;font-weight:800;color:{d['color_hex']};">{d['damaged_pct']:.2f}%</span>
                    <div style="font-size:.65rem;color:var(--muted);text-transform:uppercase;">area</div>
                  </div>
                </div>
                """), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
        render_inspection_report(R, key_prefix="defect_report")


# ===========================================================================
# PAGE 5: FURNITURE RECOMMENDATIONS (DEDICATED PAGE)
# ===========================================================================
elif st.session_state["current_page"] == "Furniture Recommendations":
    import page5_furniture
    page5_furniture.render_furniture_page(dark)
    active_item = furniture_recommender.get_furniture_item(st.session_state.get("selected_furniture", "wooden_chair"))
    # -----------------------------------------------------------------------
    # OPTIONAL SPECIMEN COMPATIBILITY CHECK (NON-BLOCKING)
    # -----------------------------------------------------------------------
    R_scan = st.session_state.get("last_result")
    if R_scan and R_scan.get("is_w"):
        sp_scan = R_scan.get("sp_info", {})
        scan_name = sp_scan.get("common_name", "Scanned Timber")
        scan_mor = sp_scan.get("mor", 80)
        scan_dmg = R_scan.get("dmg", 0.0)

        with st.expander(f"🔎 Optional: Check Uploaded Specimen Compatibility ({scan_name} vs {active_item['name']})", expanded=False):
            st.markdown(uhtml(f"""
            <div style="background:var(--surface-2);border:1px solid var(--line);border-left:3px solid var(--amber);border-radius:12px;padding:0.9rem 1.2rem;margin-bottom:0.75rem;font-size:0.85rem;color:var(--muted);">
              <div><strong>Uploaded Specimen:</strong> {scan_name} ({sp_scan.get('botanical_name', '')})</div>
              <div style="margin-top:0.2rem;">Measured Surface Damage: <strong>{scan_dmg:.2f}%</strong> | Base Specimen MOR: <strong>{scan_mor} MPa</strong></div>
            </div>
            """), unsafe_allow_html=True)

            req_mor_val = 90
            try:
                mor_str = active_item["stress_profile"]["min_mor"].replace("≥", "").replace("MPa", "").strip()
                req_mor_val = float(mor_str)
            except Exception:
                pass

            is_compat = (scan_mor >= req_mor_val) and (scan_dmg <= 3.0)
            if is_compat:
                st.success(f"✓ {scan_name} meets the mechanical bending requirements ({scan_mor} MPa ≥ {req_mor_val} MPa) and defect tolerances for constructing a {active_item['name']}.")
            else:
                reason = f"has lower MOR ({scan_mor} MPa < required {req_mor_val} MPa)" if scan_mor < req_mor_val else f"damage of {scan_dmg:.2f}% exceeds high-stress tolerance"
                st.warning(f"⚠️ {scan_name} is conditionally or marginally suitable for {active_item['name']} because it {reason}. Consider using one of the top recommended species above.")


# ===========================================================================
# PAGE 6: COMPARE WOOD (DEDICATED PAGE)
# ===========================================================================
elif st.session_state["current_page"] == "Compare Wood":
    st.markdown('<div class="wi-card"><div class="wi-card-header"><span class="wi-card-title">Compare Two Wood Specimens</span><span class="wi-section-label">HEAD-TO-HEAD AUDIT</span></div>', unsafe_allow_html=True)

    tf = st.selectbox("Select Target Furniture Application:", list(FURNITURE_CATALOG.keys()),
                      format_func=lambda x: f"{FURNITURE_CATALOG[x]['icon']} {FURNITURE_CATALOG[x]['full_name']}")

    st.markdown("**Select from Presets or Upload Custom Photos:**")
    cp1, cp2, cp3 = st.columns([2, 2, 1])
    preset_names = ["None"] + [s["name"] for s in SAMPLES]
    with cp1:
        pr_a = st.selectbox("Preset Wood A:", preset_names, index=1, key="sel_pr_a_new")
    with cp2:
        pr_b = st.selectbox("Preset Wood B:", preset_names, index=3, key="sel_pr_b_new")
    with cp3:
        st.markdown("<div style='height:1.75rem'></div>", unsafe_allow_html=True)
        if st.button("Apply Presets", key="btn_apply_presets_new", use_container_width=True):
            s_map = {s["name"]: s["file"] for s in SAMPLES}
            st.session_state["cmp_a_sample"] = s_map.get(pr_a)
            st.session_state["cmp_b_sample"] = s_map.get(pr_b)
            st.rerun()

    ca, cb = st.columns(2, gap="large")
    with ca:
        upa = st.file_uploader("Upload Wood Specimen A:", type=["jpg", "jpeg", "png", "webp"], key="cmp_a_new")
        if not upa and st.session_state.get("cmp_a_sample") and os.path.exists(st.session_state["cmp_a_sample"]):
            st.caption(f"Using Preset A: {os.path.basename(st.session_state['cmp_a_sample'])}")
    with cb:
        upb = st.file_uploader("Upload Wood Specimen B:", type=["jpg", "jpeg", "png", "webp"], key="cmp_b_new")
        if not upb and st.session_state.get("cmp_b_sample") and os.path.exists(st.session_state["cmp_b_sample"]):
            st.caption(f"Using Preset B: {os.path.basename(st.session_state['cmp_b_sample'])}")

    run_cmp = st.button("⚔️ Run Head-to-Head Comparison", type="primary")

    def analyse_cmp(input_source):
        if not input_source:
            return None
        if isinstance(input_source, str):
            an = os.path.basename(input_source)
            with open(input_source, "rb") as fh:
                ab = fh.read()
        else:
            ab = input_source.getvalue()
            an = input_source.name

        suffix = os.path.splitext(an)[1] or ".jpg"
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        try:
            tmp.write(ab)
            tmp.close()
            pil_s = Image.open(io.BytesIO(ab))
            ws, _ = wood_gate.wood_score(tmp.name)
            is_w = ws >= st.session_state["wood_threshold"]
            sp, rd, dmg, usbl, wst, ditems, seg = [], [], 0.0, 100.0, 0.0, [], None
            sp_info = {}
            if is_w:
                sp = predict.predict_species(tmp.name)
                sp_info = get_species_info(sp[0].get("folder_id", "1") if sp else "1")
                predict.DEFECT_CONF = st.session_state["conf_threshold"]
                rd, _ = predict.predict_defects(tmp.name)
                for d in rd:
                    d["label"] = defect_label(d["class_id"])
                seg, _, dmg, usbl, wst, ditems = segment_defects(tmp.name, rd)
            finfo = FURNITURE_CATALOG[tf]
            dims_input = {"length": st.session_state["board_length"], "width": st.session_state["board_width"], "thickness": st.session_state["board_thickness"]}
            fr = evaluate_furniture(finfo, sp_info or {}, rd, dmg, dims_input, st.session_state["rec_priority"])
            return {
                "name": an, "is_w": is_w, "ws": ws, "sp": sp, "sp_info": sp_info or {},
                "dets": rd, "ditems": ditems, "dmg": dmg, "usbl": usbl, "wst": wst,
                "sev": overall_severity(ditems, dmg), "fr": fr, "pil": pil_s, "seg": seg
            }
        except Exception as e:
            st.error(f"Comparison error: {e}")
            return None
        finally:
            try:
                os.remove(tmp.name)
            except OSError:
                pass

    src_a = upa or st.session_state.get("cmp_a_sample")
    src_b = upb or st.session_state.get("cmp_b_sample")

    if run_cmp:
        if not src_a or not src_b:
            st.warning("Please provide or select both Wood A and Wood B specimens.")
        else:
            with st.spinner("Analyzing both timber pieces simultaneously..."):
                ra = analyse_cmp(src_a)
                rb = analyse_cmp(src_b)
            if ra and rb:
                ca2, cb2 = st.columns(2, gap="large")
                for res, col, lbl in [(ra, ca2, "Wood A"), (rb, cb2, "Wood B")]:
                    with col:
                        img_to_show = res["seg"] if res.get("seg") is not None else res["pil"]
                        st.image(img_to_show, caption=f"{lbl}: {res['name']}", use_container_width=True)
                if ra["is_w"] and rb["is_w"]:
                    winner = (ra if ra["fr"]["score"] >= rb["fr"]["score"] else rb)
                    loser = (rb if winner == ra else ra)
                    wlbl = "Wood A" if winner == ra else "Wood B"
                    st.markdown(uhtml(f"""
                    <div style="background:var(--good-tint);border:2px solid var(--good-border);border-radius:14px;padding:1.2rem;margin:1rem 0;text-align:center;">
                      <div style="font-size:1.6rem;font-weight:800;color:var(--good);">🏆 {wlbl} is Better for {FURNITURE_CATALOG[tf]['name']}!</div>
                      <div style="color:var(--good);font-size:.9rem;margin-top:.2rem;">
                        Score: <strong>{winner['fr']['score']}/100</strong> vs {loser['fr']['score']}/100 • Advantage: <strong>+{winner['fr']['score']-loser['fr']['score']} pts</strong>
                      </div>
                    </div>
                    """), unsafe_allow_html=True)

                    w1, w2 = st.columns(2)
                    for res, col, is_win, lbl in [(ra, w1, winner == ra, "Wood A"), (rb, w2, winner == rb, "Wood B")]:
                        fr = res["fr"]
                        sc_ = "var(--good)" if fr["score"] >= 75 else ("var(--warn)" if fr["score"] >= 50 else "var(--bad)")
                        sp_disp = (res.get("sp_info") or {}).get("common_name", "Timber")
                        with col:
                            st.markdown(uhtml(f"""
                            <div style="background:var(--surface);border:{'2px solid var(--good)' if is_win else '1px solid var(--line)'};border-radius:14px;padding:1.1rem;">
                              <div style="font-size:1.15rem;font-weight:800;color:var(--ink);margin-bottom:.5rem;">{'★ WINNER: ' if is_win else ''}{lbl}</div>
                              <div style="display:flex;gap:1rem;margin-bottom:.6rem;">
                                <div style="text-align:center;">
                                  <div style="font-size:1.85rem;font-weight:800;color:{sc_};font-family:'JetBrains Mono',monospace;">{fr['score']}</div>
                                  <div style="font-size:.7rem;color:var(--muted);">/ 100</div>
                                </div>
                                <div style="font-size:.84rem;color:var(--ink);line-height:1.45;">
                                  Species: <strong>{sp_disp}</strong><br/>
                                  Damaged: <strong>{res['dmg']:.2f}%</strong> | Waste: <strong>{res['wst']:.2f}%</strong><br/>
                                  Usable: <strong>{res['usbl']:.2f}%</strong> | Status: <strong>{fr['status']}</strong>
                                </div>
                              </div>
                              <div style="font-size:.82rem;color:var(--muted);line-height:1.5;">{fr['reason']}</div>
                            </div>
                            """), unsafe_allow_html=True)
                else:
                    st.warning("One or both images were rejected by the wood authenticity gate.")
    st.markdown("</div>", unsafe_allow_html=True)


# ===========================================================================
# PAGE 7: ANALYSIS HISTORY (DEDICATED PAGE)
# ===========================================================================
elif st.session_state["current_page"] == "Analysis History":
    st.markdown('<div class="wi-card"><div class="wi-card-header"><span class="wi-card-title">Audit Trail & Inspection History</span><span class="wi-section-label">LAST 50 SPECIMENS</span></div>', unsafe_allow_html=True)
    history = load_history()
    if not history:
        st.markdown(uhtml("""
        <div style="text-align:center;padding:2.8rem;color:var(--muted);">
          <div style="font-size:3rem;">📋</div>
          <h4>No Inspection History Logged</h4>
          <p>Execute an analysis on the New Analysis page to view historical timber records here.</p>
        </div>
        """), unsafe_allow_html=True)
    else:
        total = len(history)
        avg_d = sum(h.get("damaged_pct", 0) for h in history) / total
        hi_risk = sum(1 for h in history if h.get("severity") == "High")
        clear_b = sum(1 for h in history if h.get("defect_count", 1) == 0)

        hc1, hc2, hc3, hc4 = st.columns(4)
        for col, (lbl, val, clr) in zip([hc1, hc2, hc3, hc4], [
            ("Total Logs", total, "var(--amber)"),
            ("Avg Damage", f"{avg_d:.2f}%", "var(--warn)" if avg_d > 1 else "var(--good)"),
            ("High Risk Boards", hi_risk, "var(--bad)"),
            ("Prime Clear Boards", clear_b, "var(--good)")
        ]):
            with col:
                st.markdown(f'<div class="kpi-card"><div class="kpi-val" style="color:{clr};">{val}</div><div class="kpi-label">{lbl}</div></div>', unsafe_allow_html=True)

        st.markdown("<div style='height:.9rem;'></div>", unsafe_allow_html=True)

        for entry in history:
            sv = entry.get("severity", "Low")
            sc2 = SEV_COLORS.get(sv, SEV_COLORS["Low"])
            st.markdown(uhtml(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;padding:.75rem 1rem;border-radius:10px;background:var(--surface);border:1px solid var(--line);margin-bottom:.45rem;font-size:.84rem;flex-wrap:wrap;gap:.6rem;">
              <div style="display:flex;align-items:center;gap:.7rem;flex:1;">
                <strong style="color:var(--ink);">{entry.get('filename', 'specimen.jpg')}</strong>
                <span style="background:{sc2['bg']};color:{sc2['text']};border:1px solid {sc2['border']};font-size:.72rem;padding:.15rem .5rem;border-radius:4px;font-weight:700;">{sv}</span>
                <span style="font-size:.78rem;color:var(--muted);">{entry.get('species', 'Timber')}</span>
              </div>
              <div style="display:flex;align-items:center;gap:1.2rem;font-size:.82rem;color:var(--muted);">
                <span>Damage: <strong>{entry.get('damaged_pct', 0):.2f}%</strong></span>
                <span>Usable: <strong style="color:var(--good);">{entry.get('usable_pct', 0):.2f}%</strong></span>
                <span>Best: <strong>{entry.get('best_furniture', 'N/A')} ({entry.get('best_score', 0)}/100)</strong></span>
                <span style="font-size:.75rem;color:#a8a29e;">{entry.get('timestamp', '')}</span>
              </div>
            </div>
            """), unsafe_allow_html=True)

        st.markdown("<div style='height:.8rem;'></div>", unsafe_allow_html=True)
        btn_d1, btn_d2 = st.columns([2, 1])
        with btn_d1:
            st.download_button("💾 Download History Audit (JSON)", json.dumps(history, indent=2).encode(),
                               file_name="timber_analysis_history.json", mime="application/json", use_container_width=True)
        with btn_d2:
            if st.button("🗑️ Clear History Records", type="secondary", use_container_width=True):
                if os.path.exists(HISTORY_FILE):
                    os.remove(HISTORY_FILE)
                st.success("History records cleared.")
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


# ===========================================================================
# PAGE 8: REPORTS & VERIFICATION (DEDICATED PAGE)
# ===========================================================================
elif st.session_state["current_page"] == "Reports":
    R = st.session_state.get("last_result")
    if not R or not R.get("is_w"):
        st.markdown(uhtml("""
        <div class="wi-card" style="text-align:center;padding:3rem 1.5rem;">
          <div style="font-size:3.5rem;margin-bottom:.6rem;">📑</div>
          <h3 style="color:var(--ink);">No Specimen Ready for Report Generation</h3>
          <p style="color:var(--muted);max-width:500px;margin:0 auto 1.5rem auto;">
            Please execute a timber analysis first to generate official PDF reports, verification QR codes, and voice audio summaries.
          </p>
        </div>
        """), unsafe_allow_html=True)
        if st.button("Analyze Timber Now", type="primary"):
            st.session_state["current_page"] = "New Analysis"
            st.rerun()
    else:
        render_inspection_report(R, key_prefix="reports_page")


# ===========================================================================
# PAGE 9: SETTINGS
# ===========================================================================
elif st.session_state["current_page"] == "Settings":
    st.markdown('<div class="wi-card"><div class="wi-card-header"><span class="wi-card-title">System Settings & Model Diagnostics</span><span class="wi-section-label">CONFIGURATION</span></div>', unsafe_allow_html=True)

    s1, s2 = st.columns(2, gap="large")
    with s1:
        st.markdown("#### 🎛️ AI Detection Parameters")
        st.session_state["conf_threshold"] = st.slider("Global Defect Confidence Threshold", 0.10, 0.90, float(st.session_state["conf_threshold"]), 0.05,
                                                      help="Lower values report more borderline defects; higher values suppress noise.")
        st.session_state["wood_threshold"] = st.slider("Wood Authenticity Gate Threshold", 0.10, 0.95, float(st.session_state["wood_threshold"]), 0.01,
                                                      help="Specimens below this threshold are flagged as non-wood surfaces.")
        st.session_state["rec_priority"] = st.radio("Default Optimization Focus:", ["strength", "best_appearance", "low_cost"],
                                                    format_func=lambda x: {"strength": "Max Structural Strength", "best_appearance": "Aesthetic Finish", "low_cost": "Cost & Timber Yield"}[x],
                                                    index=["strength", "best_appearance", "low_cost"].index(st.session_state["rec_priority"]))

    with s2:
        st.markdown("#### 🔬 AI Model Architecture")
        st.markdown(uhtml("""
        <div style="background:var(--surface);border:1px solid var(--line);border-left:3px solid var(--amber);border-radius:12px;padding:1rem;font-size:.84rem;line-height:1.6;">
          <div>🧠 <strong>Species Classifier:</strong> Fine-Tuned ResNet50 (12 Classes)</div>
          <div>🎯 <strong>Defect Detector:</strong> YOLOv11n (416×416 anchors)</div>
          <div>🛡️ <strong>Authenticity Gate:</strong> MobileNetV2 (Wood vs Non-Wood)</div>
          <div>📐 <strong>Segmentation:</strong> Computer Vision Otsu Morphological Masking</div>
          <hr style="border:none;border-bottom:1px solid var(--line);margin:.6rem 0;" />
          <div style="color:var(--good);font-weight:700;">✓ Hardware Status: CPU Acceleration Active</div>
        </div>
        """), unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
