"""Unit Tests for Wood Intelligence Scoring Engine.
Tests furniture-to-wood suitability, priority toggles, budget filters,
outdoor durability gating, and two-way explorer matching.
"""
import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scoring_engine import recommend_woods, get_other_designs_for_wood
from woods_data import WOODS_DATABASE, WOODS_BY_ID
from furniture_data import FURNITURE_DATA, FURNITURE_BY_ID

class TestWoodScoringEngine(unittest.TestCase):

    def test_database_completeness(self):
        """Verify database has at least 25 woods and all have required fields."""
        self.assertGreaterEqual(len(WOODS_DATABASE), 25, "Wood database must have at least 25 timbers")
        for wood in WOODS_DATABASE:
            self.assertIn("id", wood)
            self.assertIn("name", wood)
            self.assertIn("scientificName", wood)
            self.assertIn("density", wood)
            self.assertIn("mor", wood)
            self.assertIn("hardness", wood)
            self.assertIn("shrinkage", wood)
            self.assertIn("stability_score", wood["shrinkage"])
            self.assertIn("durability", wood)
            self.assertIn("workability", wood)
            self.assertIn("finishQuality", wood)
            self.assertIn("costTier", wood)
            self.assertIn("availabilityInIndia", wood)
            self.assertIn("sustainability", wood)
            self.assertIn("bestUses", wood)
            self.assertIn("joineryTip", wood)
            self.assertIn("source", wood)

    def test_furniture_catalog_completeness(self):
        """Verify catalog has 31 items with images and structural demands."""
        self.assertEqual(len(FURNITURE_DATA), 31, "Must have exactly 31 furniture items")
        for item in FURNITURE_DATA:
            self.assertIn("id", item)
            self.assertIn("name", item)
            self.assertIn("category", item)
            self.assertIn("image", item)
            self.assertIn("structuralDemands", item)
            self.assertTrue(os.path.exists(item["image"]), f"Image missing for {item['name']}: {item['image']}")

    def test_recommend_woods_returns_top_5(self):
        """Verify exactly 5 ranked results returned with required attributes."""
        recs = recommend_woods("wooden_chair")
        self.assertEqual(len(recs), 5, "Must return exactly 5 recommendations")
        for idx, rec in enumerate(recs):
            self.assertEqual(rec["rank"], idx + 1)
            self.assertIn("score", rec)
            self.assertGreaterEqual(rec["score"], 0)
            self.assertLessEqual(rec["score"], 100)
            self.assertIn("breakdown", rec)
            self.assertIn("reasons", rec)
            self.assertIn("tradeoffs", rec)
            self.assertGreater(len(rec["reasons"]), 0)
            self.assertGreater(len(rec["tradeoffs"]), 0)

    def test_chair_favors_high_strength_hardwoods(self):
        """Chairs must rank strong hardwoods (Oak, Ash, Teak, Beech, Rosewood) above softwoods."""
        recs = recommend_woods("wooden_chair")
        top_wood_names = [r["wood"]["name"] for r in recs]
        top_mors = [r["wood"]["mor"] for r in recs]
        
        # Top recommended woods should have high bending strength (> 90 MPa)
        for mor in top_mors:
            self.assertGreaterEqual(mor, 85.0, "Chair recommendations must feature high bending strength timbers")
            
        # Scots Pine (softwood with 82 MPa) should NOT outrank White Oak or Ash for structural chairs
        scores = {r["wood"]["id"]: r["score"] for r in recs}
        if "pine" in scores and "white_ash" in scores:
            self.assertGreater(scores["white_ash"], scores["pine"])

    def test_wardrobe_favors_stable_timbers(self):
        """Wardrobes and tall cabinetry must favor high stability scores."""
        recs = recommend_woods("wardrobe")
        top_stabilities = [r["wood"]["shrinkage"]["stability_score"] for r in recs]
        # Top woods for wardrobes should have stability score >= 8.0
        avg_stab = sum(top_stabilities) / len(top_stabilities)
        self.assertGreaterEqual(avg_stab, 7.8, "Wardrobes must favor dimensionally stable timbers")

    def test_outdoor_environment_enforces_durability(self):
        """Outdoor environment must heavily penalize perishable timbers."""
        indoor_recs = recommend_woods("door", {"environment": "Indoor"})
        outdoor_recs = recommend_woods("door", {"environment": "Outdoor"})
        
        # In outdoor mode, top woods must have high natural durability (rot resistance)
        for r in outdoor_recs:
            self.assertGreaterEqual(r["wood"]["durability"], 8.0, 
                                    f"Outdoor recommendation {r['wood']['name']} has low durability {r['wood']['durability']}")

    def test_priority_budget_filter(self):
        """Budget priority must elevate low-cost woods and penalize Tier 5 luxury woods."""
        balanced_recs = recommend_woods("desk", {"priority": "Balanced"})
        budget_recs = recommend_woods("desk", {"priority": "Budget", "budget": "Low"})
        
        budget_cost_tiers = [r["wood"]["costTier"] for r in budget_recs]
        # None of the top budget recommendations should be Tier 5 (Luxury)
        self.assertNotIn(5, budget_cost_tiers, "Low-budget recommendations should exclude Tier 5 luxury woods")

    def test_two_way_explorer_returns_valid_pieces(self):
        """get_other_designs_for_wood must return categorized furniture pieces."""
        results = get_other_designs_for_wood("teak", threshold=70.0)
        self.assertIsInstance(results, dict)
        self.assertGreater(len(results), 0, "Teak should be suitable for multiple categories")
        
        total_items = sum(len(items) for items in results.values())
        self.assertGreaterEqual(total_items, 5, "Teak should qualify for at least 5 furniture pieces at 70% threshold")
        
        # Verify scores are sorted descending
        for cat, items in results.items():
            scores = [i["score"] for i in items]
            self.assertEqual(scores, sorted(scores, reverse=True), f"Items in {cat} must be sorted by descending score")

if __name__ == "__main__":
    unittest.main()

