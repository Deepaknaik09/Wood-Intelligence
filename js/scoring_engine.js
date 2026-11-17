/**
 * Decoupled Multi-Criteria Scoring Engine for Wood Intelligence.
 * Pure, deterministic function computing normalized engineering fit for any furniture piece.
 */
(function (root, factory) {{
    if (typeof define === 'function' && define.amd) {{
        define(['./furniture.data.js', './woods.data.js'], factory);
    }} else if (typeof module === 'object' && module.exports) {{
        module.exports = factory(require('../data/furniture.data.js'), require('../data/woods.data.js'));
    }} else {{
        root.ScoringEngine = factory(root.FURNITURE_DATA, root.WOODS_DATABASE);
    }}
}}(typeof self !== 'undefined' ? self : this, function (furnitureData, woodsData) {{
    'use strict';

    var furnitureById = {};
    if (Array.isArray(furnitureData)) {
        furnitureData.forEach(function (f) {
            furnitureById[f.id] = f;
            furnitureById[f.id.replace(/_/g, '-')] = f;
        });
    }

    var woodsById = {};
    var woodsList = Array.isArray(woodsData) ? woodsData : [];
    woodsList.forEach(function (w) {
        woodsById[w.id] = w;
        woodsById[w.id.replace(/_/g, '-')] = w;
    });
    if (woodsById['african_padauk']) {
        woodsById['padauk'] = woodsById['african_padauk'];
    }

    // Default category base weights
    var CATEGORY_WEIGHTS = {
        'Seating & Chairs': { strength: 0.35, hardness: 0.20, stability: 0.15, workability: 0.15, finish: 0.15 },
        'Tables & Desks': { strength: 0.20, hardness: 0.30, stability: 0.25, workability: 0.10, finish: 0.15 },
        'Beds & Bedroom': { strength: 0.30, hardness: 0.15, stability: 0.25, workability: 0.15, finish: 0.15 },
        'Storage & Shelves': { strength: 0.20, hardness: 0.15, stability: 0.30, workability: 0.20, finish: 0.15 },
        'Architectural & Frames': { strength: 0.25, hardness: 0.15, stability: 0.30, workability: 0.10, finish: 0.20 }
    };

    function normRange(val, minV, maxV) {
        if (val <= minV) return 0.0;
        if (val >= maxV) return 1.0;
        return (val - minV) / (maxV - minV);
    }

    function normDensity(val) {
        // Optimal range 560 - 780 kg/m³
        if (val < 420) return 0.40 + (val - 350) / 70 * 0.25;
        if (val <= 780) return 0.70 + (val - 420) / 360 * 0.30;
        if (val <= 900) return 1.0 - (val - 780) / 120 * 0.15;
        return Math.max(0.60, 0.85 - (val - 900) / 250 * 0.25);
    }

    var FURNITURE_FIT = {
        'wooden_chair': ['white_ash', 'white_oak', 'beech', 'teak', 'african_padauk'],
        'dining_chair': ['beech', 'white_ash', 'white_oak', 'black_walnut', 'teak'],
        'armchair': ['black_walnut', 'white_oak', 'teak', 'sheesham', 'mahogany'],
        'stool': ['hard_maple', 'white_ash', 'beech', 'acacia', 'rubberwood'],
        'bench': ['sal', 'white_ash', 'white_oak', 'acacia', 'eucalyptus'],
        'wooden_sofa_frame': ['sheesham', 'teak', 'sal', 'eucalyptus', 'white_oak'],
        'dining_table': ['teak', 'black_walnut', 'sheesham', 'white_oak', 'black_cherry'],
        'coffee_table': ['black_walnut', 'mango', 'teak', 'sheesham', 'wenge'],
        'study_table': ['hard_maple', 'bamboo', 'white_oak', 'rubberwood', 'teak'],
        'desk': ['black_walnut', 'mahogany', 'white_oak', 'hard_maple', 'sapele'],
        'side_table': ['black_cherry', 'teak', 'mango', 'sheesham', 'black_walnut'],
        'console_table': ['mahogany', 'mango', 'wenge', 'teak', 'black_walnut'],
        'dining_set': ['sheesham', 'teak', 'white_oak', 'beech', 'african_padauk'],
        'bed_frame': ['sheesham', 'teak', 'mahogany', 'sal', 'rubberwood'],
        'bunk_bed': ['sal', 'rubberwood', 'hard_maple', 'teak', 'eucalyptus'],
        'cot': ['hard_maple', 'sheesham', 'teak', 'jackfruit', 'rubberwood'],
        'bedside_table': ['black_cherry', 'black_walnut', 'teak', 'yellow_birch', 'mango'],
        'dressing_table': ['haldu', 'black_walnut', 'sheesham', 'black_cherry', 'teak'],
        'wardrobe': ['deodar', 'teak', 'sheesham', 'mahogany', 'white_oak'],
        'cupboard': ['deodar', 'teak', 'white_oak', 'yellow_birch', 'rubberwood'],
        'cabinet': ['sheesham', 'teak', 'white_oak', 'black_cherry', 'mahogany'],
        'bookshelf': ['white_oak', 'hard_maple', 'white_ash', 'red_oak', 'bamboo'],
        'wall_shelf': ['bamboo', 'mango', 'white_oak', 'poplar', 'marupa'],
        'tv_unit': ['sheesham', 'teak', 'black_walnut', 'mango', 'wenge'],
        'drawer_chest': ['black_cherry', 'deodar', 'yellow_birch', 'teak', 'beech'],
        'shoe_rack': ['acacia', 'rubberwood', 'deodar', 'mango', 'yellow_birch'],
        'door': ['teak', 'deodar', 'sal', 'andaman_padauk', 'african_padauk'],
        'window_frame': ['deodar', 'teak', 'sal', 'western_red_cedar', 'andaman_padauk'],
        'mirror_frame': ['haldu', 'black_walnut', 'black_cherry', 'mango', 'sheesham'],
        'photo_frame': ['black_cherry', 'marupa', 'poplar', 'haldu', 'beech'],
        'wooden_partition': ['bamboo', 'deodar', 'haldu', 'teak', 'sheesham']
    };

    function recommendWoods(furnitureId, options) {
        options = options || {};
        var priority = options.priority || 'Balanced';
        var budget = options.budget || 'All';
        var env = options.environment || 'Indoor';

        var item = furnitureById[furnitureId] || furnitureById[String(furnitureId).replace(/-/g, '_')] || (furnitureData && furnitureData[0]);
        if (!item) return [];

        var fId = (item.id || '').replace(/-/g, '_');
        var premierList = FURNITURE_FIT[fId] || [];

        var cat = item.category || 'Seating & Chairs';
        var baseWeights = Object.assign({}, CATEGORY_WEIGHTS[cat] || CATEGORY_WEIGHTS['Seating & Chairs']);

        // Structural overrides if specified
        var demands = item.structuralDemands || {};
        if (demands.weightImportance) {
            baseWeights.strength = demands.weightImportance;
        }
        if (demands.hardnessImportance) {
            baseWeights.hardness = demands.hardnessImportance;
        }
        if (demands.stabilityImportance) {
            baseWeights.stability = demands.stabilityImportance;
        }

        // Apply Priority Modifiers
        var weights = Object.assign({}, baseWeights);
        if (priority === 'Strength') {
            weights.strength *= 1.8;
            weights.hardness *= 1.3;
        } else if (priority === 'Stability') {
            weights.stability *= 2.0;
        } else if (priority === 'Looks') {
            weights.finish *= 2.2;
            weights.workability *= 1.3;
        } else if (priority === 'Eco') {
            weights.workability *= 1.2;
        }

        // Normalize weights sum to 1.0
        var totalW = weights.strength + weights.hardness + weights.stability + weights.workability + weights.finish;
        Object.keys(weights).forEach(function (k) {
            weights[k] /= totalW;
        });

        var scored = [];
        woodsList.forEach(function (wood) {
            // Budget constraint filter
            if (budget === 'Low' && wood.costTier > 2) return;
            if (budget === 'Medium' && wood.costTier > 3) return;
            if (budget === 'High' && wood.costTier < 3) return;

            // Compute normalized criteria (0 - 1)
            var nMor = normRange(wood.mor, 50.0, 115.0);
            var nHard = normRange(wood.hardness, 1500.0, 6800.0);
            var nStab = normRange(wood.shrinkage ? wood.shrinkage.stability_score : 7.0, 5.0, 9.8);
            var nWork = normRange(wood.workability, 4.0, 9.5);
            var nFin = normRange(wood.finishQuality, 5.0, 9.8);
            var nDens = normDensity(wood.density);

            var rawScore = (
                nMor * weights.strength +
                nHard * weights.hardness +
                nStab * weights.stability +
                nWork * weights.workability +
                nFin * weights.finish
            );

            // Density alignment modifier
            rawScore = rawScore * 0.90 + nDens * 0.10;

            // Outdoor durability requirement
            if (env === 'Outdoor') {
                var durFactor = (wood.durability || 5.0) / 10.0;
                rawScore = rawScore * 0.65 + durFactor * 0.35;
                if ((wood.durability || 5.0) < 6.0) {
                    rawScore *= 0.65; // Severe penalty for non-durable timbers outdoors
                }
            }

            // Priority modifiers
            if (priority === 'Budget') {
                var ecoFactor = (6 - wood.costTier) / 5.0;
                rawScore = rawScore * 0.75 + ecoFactor * 0.25;
            } else if (priority === 'Eco') {
                var sustFactor = (wood.sustainability || 7.0) / 10.0;
                rawScore = rawScore * 0.70 + sustFactor * 0.30;
            }

            // Craftsmanship design suitability bonus
            if (premierList.indexOf(wood.id) !== -1) {
                var pos = premierList.indexOf(wood.id);
                var bonus = 20.0 - (pos * 3.75);
                rawScore += (bonus / 100.0);
            }

            // Convert to 0 - 100 score
            var finalScore = Math.min(99.4, Math.max(52.0, rawScore * 100.0));

            // Generate plain-English reasons & trade-offs
            var reasons = [];
            var tradeoffs = [];

            if (premierList.indexOf(wood.id) !== -1) {
                reasons.push('Classically favored master timber for handcrafted ' + (item.name || 'furniture').toLowerCase() + ' joinery.');
            }

            if (wood.mor >= 100.0) {
                reasons.push('High bending strength (' + wood.mor.toFixed(1) + ' MPa) ensures structural joints endure heavy cyclic loads.');
            } else if (wood.mor >= 80.0) {
                reasons.push('Well-balanced modulus of rupture (' + wood.mor.toFixed(1) + ' MPa) provides reliable domestic resilience.');
            } else {
                tradeoffs.push('Moderate flexural strength (' + wood.mor.toFixed(1) + ' MPa); requires reinforced rail joinery.');
            }

            if (wood.shrinkage && wood.shrinkage.stability_score >= 8.5) {
                reasons.push('Outstanding dimensional stability (Score ' + wood.shrinkage.stability_score + '/10) resists seasonal warping.');
            }

            if (wood.hardness >= 5500) {
                reasons.push('Dense Janka hardness (' + wood.hardness + ' N) resists denting, scratches, and surface wear.');
            }

            if (wood.costTier >= 4) {
                tradeoffs.push('Premium commercial pricing (Cost Tier ' + wood.costTier + '/5); elevated material investment.');
            } else if (wood.costTier <= 2) {
                reasons.push('Highly cost-effective (Tier ' + wood.costTier + '/5) with excellent timber yield.');
            }

            if (wood.availabilityInIndia <= 5.0) {
                tradeoffs.push('Limited regional availability in Indian timber depots; may require specialty lumber import.');
            }

            if (wood.workability >= 8.0) {
                reasons.push('Superb workability (' + wood.workability + '/10); cuts crisp tenons and responds cleanly to hand planes.');
            } else if (wood.workability <= 5.0) {
                tradeoffs.push('Dense grain increases cutter dulling; requires carbide-tipped workshop tooling.');
            }

            scored.push({
                wood: wood,
                score: Math.round(finalScore * 10) / 10,
                breakdown: {
                    bendingStrength: Math.round(nMor * 100),
                    hardness: Math.round(nHard * 100),
                    dimensionalStability: Math.round(nStab * 100),
                    workability: Math.round(nWork * 100),
                    finishQuality: Math.round(nFin * 100),
                    weightsUsed: weights
                },
                reasons: reasons.slice(0, 3),
                tradeoffs: tradeoffs.length ? tradeoffs.slice(0, 2) : ['Requires standard climate acclimation before glue-up.']
            });
        });

        // Deterministic sorting: Score desc, then costTier asc, then availability desc
        scored.sort(function (a, b) {
            if (b.score !== a.score) return b.score - a.score;
            if (a.wood.costTier !== b.wood.costTier) return a.wood.costTier - b.wood.costTier;
            return (b.wood.availabilityInIndia || 0) - (a.wood.availabilityInIndia || 0);
        });

        var top5 = scored.slice(0, 5);
        top5.forEach(function (res, idx) {
            res.rank = idx + 1;
            res.isBestMatch = (idx === 0);
        });

        return top5;
    }

    function getOtherDesignsForWood(woodId, threshold, options) {
        threshold = threshold || 70.0;
        options = options || {};

        var wood = woodsById[woodId] || woodsById[String(woodId).replace(/-/g, '_')];
        if (!wood) return {};

        var categorized = {};
        (furnitureData || []).forEach(function (fItem) {
            var recs = recommendWoods(fItem.id, options);
            var match = recs.find(function (r) {
                return r.wood.id === wood.id;
            });

            var score = match ? match.score : 0;
            if (!match) {
                // Secondary check if wood is among general recommendations
                var genRecs = recommendWoods(fItem.id, { priority: 'Balanced', budget: 'All', environment: 'Indoor' });
                var genMatch = genRecs.find(function (r) {
                    return r.wood.id === wood.id;
                });
                score = genMatch ? genMatch.score : 65.0;
            }

            if (score >= threshold) {
                var c = fItem.category || 'Other';
                if (!categorized[c]) categorized[c] = [];
                categorized[c].push({
                    item: fItem,
                    score: score
                });
            }
        });

        // Sort items inside each category by score desc
        Object.keys(categorized).forEach(function (c) {
            categorized[c].sort(function (a, b) {
                return b.score - a.score;
            });
        });

        return categorized;
    }

    return {
        recommendWoods: recommendWoods,
        getOtherDesignsForWood: getOtherDesignsForWood,
        getFurnitureById: function (id) {
            return furnitureById[id] || furnitureById[String(id).replace(/-/g, '_')] || (furnitureData && furnitureData[0]);
        },
        getWoodById: function (id) {
            return woodsById[id] || woodsById[String(id).replace(/-/g, '_')] || (woodsList && woodsList[0]);
        },
        getAllWoods: function () {
            return woodsList;
        },
        getAllFurniture: function () {
            return furnitureData || [];
        }
    };
}));
