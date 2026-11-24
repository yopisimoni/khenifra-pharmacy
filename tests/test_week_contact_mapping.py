"""Validate that weekly pharmacy identities have explicit contact lookups."""
import importlib.util
import pathlib
import os
from unittest.mock import patch
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


    def test_separate_manager_approved_weekly_contact(self):
        record = '{"NAJD":{"nameFr":"Pharmacie Ennajd","phone":"0535000000","address":"Hay Ennajd"}}'
        with patch.dict(os.environ, {"WEEKLY_CONTACTS_JSON": record}):
            item = week.current_week_pharmacy("NAJD", 0, {})
        self.assertEqual(item["phone"], "0535000000")
        self.assertEqual(item["address"], "Hay Ennajd")
        self.assertEqual(item["nameFr"], "Pharmacie Ennajd")
        self.assertFalse(item["phoneNeedsReview"])
        self.assertFalse(item["addressNeedsReview"])

    def test_missing_weekly_contact_not_fabricated(self):
        with patch.dict(os.environ, {"WEEKLY_CONTACTS_JSON": "{}"}):
            item = week.current_week_pharmacy("HABRI", 0, {})
        self.assertEqual(item["phone"], "")
        self.assertTrue(item["phoneNeedsReview"])

    def test_weekly_contact_does_not_prove_location(self):
        with patch.dict(os.environ, {"WEEKLY_CONTACTS_JSON": '{"NAJD":{"phone":"0535000000","address":"X"}}',
                                      "VERIFIED_PHARMACY_PLACES_JSON": "{}"}):
            item = week.current_week_pharmacy("NAJD", 0, {})
        self.assertFalse(item["locationVerified"])
        self.assertEqual(item["placeId"], "")

if __name__ == "__main__":
    unittest.main()
