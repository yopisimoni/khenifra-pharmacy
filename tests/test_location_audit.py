import csv
import json
import tempfile
import unittest
from pathlib import Path
from scripts.location_audit import prepare, approve, export

class LocationAuditTests(unittest.TestCase):
    def test_requires_human_approval(self):
        with tempfile.TemporaryDirectory() as d:
            source = Path(d) / "source.csv"
            with source.open("w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=["اسم الصيدلية","الهاتف","العنوان"])
                w.writeheader()
                w.writerow({"اسم الصيدلية":"صيدلية مثال","الهاتف":"0535000000","العنوان":"خنيفرة"})
            review = Path(d) / "review.csv"
            output = Path(d) / "approved.json"
            self.assertEqual(prepare(source, review), 1)
            self.assertEqual(export(review, output), 0)
            self.assertEqual(json.loads(output.read_text()), {})
            with self.assertRaises(ValueError):
                approve(review,"صيدلية مثال","bad","https://example.org","admin")
            approve(review,"صيدلية مثال","ChIJQRPdJgArog0R5noTl876f1c",
                    "https://www.google.com/maps/","admin")
            self.assertEqual(export(review,output),1)
            self.assertIn("صيدلية مثال",json.loads(output.read_text()))

if __name__ == "__main__":
    unittest.main()
