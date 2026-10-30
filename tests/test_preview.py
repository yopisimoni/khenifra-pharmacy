import sys, unittest, base64, os
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'api'))
from night import get_duty
class PreviewTests(unittest.TestCase):
 def test_without_schedule(self):
  old=os.environ.pop('NIGHT_SCHEDULE_CSV_B64',None)
  try:self.assertIsNone(get_duty())
  finally:
   if old is not None:os.environ['NIGHT_SCHEDULE_CSV_B64']=old
 def test_private_schedule(self):
  sample='التاريخ,اسم الصيدلية,الهاتف,العنوان,بداية الحراسة,نهاية الحراسة (صباح اليوم التالي)\n2026-10-29,صيدلية الفتح,0535382552,خنيفرة,21:00,09:00\n'
  old=os.environ.get('NIGHT_SCHEDULE_CSV_B64')
  os.environ['NIGHT_SCHEDULE_CSV_B64']=base64.b64encode(sample.encode()).decode()
  try:
   p=get_duty(datetime(2026,10,29,23,0,tzinfo=ZoneInfo('Africa/Casablanca')))
   self.assertEqual(p['nameAr'],'صيدلية الفتح')
   self.assertEqual(len(p),11)
   self.assertIsNone(get_duty(datetime(2026,12,1,23,0,tzinfo=ZoneInfo('Africa/Casablanca'))))
  finally:
   if old is None:os.environ.pop('NIGHT_SCHEDULE_CSV_B64',None)
   else:os.environ['NIGHT_SCHEDULE_CSV_B64']=old
if __name__=='__main__':unittest.main()
