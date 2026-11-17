"""Script to enrich furniture_data.py with carpentry cut lists, volume metrics,
joinery difficulty ratings, and orthographic specs for all 31 items.
"""
import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

import furniture_data

# Blueprint dimensions, cut lists, and joinery profiles by category
CATEGORY_PROFILES = {
    "Seating & Chairs": {
        "dims": {"width_cm": 46, "depth_cm": 48, "height_cm": 86, "seat_height_cm": 45},
        "cut_list": [
            {"part": "Front Legs (2x)", "count": 2, "thickness_mm": 45, "width_mm": 45, "length_mm": 450, "board_feet": 0.77, "cubic_meters": 0.0018},
            {"part": "Rear Splayed Legs (2x)", "count": 2, "thickness_mm": 45, "width_mm": 80, "length_mm": 860, "board_feet": 2.65, "cubic_meters": 0.0062},
            {"part": "Side Seat Rails (2x)", "count": 2, "thickness_mm": 25, "width_mm": 70, "length_mm": 400, "board_feet": 0.59, "cubic_meters": 0.0014},
            {"part": "Front/Rear Apron Rails (2x)", "count": 2, "thickness_mm": 25, "width_mm": 70, "length_mm": 420, "board_feet": 0.62, "cubic_meters": 0.0015},
            {"part": "Contoured Crest & Back Slats", "count": 3, "thickness_mm": 20, "width_mm": 60, "length_mm": 400, "board_feet": 0.61, "cubic_meters": 0.0014},
            {"part": "Solid Wood Sculpted Seat Pan", "count": 1, "thickness_mm": 32, "width_mm": 440, "length_mm": 440, "board_feet": 2.62, "cubic_meters": 0.0062}
        ],
        "total_board_feet": 7.86,
        "total_cubic_meters": 0.0185,
        "cost_tiers": {
            "tier1": "₹3,200 – ₹4,800",
            "tier2": "₹5,000 – ₹7,500",
            "tier3": "₹8,000 – ₹11,500",
            "tier4": "₹12,000 – ₹17,000",
            "tier5": "₹18,000 – ₹26,000"
        },
        "diagram_type": "chair_ortho",
        "joints": [
            {"joint": "Integral Mortise & Tenon", "location": "Apron to Rear Splayed Legs", "why": "Withstands continuous dynamic racking and backward lever stress without loosening.", "difficulty": 4, "tools": ["Mortiser / Chisel", "Tenon Saw", "Marking Gauge"], "glue": "Type II Cross-Linking PVA or Epoxy", "finish_tip": "Apply end-grain sealer before assembly to avoid glue starvation."},
            {"joint": "Reinforced Hardwood Corner Blocks", "location": "Inner Seat Frame Corners", "why": "Traingulates perimeter frame, neutralizing side-to-side shear forces.", "difficulty": 2, "tools": ["Miter Saw", "Countersink Drill"], "glue": "Thixotropic PVA + Screws", "finish_tip": "Pre-drill 3.5mm pilot holes to prevent splitting in dense hardwoods."}
        ]
    },
    "Tables & Desks": {
        "dims": {"width_cm": 150, "depth_cm": 85, "height_cm": 76, "seat_height_cm": None},
        "cut_list": [
            {"part": "Bookmatched Top Planks (4x)", "count": 4, "thickness_mm": 35, "width_mm": 220, "length_mm": 1520, "board_feet": 19.8, "cubic_meters": 0.0468},
            {"part": "Turned / Tapered Table Legs (4x)", "count": 4, "thickness_mm": 75, "width_mm": 75, "length_mm": 730, "board_feet": 11.2, "cubic_meters": 0.0264},
            {"part": "Longitudinal Perimeter Aprons (2x)", "count": 2, "thickness_mm": 25, "width_mm": 95, "length_mm": 1360, "board_feet": 4.5, "cubic_meters": 0.0107},
            {"part": "Transverse End Aprons (2x)", "count": 2, "thickness_mm": 25, "width_mm": 95, "length_mm": 710, "board_feet": 2.4, "cubic_meters": 0.0056},
            {"part": "Slotted Expansion Cleats (Z-fasteners)", "count": 8, "thickness_mm": 20, "width_mm": 40, "length_mm": 80, "board_feet": 0.4, "cubic_meters": 0.0009}
        ],
        "total_board_feet": 38.3,
        "total_cubic_meters": 0.0904,
        "cost_tiers": {
            "tier1": "₹12,000 – ₹18,000",
            "tier2": "₹19,000 – ₹28,000",
            "tier3": "₹30,000 – ₹45,000",
            "tier4": "₹48,000 – ₹68,000",
            "tier5": "₹75,000 – ₹110,000"
        },
        "diagram_type": "table_ortho",
        "joints": [
            {"joint": "Drawbored Mortise & Tenon", "location": "Apron to Leg Haunches", "why": "Drawbore dowel locks shoulder tight against leg without relying solely on glue longevity.", "difficulty": 4, "tools": ["Drill Press", "Drawbore Pins", "Tenon Saw"], "glue": "Liquid Hide Glue or Polyurethane", "finish_tip": "Offset peg hole by 2.5mm toward tenon shoulder for maximum clamping tension."},
            {"joint": "Slotted Figure-8 / Z-Fasteners", "location": "Table Top to Apron Frame", "why": "Permits seasonal cross-grain expansion and contraction without splitting solid tabletop.", "difficulty": 2, "tools": ["Biscuit Joiner / Router", "Screwdriver"], "glue": "None (Mechanical floating fastener)", "finish_tip": "Never glue tabletop directly to aprons."}
        ]
    },
    "Beds & Bedroom": {
        "dims": {"width_cm": 188, "depth_cm": 205, "height_cm": 105, "seat_height_cm": 42},
        "cut_list": [
            {"part": "Headboard Solid Posts (2x)", "count": 2, "thickness_mm": 80, "width_mm": 80, "length_mm": 1050, "board_feet": 9.2, "cubic_meters": 0.0217},
            {"part": "Footboard Posts (2x)", "count": 2, "thickness_mm": 80, "width_mm": 80, "length_mm": 520, "board_feet": 4.6, "cubic_meters": 0.0108},
            {"part": "Load-Bearing Side Bed Rails (2x)", "count": 2, "thickness_mm": 35, "width_mm": 160, "length_mm": 2000, "board_feet": 15.8, "cubic_meters": 0.0373},
            {"part": "Headboard Floating Infill Panel", "count": 1, "thickness_mm": 22, "width_mm": 600, "length_mm": 1750, "board_feet": 9.8, "cubic_meters": 0.0231},
            {"part": "Solid Hardwood Foundation Slats (14x)", "count": 14, "thickness_mm": 20, "width_mm": 70, "length_mm": 1820, "board_feet": 14.5, "cubic_meters": 0.0342}
        ],
        "total_board_feet": 53.9,
        "total_cubic_meters": 0.1271,
        "cost_tiers": {
            "tier1": "₹16,000 – ₹24,000",
            "tier2": "₹26,000 – ₹38,000",
            "tier3": "₹40,000 – ₹60,000",
            "tier4": "₹65,000 – ₹95,000",
            "tier5": "₹100,000 – ₹155,000"
        },
        "diagram_type": "bed_ortho",
        "joints": [
            {"joint": "Demountable Steel Bed-Bolt Knockdown Joinery", "location": "Side Rails to Corner Posts", "why": "Enables rapid assembly/disassembly while sustaining massive torsional load without creaking.", "difficulty": 3, "tools": ["Forstner Bit", "Wrench", "Mortise Chisel"], "glue": "None (Bed bolt hardware)", "finish_tip": "Wax bolt threads to ensure silent operation over decades."},
            {"joint": "Haunched Blind Mortise & Tenon", "location": "Headboard Rails to Posts", "why": "Concealed haunch prevents twist along top edges under headboard flexural load.", "difficulty": 4, "tools": ["Router", "Tenon Saw", "Corner Chisel"], "glue": "Type I Waterproof PVA", "finish_tip": "Keep tenon thickness to 1/3 of post thickness for optimal shear balance."}
        ]
    },
    "Storage & Shelves": {
        "dims": {"width_cm": 110, "depth_cm": 55, "height_cm": 190, "seat_height_cm": None},
        "cut_list": [
            {"part": "Carcass Side Panels (2x)", "count": 2, "thickness_mm": 22, "width_mm": 520, "length_mm": 1880, "board_feet": 17.5, "cubic_meters": 0.0413},
            {"part": "Top & Bottom Fixed Shelves (2x)", "count": 2, "thickness_mm": 22, "width_mm": 510, "length_mm": 1050, "board_feet": 9.8, "cubic_meters": 0.0231},
            {"part": "Adjustable Heavy-Duty Shelves (3x)", "count": 3, "thickness_mm": 22, "width_mm": 490, "length_mm": 1045, "board_feet": 14.2, "cubic_meters": 0.0335},
            {"part": "Stile & Rail Shaker Doors (2x)", "count": 2, "thickness_mm": 22, "width_mm": 520, "length_mm": 1780, "board_feet": 16.6, "cubic_meters": 0.0392},
            {"part": "Shiplapped Solid Backing Slats", "count": 10, "thickness_mm": 12, "width_mm": 100, "length_mm": 1850, "board_feet": 8.9, "cubic_meters": 0.0210}
        ],
        "total_board_feet": 67.0,
        "total_cubic_meters": 0.1581,
        "cost_tiers": {
            "tier1": "₹22,000 – ₹32,000",
            "tier2": "₹35,000 – ₹52,000",
            "tier3": "₹55,000 – ₹82,000",
            "tier4": "₹88,000 – ₹128,000",
            "tier5": "₹135,000 – ₹210,000"
        },
        "diagram_type": "cabinet_ortho",
        "joints": [
            {"joint": "Stopped Housing Dado with Rebate", "location": "Fixed Carcass Shelves to Sides", "why": "Stops 15mm from front edge to hide end-grain while carrying 90kg shelf loads.", "difficulty": 3, "tools": ["Router", "Straight Edge", "Chisel"], "glue": "Thixotropic Woodworkers PVA", "finish_tip": "Cut stopped dado depth to exactly 1/3 panel thickness (7mm)."},
            {"joint": "Half-Lap & Cope-and-Stick Joinery", "location": "Door Stile and Rail Frames", "why": "Enables floating tongue-and-groove center panels that expand without warping cabinet doors.", "difficulty": 4, "tools": ["Shaper / Router Table", "Coping Bit"], "glue": "PVA at frame corners only", "finish_tip": "Never glue the central panel into the frame grooves."}
        ]
    },
    "Architectural & Frames": {
        "dims": {"width_cm": 95, "depth_cm": 12, "height_cm": 210, "seat_height_cm": None},
        "cut_list": [
            {"part": "Exterior Vertical Jamb Stiles (2x)", "count": 2, "thickness_mm": 50, "width_mm": 115, "length_mm": 2150, "board_feet": 10.4, "cubic_meters": 0.0245},
            {"part": "Header Jamb Transverse Rail", "count": 1, "thickness_mm": 50, "width_mm": 115, "length_mm": 1050, "board_feet": 2.5, "cubic_meters": 0.0059},
            {"part": "Hardwood Weather Sill / Threshold", "count": 1, "thickness_mm": 45, "width_mm": 140, "length_mm": 1050, "board_feet": 3.1, "cubic_meters": 0.0073},
            {"part": "Architectural Architrave Casing Trim", "count": 5, "thickness_mm": 18, "width_mm": 75, "length_mm": 2200, "board_feet": 6.8, "cubic_meters": 0.0160}
        ],
        "total_board_feet": 22.8,
        "total_cubic_meters": 0.0537,
        "cost_tiers": {
            "tier1": "₹8,500 – ₹13,000",
            "tier2": "₹14,000 – ₹21,000",
            "tier3": "₹22,000 – ₹34,000",
            "tier4": "₹36,000 – ₹54,000",
            "tier5": "₹58,000 – ₹88,000"
        },
        "diagram_type": "frame_ortho",
        "joints": [
            {"joint": "Housed Lap & Mortise Joint", "location": "Header to Side Jamb Corners", "why": "Resists door impact slam shock while providing water-shedding exterior weather barrier.", "difficulty": 4, "tools": ["Circular Saw", "Chisel", "Clamp"], "glue": "Polyurethane (Gorilla) or Resorcinol", "finish_tip": "Coat mating end-grain with epoxy primer before exterior assembly."},
            {"joint": "Rebated Weatherstop Seal Rebate", "location": "Inner Jamb Perimeters", "why": "Continuous 12x15mm rebate houses silicone acoustic and weather draft gasket.", "difficulty": 2, "tools": ["Rebate Plane / Spindle"], "glue": "None (Mechanical seal)", "finish_tip": "Apply marine-grade teak oil or UV spar varnish."}
        ]
    }
}

updated_items = []
for item in furniture_data.FURNITURE_DATA:
    cat = item["category"]
    prof = CATEGORY_PROFILES.get(cat, CATEGORY_PROFILES["Seating & Chairs"])
    
    entry = dict(item)
    entry["dimensions"] = prof["dims"]
    entry["cutList"] = prof["cut_list"]
    entry["totalBoardFeet"] = prof["total_board_feet"]
    entry["totalCubicMeters"] = prof["total_cubic_meters"]
    entry["costTiers"] = prof["cost_tiers"]
    entry["diagramType"] = prof["diagram_type"]
    entry["joineryBreakdown"] = prof["joints"]
    entry["typicalJoinery"] = prof["joints"][0]["joint"]
    
    updated_items.append(entry)

print(f"Enriched all {len(updated_items)} furniture pieces.")

# Export to furniture.data.json
out_json = os.path.join(BASE_DIR, "furniture.data.json")
with open(out_json, "w", encoding="utf-8") as f:
    json.dump(updated_items, f, indent=2)

print("Updated furniture.data.json successfully!")

