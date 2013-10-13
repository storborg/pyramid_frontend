import os.path
import pkg_resources

from unittest import TestCase

from PIL import Image

from ..images import utils, filters

samples_dir = pkg_resources.resource_filename('pyramid_frontend.tests', 'data')


class TestUtils(TestCase):
    def setUp(self):
        self.im = Image.open(os.path.join(samples_dir, 'smiley-jpeg-rgb.jpg'))

    def test_bounding_box(self):
        self.assertEqual(utils.bounding_box(self.im), (8, 16, 496, 504))


class TestFilters(TestCase):
    def test_png_save_rgb(self):
        saver = filters.PNGSaver(palette=True)
        im = Image.new("RGB", (25, 25), "red")
        f = saver(im)

        nm = Image.open(f)
        self.assertEqual(nm.mode, "P")
        nm = nm.convert("RGBA")
        self.assertEqual(nm.getpixel((8, 8)), (255, 0, 0, 255))

    def test_png_save_palette(self):
        saver = filters.PNGSaver(palette=True)
        im = Image.new("P", (25, 25))
        im.putpalette([0] * 768)
        im.paste(23, (0, 0, 25, 25))
        f = saver(im)

        nm = Image.open(f)
        self.assertEqual(nm.mode, "P")
        self.assertEqual(nm.getpixel((8, 8)), 23)
