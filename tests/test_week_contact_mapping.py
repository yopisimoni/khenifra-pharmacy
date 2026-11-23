"""Validate that weekly pharmacy identities have explicit contact lookups."""
import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("week", ROOT / "api" / "week.py")
week = importlib.util.module_from_spec(spec)
spec.loader.exec_module(week)

class WeeklyContactMappingTests(unittest.TestCase):
    def test_najd_is_not_silently_dropped(self):
        self.assertEqual(week.WEEK_TO_NIGHT.get("NAJD"), "صيدلية نجد")

    def test_contact_mapping_retains_owner_supplied_phone(self):
        original = {"nameAr": "صيدلية نجد", "nameFr": "Pharmacie Najd",
                    "phone": "0535000000", "address": "Khénifra"}
        pharmacy = week.current_week_pharmacy("NAJD", 0, {"صيدلية نجد": original})
        self.assertEqual(pharmacy["phone"], original["phone"])
        self.assertEqual(pharmacy["address"], original["address"])

    def test_missing_phone_is_flagged_and_never_fabricated(self):
        pharmacy = week.current_week_pharmacy("NAJD", 0, {})
        self.assertEqual(pharmacy["phone"], "")
        self.assertTrue(pharmacy["phoneNeedsReview"])

if __name__ == "__main__":
    unittest.main()
