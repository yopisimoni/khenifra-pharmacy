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

TZ = ZoneInfo("Africa/Casablanca")

def sample_rotation():
    return [
        {
            "nameAr": ("صيدلية المسيرة الخضراء" if i == 0 else
                       "صيدلية النجاح" if i == 39 else f"صيدلية {i + 1}"),
            "nameFr": f"Pharmacie {i + 1}",
            "phone": "0535000000",
            "address": "خنيفرة"
        }
        for i in range(40)
    ]

class PreviewTests(unittest.TestCase):
    def test_without_rotation(self):
        with patch.dict(os.environ, {"NIGHT_ROTATION_JSON": ""}):
            self.assertIsNone(get_duty(datetime(2026, 11, 3, 22, tzinfo=TZ)))

    def test_night_schedule_and_seasonal_disclaimer(self):
        with patch.dict(os.environ, {"NIGHT_ROTATION_JSON": json.dumps(sample_rotation())}):
            item = get_duty(datetime(2026, 11, 3, 22, tzinfo=TZ))
            self.assertEqual(item["nameAr"], "صيدلية المسيرة الخضراء")
            self.assertEqual(item["startTime"], "21:00")
            self.assertEqual(item["endTime"], "09:00")
            self.assertTrue(item["startTimeMayVary"])
            self.assertTrue(item["scheduleBasedOnRotation"])
            self.assertFalse(item["upcoming"])

    def test_before_nine_shows_previous_night(self):
        with patch.dict(os.environ, {"NIGHT_ROTATION_JSON": json.dumps(sample_rotation())}):
            item = get_duty(datetime(2026, 11, 4, 8, 59, tzinfo=TZ))
            self.assertEqual(item["date"], "2026-11-03")
            self.assertEqual(item["nameAr"], "صيدلية المسيرة الخضراء")

    def test_cycle_restarts_at_forty_days(self):
        with patch.dict(os.environ, {"NIGHT_ROTATION_JSON": json.dumps(sample_rotation())}):
            self.assertEqual(get_duty(datetime(2026, 12, 12, 22, tzinfo=TZ))["nameAr"], "صيدلية النجاح")
            self.assertEqual(get_duty(datetime(2026, 12, 13, 22, tzinfo=TZ))["nameAr"], "صيدلية المسيرة الخضراء")

if __name__ == "__main__":
    unittest.main()
