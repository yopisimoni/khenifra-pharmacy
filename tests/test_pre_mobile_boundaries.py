import json
import os
import sys
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "api"))
from night import get_duty
from week import get_current_week

TZ = ZoneInfo("Africa/Casablanca")

def rotation():
    return [{"nameAr": f"صيدلية {i+1}", "nameFr": f"Pharmacie {i+1}",
             "phone": "0535000000", "address": "Khénifra"}
            for i in range(40)]

class PreMobileBoundaryTests(unittest.TestCase):
    def test_night_share_id_changes_by_pharmacy(self):
        with patch.dict(os.environ, {"NIGHT_ROTATION_JSON": json.dumps(rotation()),
                                      "VERIFIED_PHARMACY_PLACES_JSON": "{}"}):
            a = get_duty(datetime(2026, 11, 3, 22, tzinfo=TZ))
            b = get_duty(datetime(2026, 11, 4, 22, tzinfo=TZ))
            self.assertNotEqual(a["id"], b["id"])
            self.assertEqual(a["id"], "night-01")
            self.assertEqual(b["id"], "night-02")

    def test_night_share_id_is_stable_on_repeat(self):
        with patch.dict(os.environ, {"NIGHT_ROTATION_JSON": json.dumps(rotation()),
                                      "VERIFIED_PHARMACY_PLACES_JSON": "{}"}):
            a = get_duty(datetime(2026, 11, 3, 22, tzinfo=TZ))
            repeat = get_duty(datetime(2026, 12, 13, 22, tzinfo=TZ))
            self.assertEqual(a["id"], repeat["id"])

    def test_weekly_share_id_is_stable_and_distinct(self):
        week = [["2026-11-02", "2026-11-08", "JABOR", "TOUHAMI"]]
        env = {"WEEKLY_ROTATION_JSON": json.dumps(week),
               "NIGHT_ROTATION_JSON": json.dumps(rotation()),
               "VERIFIED_PHARMACY_PLACES_JSON": "{}"}
        with patch.dict(os.environ, env):
            result = get_current_week(datetime(2026, 11, 3, 14, tzinfo=TZ))
            ids = [p["id"] for p in result["pharmacies"]]
            self.assertEqual(ids, ["week-jabor", "week-touhami"])
            self.assertEqual(len(set(ids)), 2)

    def test_weekly_missing_contact_is_explicit_and_never_invented(self):
        week = [["2026-11-09", "2026-11-15", "AMALOU", "NAJAH"]]
        env = {"WEEKLY_ROTATION_JSON": json.dumps(week),
               "NIGHT_ROTATION_JSON": json.dumps(rotation()),
               "VERIFIED_PHARMACY_PLACES_JSON": "{}"}
        with patch.dict(os.environ, env):
            data = get_current_week(datetime(2026, 11, 9, 14, tzinfo=TZ))
            amalou = data["pharmacies"][0]
            self.assertEqual(amalou["nameAr"], "صيدلية أمالو")
            self.assertEqual(amalou["phone"], "0535586232")
            self.assertTrue(amalou["phoneNeedsReview"])
            self.assertTrue(amalou["addressNeedsReview"])
            self.assertEqual(amalou["address"], "")

    def test_weekly_expiry(self):
        env = {"WEEKLY_ROTATION_JSON": json.dumps([["2026-11-02", "2026-11-08", "JABOR", "TOUHAMI"]]),
               "NIGHT_ROTATION_JSON": "[]"}
        with patch.dict(os.environ, env):
            self.assertIsNone(get_current_week(datetime(2026, 11, 9, 12, tzinfo=TZ)))

if __name__ == "__main__":
    unittest.main()
