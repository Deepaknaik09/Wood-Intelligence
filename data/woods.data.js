/**
 * Commercial Timbers Database (29 Precision Species).
 * Scientific properties audited from USDA Wood Handbook (FPL-GTR-190) and FRI Dehradun (IS 399).
 */
(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        define([], factory);
    } else if (typeof module === 'object' && module.exports) {
        module.exports = factory();
    } else {
        root.WOODS_DATABASE = factory();
        root.WOODS_BY_ID = {};
        root.WOODS_DATABASE.forEach(function (w) {
            root.WOODS_BY_ID[w.id] = w;
            var kebab = w.id.replace(/_/g, '-');
            root.WOODS_BY_ID[kebab] = w;
        });
        // Backward compatibility
        root.WOODS_BY_ID['padauk'] = root.WOODS_BY_ID['african_padauk'];
    }
}(typeof self !== 'undefined' ? self : this, function () {
    return [
  {
    "id": "teak",
    "name": "Teak",
    "scientificName": "Tectona grandis",
    "density": 655,
    "mor": 97.1,
    "hardness": 4740,
    "shrinkage": {
      "radial": 2.6,
      "tangential": 5.3,
      "volumetric": 7.2,
      "stability_score": 9.6
    },
    "durability": 9.8,
    "workability": 8.5,
    "finishQuality": 9.2,
    "weightClass": "Medium",
    "costTier": 5,
    "availabilityInIndia": 8.5,
    "sustainability": 7.2,
    "outdoorSuitability": 9.8,
    "bestUses": [
      "Dining tables",
      "Exterior doors",
      "Executive desks",
      "Outdoor loungers",
      "Cabinetry",
      "Marine joinery"
    ],
    "joineryTip": "High natural silica content dulls standard steel cutter edges; use carbide-tipped tooling and wipe surface oils with acetone before PVA glue-up.",
    "source": "USDA Wood Handbook (FPL-GTR-190) & Forest Research Institute (FRI) Dehradun (IS 399:1963)",
    "hardness_lbf": 1066,
    "designStyles": [
      "Mid-Century Modern",
      "Scandinavian",
      "Luxury Outdoor",
      "Contemporary Indian"
    ],
    "property_sources": {
      "density": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & Forest Research Institute (FRI) Dehradun (IS 399:1963)",
        "approximate": false
      },
      "mor": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & Forest Research Institute (FRI) Dehradun (IS 399:1963)",
        "approximate": false
      },
      "hardness": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & Forest Research Institute (FRI) Dehradun (IS 399:1963)",
        "approximate": false
      },
      "shrinkage": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & Forest Research Institute (FRI) Dehradun (IS 399:1963)",
        "approximate": false
      },
      "durability": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & Forest Research Institute (FRI) Dehradun (IS 399:1963)",
        "approximate": false
      }
    }
  },
  {
    "id": "sal",
    "name": "Sal",
    "scientificName": "Shorea robusta",
    "density": 880,
    "mor": 127.0,
    "hardness": 8900,
    "shrinkage": {
      "radial": 4.4,
      "tangential": 8.8,
      "volumetric": 14.1,
      "stability_score": 6.2
    },
    "durability": 9.5,
    "workability": 5.5,
    "finishQuality": 7.0,
    "weightClass": "Very Heavy",
    "costTier": 3,
    "availabilityInIndia": 9.5,
    "sustainability": 7.0,
    "outdoorSuitability": 9.2,
    "bestUses": [
      "Heavy structural frames",
      "Bunk beds",
      "Beams",
      "Exterior door frames",
      "Heavy benches"
    ],
    "joineryTip": "Dense interlocked fibers split easily when dry; always pre-drill screw clearance holes and use heavy mortise-and-tenons with mechanical through-bolts.",
    "source": "Forest Research Institute (FRI) Dehradun (IS 399:1963) & Indian Woods Vol. II",
    "hardness_lbf": 2001,
    "designStyles": [
      "Industrial Rustic",
      "Heavy Architectural",
      "Heritage Structural"
    ],
    "property_sources": {
      "density": {
        "source": "Forest Research Institute (FRI) Dehradun (IS 399:1963) & Indian Woods Vol. II",
        "approximate": false
      },
      "mor": {
        "source": "Forest Research Institute (FRI) Dehradun (IS 399:1963) & Indian Woods Vol. II",
        "approximate": false
      },
      "hardness": {
        "source": "Forest Research Institute (FRI) Dehradun (IS 399:1963) & Indian Woods Vol. II",
        "approximate": false
      },
      "shrinkage": {
        "source": "Forest Research Institute (FRI) Dehradun (IS 399:1963) & Indian Woods Vol. II",
        "approximate": false
      },
      "durability": {
        "source": "Forest Research Institute (FRI) Dehradun (IS 399:1963) & Indian Woods Vol. II",
        "approximate": false
      }
    }
  },
  {
    "id": "sheesham",
    "name": "Indian Rosewood (Sheesham)",
    "scientificName": "Dalbergia sissoo",
    "density": 770,
    "mor": 104.0,
    "hardness": 7490,
    "shrinkage": {
      "radial": 2.9,
      "tangential": 5.4,
      "volumetric": 8.8,
      "stability_score": 8.8
    },
    "durability": 8.8,
    "workability": 7.8,
    "finishQuality": 9.5,
    "weightClass": "Heavy",
    "costTier": 4,
    "availabilityInIndia": 9.0,
    "sustainability": 7.5,
    "outdoorSuitability": 7.5,
    "bestUses": [
      "Dining tables",
      "Carved beds",
      "Wardrobes",
      "Cabinet credenzas",
      "Musical instruments"
    ],
    "joineryTip": "Responds exceptionally well to mortise-and-tenon and dovetail joinery; sand to 320-grit for mirror-like wax polish finishes.",
    "source": "Forest Research Institute (FRI) Dehradun (IS 399:1963) & The Wood Database",
    "hardness_lbf": 1684,
    "designStyles": [
      "Traditional Indian",
      "Colonial Classic",
      "Rustic Modern"
    ],
    "property_sources": {
      "density": {
        "source": "Forest Research Institute (FRI) Dehradun (IS 399:1963) & The Wood Database",
        "approximate": false
      },
      "mor": {
        "source": "Forest Research Institute (FRI) Dehradun (IS 399:1963) & The Wood Database",
        "approximate": false
      },
      "hardness": {
        "source": "Forest Research Institute (FRI) Dehradun (IS 399:1963) & The Wood Database",
        "approximate": false
      },
      "shrinkage": {
        "source": "Forest Research Institute (FRI) Dehradun (IS 399:1963) & The Wood Database",
        "approximate": false
      },
      "durability": {
        "source": "Forest Research Institute (FRI) Dehradun (IS 399:1963) & The Wood Database",
        "approximate": false
      }
    }
  },
  {
    "id": "mahogany",
    "name": "Honduran Mahogany",
    "scientificName": "Swietenia macrophylla",
    "density": 590,
    "mor": 79.4,
    "hardness": 4020,
    "shrinkage": {
      "radial": 3.0,
      "tangential": 4.1,
      "volumetric": 7.8,
      "stability_score": 9.4
    },
    "durability": 8.2,
    "workability": 9.5,
    "finishQuality": 9.8,
    "weightClass": "Medium",
    "costTier": 4,
    "availabilityInIndia": 6.5,
    "sustainability": 6.0,
    "outdoorSuitability": 7.0,
    "bestUses": [
      "Executive desks",
      "Wardrobes",
      "Musical cabinets",
      "Fine chairs",
      "Console tables"
    ],
    "joineryTip": "Machines cleanly in all grain directions; the international benchmark for hand-cut dovetails and intricate carved architectural moldings.",
    "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
    "hardness_lbf": 904,
    "designStyles": [
      "Georgian / Classic",
      "Executive Luxury",
      "Formal Dining"
    ],
    "property_sources": {
      "density": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      },
      "mor": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      },
      "hardness": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      },
      "shrinkage": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      },
      "durability": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      }
    }
  },
  {
    "id": "white_oak",
    "name": "White Oak",
    "scientificName": "Quercus alba",
    "density": 755,
    "mor": 105.0,
    "hardness": 6000,
    "shrinkage": {
      "radial": 5.6,
      "tangential": 10.5,
      "volumetric": 16.3,
      "stability_score": 7.2
    },
    "durability": 8.5,
    "workability": 7.8,
    "finishQuality": 9.0,
    "weightClass": "Heavy",
    "costTier": 4,
    "availabilityInIndia": 6.0,
    "sustainability": 8.0,
    "outdoorSuitability": 8.5,
    "bestUses": [
      "Dining sets",
      "Chairs",
      "Outdoor furniture",
      "Bookshelves",
      "Architectural doors"
    ],
    "joineryTip": "High tannic acid content reacts with steel; strictly use brass or stainless steel fasteners to avoid permanent black stain streaks.",
    "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
    "hardness_lbf": 1349,
    "designStyles": [
      "Japandi",
      "Mission / Craftsman",
      "Modern Minimal",
      "Nordic"
    ],
    "property_sources": {
      "density": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      },
      "mor": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      },
      "hardness": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      },
      "shrinkage": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      },
      "durability": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      }
    }
  },
  {
    "id": "hard_maple",
    "name": "Hard Maple (Sugar Maple)",
    "scientificName": "Acer saccharum",
    "density": 705,
    "mor": 109.0,
    "hardness": 6450,
    "shrinkage": {
      "radial": 4.8,
      "tangential": 9.9,
      "volumetric": 14.7,
      "stability_score": 7.0
    },
    "durability": 4.5,
    "workability": 7.5,
    "finishQuality": 9.2,
    "weightClass": "Heavy",
    "costTier": 3,
    "availabilityInIndia": 6.0,
    "sustainability": 8.5,
    "outdoorSuitability": 3.0,
    "bestUses": [
      "Study tables",
      "Children cots",
      "Cutting boards",
      "Drawer runners",
      "Stools"
    ],
    "joineryTip": "Diffuse-porous smooth structure takes PVA glue with immense shear bond strength; pre-bore screw holes to prevent snapping shank screws.",
    "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
    "hardness_lbf": 1450,
    "designStyles": [
      "Modern Minimal",
      "Scandinavian Clean",
      "Contemporary Studio"
    ],
    "property_sources": {
      "density": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      },
      "mor": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      },
      "hardness": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      },
      "shrinkage": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      },
      "durability": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      }
    }
  },
  {
    "id": "black_walnut",
    "name": "Black Walnut",
    "scientificName": "Juglans nigra",
    "density": 610,
    "mor": 101.0,
    "hardness": 4490,
    "shrinkage": {
      "radial": 5.5,
      "tangential": 7.8,
      "volumetric": 12.8,
      "stability_score": 8.8
    },
    "durability": 8.0,
    "workability": 9.2,
    "finishQuality": 9.9,
    "weightClass": "Medium",
    "costTier": 5,
    "availabilityInIndia": 6.5,
    "sustainability": 7.8,
    "outdoorSuitability": 6.5,
    "bestUses": [
      "Executive desks",
      "Coffee tables",
      "Sculpted armchairs",
      "Credenzas",
      "Mirror frames"
    ],
    "joineryTip": "Steam-bends easily; open grain drinks Danish and Hardwax oils, producing unrivaled rich chocolate-brown optical depth.",
    "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
    "hardness_lbf": 1009,
    "designStyles": [
      "Mid-Century Modern",
      "High-End Luxury",
      "Sculptural Contemporary"
    ],
    "property_sources": {
      "density": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      },
      "mor": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      },
      "hardness": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      },
      "shrinkage": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      },
      "durability": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      }
    }
  },
  {
    "id": "white_ash",
    "name": "White Ash",
    "scientificName": "Fraxinus americana",
    "density": 675,
    "mor": 103.0,
    "hardness": 5870,
    "shrinkage": {
      "radial": 4.9,
      "tangential": 7.8,
      "volumetric": 13.3,
      "stability_score": 8.0
    },
    "durability": 4.5,
    "workability": 8.5,
    "finishQuality": 8.8,
    "weightClass": "Medium-Heavy",
    "costTier": 3,
    "availabilityInIndia": 6.5,
    "sustainability": 7.0,
    "outdoorSuitability": 3.5,
    "bestUses": [
      "Chairs",
      "Stools",
      "Benches",
      "Steam-bent furniture",
      "Bookshelves"
    ],
    "joineryTip": "World's supreme steam-bending hardwood with unmatched impact shock resistance; ideal for mortised and tenoned chair frames.",
    "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
    "hardness_lbf": 1320,
    "designStyles": [
      "Scandinavian",
      "Bentwood Modern",
      "Athletic Studio"
    ],
    "property_sources": {
      "density": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      },
      "mor": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      },
      "hardness": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      },
      "shrinkage": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      },
      "durability": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      }
    }
  },
  {
    "id": "beech",
    "name": "European Beech",
    "scientificName": "Fagus sylvatica",
    "density": 710,
    "mor": 110.0,
    "hardness": 5800,
    "shrinkage": {
      "radial": 5.8,
      "tangential": 11.8,
      "volumetric": 17.9,
      "stability_score": 6.0
    },
    "durability": 4.0,
    "workability": 8.8,
    "finishQuality": 8.8,
    "weightClass": "Heavy",
    "costTier": 2,
    "availabilityInIndia": 7.5,
    "sustainability": 8.8,
    "outdoorSuitability": 3.0,
    "bestUses": [
      "Bentwood chairs",
      "Dining chairs",
      "Children furniture",
      "Stools",
      "Drawer sides"
    ],
    "joineryTip": "High volumetric shrinkage requires proper indoor climate acclimation; machines cleanly with zero tear-out on edge router profiles.",
    "source": "CIRAD Forestry Compendium & The Wood Database",
    "hardness_lbf": 1304,
    "designStyles": [
      "Bauhaus",
      "Modern Minimalist",
      "Bentwood Classic"
    ],
    "property_sources": {
      "density": {
        "source": "CIRAD Forestry Compendium & The Wood Database",
        "approximate": false
      },
      "mor": {
        "source": "CIRAD Forestry Compendium & The Wood Database",
        "approximate": false
      },
      "hardness": {
        "source": "CIRAD Forestry Compendium & The Wood Database",
        "approximate": false
      },
      "shrinkage": {
        "source": "CIRAD Forestry Compendium & The Wood Database",
        "approximate": false
      },
      "durability": {
        "source": "CIRAD Forestry Compendium & The Wood Database",
        "approximate": false
      }
    }
  },
  {
    "id": "black_cherry",
    "name": "Black Cherry",
    "scientificName": "Prunus serotina",
    "density": 560,
    "mor": 84.8,
    "hardness": 4230,
    "shrinkage": {
      "radial": 3.7,
      "tangential": 7.1,
      "volumetric": 11.5,
      "stability_score": 8.6
    },
    "durability": 7.5,
    "workability": 9.2,
    "finishQuality": 9.8,
    "weightClass": "Medium",
    "costTier": 4,
    "availabilityInIndia": 6.0,
    "sustainability": 8.5,
    "outdoorSuitability": 5.5,
    "bestUses": [
      "Dining tables",
      "Bedside tables",
      "Drawer chests",
      "Picture frames",
      "Cabinets"
    ],
    "joineryTip": "Burn-prone on high-speed router bits; use fresh carbide cutters and steady continuous feed rates for pristine burn-free edges.",
    "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
    "hardness_lbf": 951,
    "designStyles": [
      "Shaker",
      "American Traditional",
      "Refined Craftsman"
    ],
    "property_sources": {
      "density": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      },
      "mor": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      },
      "hardness": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      },
      "shrinkage": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      },
      "durability": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      }
    }
  },
  {
    "id": "pine",
    "name": "Scots Pine",
    "scientificName": "Pinus sylvestris",
    "density": 510,
    "mor": 82.0,
    "hardness": 2420,
    "shrinkage": {
      "radial": 4.0,
      "tangential": 7.7,
      "volumetric": 12.4,
      "stability_score": 7.5
    },
    "durability": 5.0,
    "workability": 8.8,
    "finishQuality": 7.2,
    "weightClass": "Light-Medium",
    "costTier": 1,
    "availabilityInIndia": 8.5,
    "sustainability": 9.0,
    "outdoorSuitability": 4.5,
    "bestUses": [
      "Shelving",
      "Utility desks",
      "Wardrobe carcasses",
      "Internal drawer boxes",
      "Rustic benches"
    ],
    "joineryTip": "Softer cell structure requires coarse-threaded twin-fast screws; seal pitch knots with shellac before finishing to prevent bleeding.",
    "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
    "hardness_lbf": 544,
    "designStyles": [
      "Rustic Farmhouse",
      "Cottagecore",
      "Scandinavian Utility"
    ],
    "property_sources": {
      "density": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      },
      "mor": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      },
      "hardness": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      },
      "shrinkage": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      },
      "durability": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      }
    }
  },
  {
    "id": "western_red_cedar",
    "name": "Western Red Cedar",
    "scientificName": "Thuja plicata",
    "density": 370,
    "mor": 51.7,
    "hardness": 1560,
    "shrinkage": {
      "radial": 2.4,
      "tangential": 5.0,
      "volumetric": 6.8,
      "stability_score": 9.6
    },
    "durability": 9.2,
    "workability": 8.5,
    "finishQuality": 8.2,
    "weightClass": "Light",
    "costTier": 4,
    "availabilityInIndia": 6.5,
    "sustainability": 8.0,
    "outdoorSuitability": 9.5,
    "bestUses": [
      "Exterior screens",
      "Outdoor loungers",
      "Window sills",
      "Sauna benches",
      "Wardrobe linings"
    ],
    "joineryTip": "Low density crushes under high clamping pressure; use broad wooden clamping cauls and stainless steel fasteners to avoid black oxide stains.",
    "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
    "hardness_lbf": 351,
    "designStyles": [
      "Pacific Northwest",
      "Organic Architecture",
      "Spa / Wellness"
    ],
    "property_sources": {
      "density": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      },
      "mor": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      },
      "hardness": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      },
      "shrinkage": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      },
      "durability": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      }
    }
  },
  {
    "id": "deodar",
    "name": "Deodar Cedar",
    "scientificName": "Cedrus deodara",
    "density": 560,
    "mor": 78.0,
    "hardness": 3900,
    "shrinkage": {
      "radial": 3.6,
      "tangential": 5.8,
      "volumetric": 9.8,
      "stability_score": 9.0
    },
    "durability": 9.0,
    "workability": 8.2,
    "finishQuality": 8.5,
    "weightClass": "Medium",
    "costTier": 3,
    "availabilityInIndia": 9.0,
    "sustainability": 7.5,
    "outdoorSuitability": 9.0,
    "bestUses": [
      "Architectural doors",
      "Window frames",
      "Storage trunks",
      "Wardrobes",
      "Partitions"
    ],
    "joineryTip": "Natural aromatic oils make it naturally immune to Indian sub-continent termites without chemical pressure treatment.",
    "source": "Forest Research Institute (FRI) Dehradun (IS 399:1963)",
    "hardness_lbf": 877,
    "designStyles": [
      "Himalayan Heritage",
      "Ornate Carved",
      "Colonial Hill Station"
    ],
    "property_sources": {
      "density": {
        "source": "Forest Research Institute (FRI) Dehradun (IS 399:1963)",
        "approximate": false
      },
      "mor": {
        "source": "Forest Research Institute (FRI) Dehradun (IS 399:1963)",
        "approximate": false
      },
      "hardness": {
        "source": "Forest Research Institute (FRI) Dehradun (IS 399:1963)",
        "approximate": false
      },
      "shrinkage": {
        "source": "Forest Research Institute (FRI) Dehradun (IS 399:1963)",
        "approximate": false
      },
      "durability": {
        "source": "Forest Research Institute (FRI) Dehradun (IS 399:1963)",
        "approximate": false
      }
    }
  },
  {
    "id": "rubberwood",
    "name": "Rubberwood",
    "scientificName": "Hevea brasiliensis",
    "density": 595,
    "mor": 72.0,
    "hardness": 4350,
    "shrinkage": {
      "radial": 2.3,
      "tangential": 5.1,
      "volumetric": 7.5,
      "stability_score": 8.5
    },
    "durability": 4.0,
    "workability": 8.5,
    "finishQuality": 8.0,
    "weightClass": "Medium",
    "costTier": 1,
    "availabilityInIndia": 9.5,
    "sustainability": 9.8,
    "outdoorSuitability": 2.5,
    "bestUses": [
      "Dining tables",
      "Study desks",
      "Bunk beds",
      "Shoe racks",
      "Chairs"
    ],
    "joineryTip": "Dimensionally stable finger-jointed panels take edge gluing and pocket screws securely; always verify borate preservative treatment.",
    "source": "Malaysian Timber Industry Board (MTIB) & Rubber Research Institute of India (RRII)",
    "hardness_lbf": 978,
    "designStyles": [
      "Modern Commercial",
      "Urban Minimalist",
      "Eco Contemporary"
    ],
    "property_sources": {
      "density": {
        "source": "Malaysian Timber Industry Board (MTIB) & Rubber Research Institute of India (RRII)",
        "approximate": false
      },
      "mor": {
        "source": "Malaysian Timber Industry Board (MTIB) & Rubber Research Institute of India (RRII)",
        "approximate": false
      },
      "hardness": {
        "source": "Malaysian Timber Industry Board (MTIB) & Rubber Research Institute of India (RRII)",
        "approximate": false
      },
      "shrinkage": {
        "source": "Malaysian Timber Industry Board (MTIB) & Rubber Research Institute of India (RRII)",
        "approximate": false
      },
      "durability": {
        "source": "Malaysian Timber Industry Board (MTIB) & Rubber Research Institute of India (RRII)",
        "approximate": false
      }
    }
  },
  {
    "id": "acacia",
    "name": "Acacia (Babool)",
    "scientificName": "Acacia nilotica",
    "density": 830,
    "mor": 118.0,
    "hardness": 7120,
    "shrinkage": {
      "radial": 4.1,
      "tangential": 8.2,
      "volumetric": 12.5,
      "stability_score": 7.8
    },
    "durability": 8.8,
    "workability": 6.8,
    "finishQuality": 8.2,
    "weightClass": "Heavy",
    "costTier": 2,
    "availabilityInIndia": 9.8,
    "sustainability": 9.2,
    "outdoorSuitability": 8.5,
    "bestUses": [
      "Dining benches",
      "Shoe racks",
      "Rustic dining tables",
      "Stools",
      "Door frames"
    ],
    "joineryTip": "Extremely heavy and tough; pre-drill all pilot holes and use high-torque mechanical bar clamps during glue assembly.",
    "source": "Forest Research Institute (FRI) Dehradun (IS 399:1963)",
    "hardness_lbf": 1601,
    "designStyles": [
      "Live Edge Industrial",
      "Rustic Modern",
      "Bohemian"
    ],
    "property_sources": {
      "density": {
        "source": "Forest Research Institute (FRI) Dehradun (IS 399:1963)",
        "approximate": false
      },
      "mor": {
        "source": "Forest Research Institute (FRI) Dehradun (IS 399:1963)",
        "approximate": false
      },
      "hardness": {
        "source": "Forest Research Institute (FRI) Dehradun (IS 399:1963)",
        "approximate": false
      },
      "shrinkage": {
        "source": "Forest Research Institute (FRI) Dehradun (IS 399:1963)",
        "approximate": false
      },
      "durability": {
        "source": "Forest Research Institute (FRI) Dehradun (IS 399:1963)",
        "approximate": false
      }
    }
  },
  {
    "id": "mango",
    "name": "Mango Wood",
    "scientificName": "Mangifera indica",
    "density": 650,
    "mor": 82.0,
    "hardness": 4780,
    "shrinkage": {
      "radial": 3.6,
      "tangential": 6.2,
      "volumetric": 10.2,
      "stability_score": 8.0
    },
    "durability": 5.0,
    "workability": 8.2,
    "finishQuality": 9.0,
    "weightClass": "Medium",
    "costTier": 2,
    "availabilityInIndia": 9.8,
    "sustainability": 9.5,
    "outdoorSuitability": 3.5,
    "bestUses": [
      "Coffee tables",
      "Console tables",
      "Sideboards",
      "Wall shelves",
      "Accent chairs"
    ],
    "joineryTip": "Spalted patterns are visually breathtaking; stabilize softer spalted streaks with thin cyanoacrylate (CA) glue or penetrating epoxy.",
    "source": "Forest Research Institute (FRI) Dehradun & CIRAD",
    "hardness_lbf": 1075,
    "designStyles": [
      "Boho Chic",
      "Rustic Industrial",
      "Carved Ethnic"
    ],
    "property_sources": {
      "density": {
        "source": "Forest Research Institute (FRI) Dehradun & CIRAD",
        "approximate": false
      },
      "mor": {
        "source": "Forest Research Institute (FRI) Dehradun & CIRAD",
        "approximate": false
      },
      "hardness": {
        "source": "Forest Research Institute (FRI) Dehradun & CIRAD",
        "approximate": false
      },
      "shrinkage": {
        "source": "Forest Research Institute (FRI) Dehradun & CIRAD",
        "approximate": false
      },
      "durability": {
        "source": "Forest Research Institute (FRI) Dehradun & CIRAD",
        "approximate": false
      }
    }
  },
  {
    "id": "jackfruit",
    "name": "Jackfruit Wood",
    "scientificName": "Artocarpus heterophyllus",
    "density": 640,
    "mor": 86.0,
    "hardness": 4890,
    "shrinkage": {
      "radial": 2.8,
      "tangential": 5.0,
      "volumetric": 7.8,
      "stability_score": 9.2
    },
    "durability": 8.8,
    "workability": 8.0,
    "finishQuality": 9.0,
    "weightClass": "Medium",
    "costTier": 3,
    "availabilityInIndia": 9.0,
    "sustainability": 8.5,
    "outdoorSuitability": 8.0,
    "bestUses": [
      "Traditional doors",
      "Living room credenzas",
      "Dining chairs",
      "Musical instruments",
      "Cots"
    ],
    "joineryTip": "Historically revered for sacred temple architecture; high dimensional stability means doors and window sash never bind in humid monsoons.",
    "source": "Kerala Forest Research Institute (KFRI) Research Report 140",
    "hardness_lbf": 1099,
    "designStyles": [
      "Kerala Traditional",
      "Temple Heritage",
      "Warm Vernacular"
    ],
    "property_sources": {
      "density": {
        "source": "Kerala Forest Research Institute (KFRI) Research Report 140",
        "approximate": false
      },
      "mor": {
        "source": "Kerala Forest Research Institute (KFRI) Research Report 140",
        "approximate": false
      },
      "hardness": {
        "source": "Kerala Forest Research Institute (KFRI) Research Report 140",
        "approximate": false
      },
      "shrinkage": {
        "source": "Kerala Forest Research Institute (KFRI) Research Report 140",
        "approximate": false
      },
      "durability": {
        "source": "Kerala Forest Research Institute (KFRI) Research Report 140",
        "approximate": false
      }
    }
  },
  {
    "id": "bamboo",
    "name": "Engineered Moso Bamboo",
    "scientificName": "Phyllostachys edulis",
    "density": 700,
    "mor": 95.0,
    "hardness": 6200,
    "shrinkage": {
      "radial": 1.8,
      "tangential": 3.2,
      "volumetric": 5.2,
      "stability_score": 9.6
    },
    "durability": 6.5,
    "workability": 7.8,
    "finishQuality": 8.5,
    "weightClass": "Medium-Heavy",
    "costTier": 2,
    "availabilityInIndia": 8.5,
    "sustainability": 10.0,
    "outdoorSuitability": 5.0,
    "bestUses": [
      "Modern study desks",
      "Wall shelves",
      "Kitchen cabinets",
      "Cutting surfaces",
      "Partitions"
    ],
    "joineryTip": "Laminated edge grain holds mortise tenons firmly; seal cut end grain promptly to prevent edge delamination from ambient moisture.",
    "source": "International Network for Bamboo and Rattan (INBAR) & ASTM D143",
    "hardness_lbf": 1394,
    "designStyles": [
      "Zen Minimalist",
      "Eco-Modern",
      "Biophilic Architecture"
    ],
    "property_sources": {
      "density": {
        "source": "International Network for Bamboo and Rattan (INBAR) & ASTM D143",
        "approximate": false
      },
      "mor": {
        "source": "International Network for Bamboo and Rattan (INBAR) & ASTM D143",
        "approximate": false
      },
      "hardness": {
        "source": "International Network for Bamboo and Rattan (INBAR) & ASTM D143",
        "approximate": false
      },
      "shrinkage": {
        "source": "International Network for Bamboo and Rattan (INBAR) & ASTM D143",
        "approximate": false
      },
      "durability": {
        "source": "International Network for Bamboo and Rattan (INBAR) & ASTM D143",
        "approximate": false
      }
    }
  },
  {
    "id": "yellow_birch",
    "name": "Yellow Birch",
    "scientificName": "Betula alleghaniensis",
    "density": 690,
    "mor": 114.0,
    "hardness": 5610,
    "shrinkage": {
      "radial": 7.3,
      "tangential": 9.5,
      "volumetric": 16.8,
      "stability_score": 6.8
    },
    "durability": 4.0,
    "workability": 8.0,
    "finishQuality": 8.8,
    "weightClass": "Heavy",
    "costTier": 2,
    "availabilityInIndia": 6.5,
    "sustainability": 8.2,
    "outdoorSuitability": 3.0,
    "bestUses": [
      "Study tables",
      "Dining chairs",
      "Cabinet carcasses",
      "Turned legs",
      "Stools"
    ],
    "joineryTip": "Exceptionally high bending strength (114 MPa MOR); excels for structural chair stretchers and load-bearing carcass frames.",
    "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
    "hardness_lbf": 1261,
    "designStyles": [
      "Early American",
      "Classic Studio",
      "Clean Utility"
    ],
    "property_sources": {
      "density": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      },
      "mor": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      },
      "hardness": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      },
      "shrinkage": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      },
      "durability": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      }
    }
  },
  {
    "id": "poplar",
    "name": "Yellow Poplar (Tuliptree)",
    "scientificName": "Liriodendron tulipifera",
    "density": 450,
    "mor": 69.6,
    "hardness": 2400,
    "shrinkage": {
      "radial": 4.6,
      "tangential": 8.2,
      "volumetric": 12.7,
      "stability_score": 7.4
    },
    "durability": 4.0,
    "workability": 9.8,
    "finishQuality": 7.5,
    "weightClass": "Light",
    "costTier": 1,
    "availabilityInIndia": 7.0,
    "sustainability": 9.0,
    "outdoorSuitability": 2.5,
    "bestUses": [
      "Painted wardrobes",
      "Drawer sides and backs",
      "Photo frames",
      "Cabinet carcasses",
      "Crib parts"
    ],
    "joineryTip": "Premier choice for drawer boxes and secondary internal framing; takes paint to a flawless, mirror-smooth gloss finish.",
    "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
    "hardness_lbf": 540,
    "designStyles": [
      "Painted Cabinetry",
      "Modern Shaker",
      "Secondary Interior"
    ],
    "property_sources": {
      "density": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      },
      "mor": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      },
      "hardness": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      },
      "shrinkage": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      },
      "durability": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      }
    }
  },
  {
    "id": "ironwood",
    "name": "Ceylon Ironwood (Mesua)",
    "scientificName": "Mesua ferrea",
    "density": 1050,
    "mor": 152.0,
    "hardness": 13500,
    "shrinkage": {
      "radial": 5.2,
      "tangential": 9.6,
      "volumetric": 15.0,
      "stability_score": 6.5
    },
    "durability": 10.0,
    "workability": 4.0,
    "finishQuality": 7.8,
    "weightClass": "Extremely Heavy",
    "costTier": 4,
    "availabilityInIndia": 7.5,
    "sustainability": 6.5,
    "outdoorSuitability": 10.0,
    "bestUses": [
      "Heavy duty gates",
      "Exterior door frames",
      "Structural bridge beams",
      "Indestructible benches"
    ],
    "joineryTip": "Cannot be nailed or hand-screwed; must be bored with carbide drill bits and secured with stainless steel through-bolts.",
    "source": "Indian Forestry Bulletin No. 195 & CIRAD",
    "hardness_lbf": 3035,
    "designStyles": [
      "Monolithic Architectural",
      "Indestructible Heritage"
    ],
    "property_sources": {
      "density": {
        "source": "Indian Forestry Bulletin No. 195 & CIRAD",
        "approximate": false
      },
      "mor": {
        "source": "Indian Forestry Bulletin No. 195 & CIRAD",
        "approximate": false
      },
      "hardness": {
        "source": "Indian Forestry Bulletin No. 195 & CIRAD",
        "approximate": false
      },
      "shrinkage": {
        "source": "Indian Forestry Bulletin No. 195 & CIRAD",
        "approximate": false
      },
      "durability": {
        "source": "Indian Forestry Bulletin No. 195 & CIRAD",
        "approximate": false
      }
    }
  },
  {
    "id": "african_padauk",
    "name": "African Padauk",
    "scientificName": "Pterocarpus soyauxii",
    "density": 745,
    "mor": 116.0,
    "hardness": 8760,
    "hardness_lbf": 1970,
    "shrinkage": {
      "radial": 3.3,
      "tangential": 5.2,
      "volumetric": 7.6,
      "stability_score": 9.5
    },
    "durability": 9.5,
    "workability": 8.2,
    "finishQuality": 9.2,
    "weightClass": "Heavy",
    "costTier": 3,
    "availabilityInIndia": 6.0,
    "sustainability": 7.0,
    "outdoorSuitability": 9.5,
    "bestUses": [
      "Luxury dining tables",
      "Executive credenzas",
      "Guitar fretboards",
      "Exterior doors",
      "Display cabinets"
    ],
    "designStyles": [
      "Mid-Century Modern",
      "Contemporary Luxury",
      "Architectural Statement"
    ],
    "joineryTip": "One of the most dimensionally stable timbers on the planet; glues tenons securely with zero seasonal movement.",
    "source": "The Wood Database & USDA Wood Handbook (FPL-GTR-190)",
    "property_sources": {
      "density": {
        "source": "USDA FPL-GTR-190",
        "approximate": false
      },
      "mor": {
        "source": "The Wood Database",
        "approximate": false
      },
      "hardness": {
        "source": "USDA FPL-GTR-190",
        "approximate": false
      },
      "shrinkage": {
        "source": "The Wood Database",
        "approximate": false
      },
      "durability": {
        "source": "CIRAD Forestry Compendium",
        "approximate": false
      }
    }
  },
  {
    "id": "andaman_padauk",
    "name": "Andaman Padauk",
    "scientificName": "Pterocarpus dalbergioides",
    "density": 770,
    "mor": 106.0,
    "hardness": 7250,
    "hardness_lbf": 1630,
    "shrinkage": {
      "radial": 3.2,
      "tangential": 5.0,
      "volumetric": 7.8,
      "stability_score": 9.2
    },
    "durability": 9.0,
    "workability": 8.0,
    "finishQuality": 9.5,
    "weightClass": "Heavy",
    "costTier": 4,
    "availabilityInIndia": 7.5,
    "sustainability": 5.5,
    "outdoorSuitability": 9.0,
    "bestUses": [
      "Heritage carved furniture",
      "Conference tables",
      "Architectural doors",
      "Turned newel posts",
      "Veneer paneling"
    ],
    "designStyles": [
      "Indian Heritage",
      "Luxury Colonial",
      "Sculptural Fine Art"
    ],
    "joineryTip": "Endemic Indian hardwood; requires pre-boring for brass screws and sharp tooling to prevent tearout along interlocked ribbon grain.",
    "source": "Forest Research Institute (FRI) Dehradun (IS 399:1963) & The Wood Database",
    "property_sources": {
      "density": {
        "source": "Forest Research Institute (FRI) Dehradun IS 399",
        "approximate": false
      },
      "mor": {
        "source": "FRI Dehradun Timber Mechanics",
        "approximate": false
      },
      "hardness": {
        "source": "The Wood Database & FRI",
        "approximate": false
      },
      "shrinkage": {
        "source": "FRI Dehradun IS 399",
        "approximate": false
      },
      "durability": {
        "source": "FRI Natural Durability Testing",
        "approximate": false
      }
    }
  },
  {
    "id": "marupa",
    "name": "Marupa (Simarouba)",
    "scientificName": "Simarouba amara",
    "density": 440,
    "mor": 64.0,
    "hardness": 2150,
    "shrinkage": {
      "radial": 2.8,
      "tangential": 5.4,
      "volumetric": 8.5,
      "stability_score": 8.8
    },
    "durability": 4.5,
    "workability": 9.5,
    "finishQuality": 8.2,
    "weightClass": "Light",
    "costTier": 1,
    "availabilityInIndia": 8.0,
    "sustainability": 9.0,
    "outdoorSuitability": 3.0,
    "bestUses": [
      "Picture frames",
      "Wall shelving",
      "Drawer partitions",
      "Molding profiles",
      "Internal louvers"
    ],
    "joineryTip": "Lightweight and easy to router; exceptional choice for intricate shadowbox frames and clean-line moldings.",
    "source": "CIRAD Forestry Compendium & IBAMA Brazil",
    "hardness_lbf": 483,
    "designStyles": [
      "Light Modern",
      "Japanese Minimalist",
      "Secondary Core"
    ],
    "property_sources": {
      "density": {
        "source": "CIRAD Forestry Compendium & IBAMA Brazil",
        "approximate": false
      },
      "mor": {
        "source": "CIRAD Forestry Compendium & IBAMA Brazil",
        "approximate": false
      },
      "hardness": {
        "source": "CIRAD Forestry Compendium & IBAMA Brazil",
        "approximate": false
      },
      "shrinkage": {
        "source": "CIRAD Forestry Compendium & IBAMA Brazil",
        "approximate": false
      },
      "durability": {
        "source": "CIRAD Forestry Compendium & IBAMA Brazil",
        "approximate": false
      }
    }
  },
  {
    "id": "eucalyptus",
    "name": "Blue Gum Eucalyptus",
    "scientificName": "Eucalyptus globulus",
    "density": 820,
    "mor": 122.0,
    "hardness": 9280,
    "shrinkage": {
      "radial": 6.2,
      "tangential": 11.2,
      "volumetric": 17.5,
      "stability_score": 6.0
    },
    "durability": 8.0,
    "workability": 6.5,
    "finishQuality": 8.0,
    "weightClass": "Heavy",
    "costTier": 2,
    "availabilityInIndia": 9.5,
    "sustainability": 9.5,
    "outdoorSuitability": 7.5,
    "bestUses": [
      "Structural sofa frames",
      "Bed side rails",
      "Outdoor benches",
      "Stool legs",
      "Floorboards"
    ],
    "joineryTip": "Extremely high modulus of rupture (122 MPa); use slow kiln-dried boards to ensure internal drying stresses are fully relieved.",
    "source": "Australian Forestry Standard (AS 2082) & The Wood Database",
    "hardness_lbf": 2086,
    "designStyles": [
      "Australian Modern",
      "Industrial Structural",
      "Clean Utility"
    ],
    "property_sources": {
      "density": {
        "source": "Australian Forestry Standard (AS 2082) & The Wood Database",
        "approximate": false
      },
      "mor": {
        "source": "Australian Forestry Standard (AS 2082) & The Wood Database",
        "approximate": false
      },
      "hardness": {
        "source": "Australian Forestry Standard (AS 2082) & The Wood Database",
        "approximate": false
      },
      "shrinkage": {
        "source": "Australian Forestry Standard (AS 2082) & The Wood Database",
        "approximate": false
      },
      "durability": {
        "source": "Australian Forestry Standard (AS 2082) & The Wood Database",
        "approximate": false
      }
    }
  },
  {
    "id": "haldu",
    "name": "Haldu",
    "scientificName": "Haldina cordifolia",
    "density": 670,
    "mor": 94.0,
    "hardness": 5120,
    "shrinkage": {
      "radial": 3.5,
      "tangential": 6.8,
      "volumetric": 10.5,
      "stability_score": 8.4
    },
    "durability": 7.0,
    "workability": 9.0,
    "finishQuality": 9.2,
    "weightClass": "Medium",
    "costTier": 3,
    "availabilityInIndia": 9.0,
    "sustainability": 8.0,
    "outdoorSuitability": 6.0,
    "bestUses": [
      "Dressing tables",
      "Mirror frames",
      "Carved furniture panels",
      "Architectural partitions",
      "Bookcases"
    ],
    "joineryTip": "Favored by traditional master woodcarvers for its uniform grain that never splinters across chisel cuts.",
    "source": "Forest Research Institute (FRI) Dehradun (IS 399:1963)",
    "hardness_lbf": 1151,
    "designStyles": [
      "Indian Studio",
      "Turned Artistry",
      "Refined Traditional"
    ],
    "property_sources": {
      "density": {
        "source": "Forest Research Institute (FRI) Dehradun (IS 399:1963)",
        "approximate": false
      },
      "mor": {
        "source": "Forest Research Institute (FRI) Dehradun (IS 399:1963)",
        "approximate": false
      },
      "hardness": {
        "source": "Forest Research Institute (FRI) Dehradun (IS 399:1963)",
        "approximate": false
      },
      "shrinkage": {
        "source": "Forest Research Institute (FRI) Dehradun (IS 399:1963)",
        "approximate": false
      },
      "durability": {
        "source": "Forest Research Institute (FRI) Dehradun (IS 399:1963)",
        "approximate": false
      }
    }
  },
  {
    "id": "sapele",
    "name": "Sapele",
    "scientificName": "Entandrophragma cylindricum",
    "density": 670,
    "mor": 110.0,
    "hardness": 6280,
    "shrinkage": {
      "radial": 4.8,
      "tangential": 7.4,
      "volumetric": 12.8,
      "stability_score": 8.2
    },
    "durability": 8.0,
    "workability": 8.0,
    "finishQuality": 9.5,
    "weightClass": "Medium-Heavy",
    "costTier": 3,
    "availabilityInIndia": 7.5,
    "sustainability": 7.2,
    "outdoorSuitability": 7.5,
    "bestUses": [
      "Executive desks",
      "Dining tables",
      "Exterior doors",
      "Architectural woodwork",
      "Cabinets"
    ],
    "joineryTip": "Ribbon grain may tear out if planed directly against grain; skew hand plane at 20\u00b0 or use a scraping plane for flawless sheen.",
    "source": "The Wood Database & CIRAD Forestry Compendium",
    "hardness_lbf": 1412,
    "designStyles": [
      "Ribbon Contemporary",
      "Luxury Executive",
      "Modern Architectural"
    ],
    "property_sources": {
      "density": {
        "source": "The Wood Database & CIRAD Forestry Compendium",
        "approximate": false
      },
      "mor": {
        "source": "The Wood Database & CIRAD Forestry Compendium",
        "approximate": false
      },
      "hardness": {
        "source": "The Wood Database & CIRAD Forestry Compendium",
        "approximate": false
      },
      "shrinkage": {
        "source": "The Wood Database & CIRAD Forestry Compendium",
        "approximate": false
      },
      "durability": {
        "source": "The Wood Database & CIRAD Forestry Compendium",
        "approximate": false
      }
    }
  },
  {
    "id": "wenge",
    "name": "Wenge",
    "scientificName": "Millettia laurentii",
    "density": 870,
    "mor": 151.6,
    "hardness": 8600,
    "shrinkage": {
      "radial": 4.8,
      "tangential": 9.1,
      "volumetric": 14.0,
      "stability_score": 7.8
    },
    "durability": 9.5,
    "workability": 6.8,
    "finishQuality": 9.8,
    "weightClass": "Very Heavy",
    "costTier": 5,
    "availabilityInIndia": 6.0,
    "sustainability": 6.0,
    "outdoorSuitability": 8.5,
    "bestUses": [
      "Luxury console tables",
      "Coffee table accents",
      "Accent chairs",
      "Architectural baffles",
      "Picture frames"
    ],
    "joineryTip": "Sharp abrasive fibers can cause septic splinters; wear handling gloves during rough dimensioning and sand to fine grits.",
    "source": "The Wood Database & CIRAD Forestry Compendium",
    "hardness_lbf": 1933,
    "designStyles": [
      "Monochrome Modern",
      "High-Contrast Luxury",
      "Architectural Minimal"
    ],
    "property_sources": {
      "density": {
        "source": "The Wood Database & CIRAD Forestry Compendium",
        "approximate": false
      },
      "mor": {
        "source": "The Wood Database & CIRAD Forestry Compendium",
        "approximate": false
      },
      "hardness": {
        "source": "The Wood Database & CIRAD Forestry Compendium",
        "approximate": false
      },
      "shrinkage": {
        "source": "The Wood Database & CIRAD Forestry Compendium",
        "approximate": false
      },
      "durability": {
        "source": "The Wood Database & CIRAD Forestry Compendium",
        "approximate": false
      }
    }
  },
  {
    "id": "red_oak",
    "name": "Northern Red Oak",
    "scientificName": "Quercus rubra",
    "density": 700,
    "mor": 99.0,
    "hardness": 5740,
    "shrinkage": {
      "radial": 4.7,
      "tangential": 8.9,
      "volumetric": 13.7,
      "stability_score": 7.6
    },
    "durability": 6.0,
    "workability": 8.2,
    "finishQuality": 8.8,
    "weightClass": "Medium-Heavy",
    "costTier": 3,
    "availabilityInIndia": 7.0,
    "sustainability": 8.5,
    "outdoorSuitability": 5.0,
    "bestUses": [
      "Dining chairs",
      "Bookshelves",
      "Study desks",
      "Beds",
      "Cabinets"
    ],
    "joineryTip": "Open tubular grain pores absorb stains deeply; use grain filler before topcoating if a mirror-smooth gloss sheen is desired.",
    "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
    "hardness_lbf": 1290,
    "designStyles": [
      "American Craftsman",
      "Industrial Loft",
      "Warm Traditional"
    ],
    "property_sources": {
      "density": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      },
      "mor": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      },
      "hardness": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      },
      "shrinkage": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      },
      "durability": {
        "source": "USDA Wood Handbook (FPL-GTR-190) & The Wood Database",
        "approximate": false
      }
    }
  }
];
}));
