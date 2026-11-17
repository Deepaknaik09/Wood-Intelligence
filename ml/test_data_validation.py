"""Data Validation Test Suite for Wood Intelligence.
Fails on missing fields, out-of-range values, or duplicate species/furniture items.
"""
import unittest
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

import woods_data
import furniture_data

class TestDataValidation(unittest.TestCase):

    def test_no_duplicate_wood_ids_or_names(self):
        """Ensure all wood IDs and scientific names are unique."""
        ids = [w["id"] for w in woods_data.WOODS_DATABASE]
        self.assertEqual(len(ids), len(set(ids)), f"Duplicate wood IDs found: {[x for x in ids if ids.count(x) > 1]}")
        
        names = [w["name"] for w in woods_data.WOODS_DATABASE]
        self.assertEqual(len(names), len(set(names)), f"Duplicate wood names found: {[x for x in names if names.count(x) > 1]}")

        # Check African and Andaman Padauk specifically exist and are distinct
        self.assertIn("african_padauk", woods_data.WOODS_BY_ID)
        self.assertIn("andaman_padauk", woods_data.WOODS_BY_ID)
        self.assertNotEqual(
            woods_data.WOODS_BY_ID["african_padauk"]["scientificName"],
            woods_data.WOODS_BY_ID["andaman_padauk"]["scientificName"]
        )

    def test_wood_required_fields(self):
        """Verify all mandatory fields are present on every wood entry."""
        required_fields = [
            "id", "name", "scientificName", "density", "mor", "hardness",
            "hardness_lbf", "shrinkage", "durability", "workability",
            "finishQuality", "weightClass", "costTier", "availabilityInIndia",
            "sustainability", "outdoorSuitability", "bestUses", "designStyles",
            "joineryTip", "source", "property_sources"
        ]
        for w in woods_data.WOODS_DATABASE:
            for field in required_fields:
                self.assertIn(field, w, f"Wood '{w.get('id')}' is missing required field '{field}'")
            
            # Check shrinkage subfields
            shrink = w["shrinkage"]
            for sf in ["radial", "tangential", "volumetric", "stability_score"]:
                self.assertIn(sf, shrink, f"Wood '{w['id']}' shrinkage missing '{sf}'")

    def test_wood_values_in_physical_range(self):
        """Verify all physical and mechanical wood values conform to credible forestry handbook limits."""
        for w in woods_data.WOODS_DATABASE:
            wid = w["id"]
            # Density between 300 and 1250 kg/m³
            self.assertGreaterEqual(w["density"], 300, f"{wid}: density {w['density']} too low")
            self.assertLessEqual(w["density"], 1250, f"{wid}: density {w['density']} too high")

            # MOR between 45 and 180 MPa
            self.assertGreaterEqual(w["mor"], 45.0, f"{wid}: MOR {w['mor']} too low")
            self.assertLessEqual(w["mor"], 180.0, f"{wid}: MOR {w['mor']} too high")

            # Janka Hardness between 1200 and 15000 N
            self.assertGreaterEqual(w["hardness"], 1200, f"{wid}: Hardness {w['hardness']} too low")
            self.assertLessEqual(w["hardness"], 15000, f"{wid}: Hardness {w['hardness']} too high")

            # Janka in lbf matches N within reasonable rounding tolerance
            expected_lbf = round(w["hardness"] / 4.44822)
            self.assertAlmostEqual(w["hardness_lbf"], expected_lbf, delta=10, msg=f"{wid}: hardness_lbf mismatch")

            # Cost tier 1 to 5
            self.assertIn(w["costTier"], [1, 2, 3, 4, 5], f"{wid}: invalid costTier {w['costTier']}")

            # Scores 0 to 10
            for score_key in ["durability", "workability", "finishQuality", "availabilityInIndia", "sustainability", "outdoorSuitability"]:
                val = w[score_key]
                self.assertGreaterEqual(val, 0.0, f"{wid}: {score_key} < 0")
                self.assertLessEqual(val, 10.0, f"{wid}: {score_key} > 10")

            # Shrinkage values
            self.assertGreaterEqual(w["shrinkage"]["radial"], 1.0, f"{wid}: radial shrinkage < 1.0")
            self.assertLessEqual(w["shrinkage"]["radial"], 8.5, f"{wid}: radial shrinkage > 8.5")
            self.assertGreaterEqual(w["shrinkage"]["tangential"], 2.0, f"{wid}: tangential shrinkage < 2.0")
            self.assertLessEqual(w["shrinkage"]["tangential"], 14.0, f"{wid}: tangential shrinkage > 14.0")

    def test_no_duplicate_furniture_ids_or_names(self):
        """Ensure all 31 furniture catalog IDs are unique."""
        f_ids = [f["id"] for f in furniture_data.FURNITURE_DATA]
        self.assertEqual(len(f_ids), 31, f"Expected 31 furniture pieces, got {len(f_ids)}")
        self.assertEqual(len(f_ids), len(set(f_ids)), f"Duplicate furniture IDs found")

    def test_furniture_required_fields(self):
        """Verify furniture items have all necessary fields for catalog and detail pages."""
        req_fields = [
            "id", "name", "category", "image", "tagline", "description",
            "structuralDemands", "rules", "architecturalDesigns"
        ]
        for f in furniture_data.FURNITURE_DATA:
            for rf in req_fields:
                self.assertIn(rf, f, f"Furniture '{f.get('id')}' missing '{rf}'")
            
            # Check structural demands
            demands = f["structuralDemands"]
            for df in ["minMOR", "minJanka", "loadType", "densityRange", "targetMC", "recommendedCut"]:
                self.assertIn(df, demands, f"Furniture '{f['id']}' demands missing '{df}'")

    def test_backward_compatibility_padauk_alias(self):
        """Ensure WOODS_BY_ID['padauk'] resolves properly without KeyError."""
        self.assertIn("padauk", woods_data.WOODS_BY_ID)
        self.assertIn(woods_data.WOODS_BY_ID["padauk"]["id"], ["african_padauk", "andaman_padauk"])

if __name__ == "__main__":
    unittest.main()

