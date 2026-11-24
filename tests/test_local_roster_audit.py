import csv
import tempfile
import unittest
from pathlib import Path
from scripts.audit_local_roster import audit

class LocalRosterAuditTests(unittest.TestCase):
    def make_csv(self, rows):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "private.csv"
        with path.open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=["التاريخ", "اسم الصيدلية", "الهاتف", "العنوان", "بداية الحراسة"])
            writer.writeheader()
            writer.writerows(rows)
        return path

    def test_repeated_same_pharmacy_allowed(self):
        row = {"التاريخ": "2026-09-21", "اسم الصيدلية": "صيدلية مثال",
               "الهاتف": "0535000000", "العنوان": "خنيفرة", "بداية الحراسة": "21:30"}
        rows, identities, findings = audit(self.make_csv([row, {**row, "التاريخ":"2026-10-31"}]))
        self.assertEqual(len(rows), 2)
        self.assertEqual(len(identities), 1)
        self.assertEqual(findings, [])

    def test_cross_pharmacy_number_conflict(self):
        a = {"التاريخ":"2026-09-21","اسم الصيدلية":"صيدلية أ","الهاتف":"0535000000","العنوان":"A","بداية الحراسة":"21:00"}
        b = {**a, "اسم الصيدلية":"صيدلية ب", "العنوان":"B"}
        self.assertTrue(any("Same number" in issue[2] for issue in audit(self.make_csv([a,b]))[2]))

    def test_two_phones_allowed_when_separated(self):
        a = {"التاريخ":"2026-09-21","اسم الصيدلية":"صيدلية مثال","الهاتف":"0535000000 / 0600000000","العنوان":"A","بداية الحراسة":"21:00"}
        self.assertEqual(audit(self.make_csv([a]))[2], [])

if __name__ == "__main__":
    unittest.main()
