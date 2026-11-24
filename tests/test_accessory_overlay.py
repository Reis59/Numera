import unittest
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ITEMS = ('none', 'cap', 'crown', 'glasses', 'halo', 'bow', 'scarf', 'antenna', 'flower')

class NumiIllustrationTests(unittest.TestCase):
    def test_all_nine_finished_illustrations_exist_and_are_transparent(self):
        folder = ROOT / 'static' / 'numi'
        for item in ITEMS:
            with self.subTest(item=item):
                path = folder / f'{item}.png'
                self.assertTrue(path.is_file(), f'Missing {path.name}')
                image = Image.open(path).convert('RGBA')
                self.assertEqual(image.size, (512, 512))
                alpha = image.getchannel('A')
                self.assertLess(alpha.getextrema()[0], 10)
                self.assertGreater(alpha.getextrema()[1], 200)

    def test_app_uses_complete_character_images_not_emoji_overlays(self):
        js = (ROOT / 'static' / 'app.js').read_text(encoding='utf-8')
        html = (ROOT / 'static' / 'index.html').read_text(encoding='utf-8')
        self.assertIn('src="numi/${equipped}.png"', js)
        self.assertIn("img.src='numi/'+equipped+'.png'", js)
        self.assertIn('src="numi/none.png"', html)
        self.assertNotIn('sideWear', html)
        self.assertIn('src="numi/${a.id}.png"', js)

    def test_illustrations_have_visible_responsive_layout(self):
        css = (ROOT / 'static' / 'style.css').read_text(encoding='utf-8')
        self.assertIn('.mascot-stage>.numi-art{display:block;width:100%;height:100%;object-fit:contain', css)
        self.assertIn('.numi-stage>.numi-art{display:block;width:100%;height:100%;object-fit:contain', css)
        self.assertIn('.accessory-preview img{width:106px;height:106px;object-fit:contain', css)
        self.assertIn('.mascot-stage{display:inline-block!important;width:86px;height:86px}', css)

if __name__ == '__main__':
    unittest.main()
