import json, unittest, collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class TestCurriculum(unittest.TestCase):
 @classmethod
 def setUpClass(cls): cls.data=json.loads((ROOT/'curriculum.json').read_text(encoding='utf8'))
 def test_four_worlds(self): self.assertEqual(len(self.data['worlds']),4)
 def test_every_level_has_content_and_multiple_questions(self):
  counts=collections.Counter(q['level'] for q in self.data['questions'])
  self.assertGreaterEqual(len(self.data['levels']),25)
  for level in self.data['levels']:
   self.assertTrue(level['lesson'] and level['example'] and level['recap'] and level['objective'])
   self.assertGreaterEqual(counts[level['id']],4,level['id'])
 def test_answer_keys_are_valid_and_options_unique(self):
  for q in self.data['questions']:
   self.assertTrue(0<=q['a']<len(q['opts']),q['id'])
   self.assertEqual(len(q['opts']),len(set(q['opts'])),q['id'])
 def test_known_calculation_answer_keys(self):
  q={x['id']:x for x in self.data['questions']}
  self.assertEqual(q['bilangan-3-v1']['opts'][q['bilangan-3-v1']['a']],'10')
  self.assertEqual(q['bilangan-8-q2']['opts'][q['bilangan-8-q2']['a']],'5,6 × 10⁻⁴')
  self.assertEqual(q['aljabar-9-q1']['opts'][q['aljabar-9-q1']['a']],'30')
 def test_operation_lesson_example_differs_from_practice(self):
  level=next(x for x in self.data['levels'] if x['id']=='bilangan-3')
  pool=[q for q in self.data['questions'] if q['level']=='bilangan-3']
  self.assertNotIn('Hasil 18 − 2 × 5 adalah ...',[q['q'] for q in pool])
  self.assertTrue(all(q['q']!='18 − 2 × 5' for q in pool))
  self.assertGreaterEqual(len(pool),4)
  q=next(x for x in pool if x['id']=='bilangan-3-q5')
  self.assertEqual(q['opts'][q['a']],'29')
 def test_accessory_rendering_uses_nine_image_variants(self):
  folder=ROOT/'static'/'numi'
  for item in ('none','cap','crown','glasses','halo','bow','scarf','antenna','flower'):
   self.assertTrue((folder/f'{item}.png').is_file())
  js=(ROOT/'static/app.js').read_text(encoding='utf8')
  self.assertIn('src="numi/${equipped}.png"',js)
  self.assertIn('src="numi/${a.id}.png"',js)

if __name__=='__main__': unittest.main()
