import os
import os.path
import pkg_resources

from unittest import TestCase

from PIL import Image

from ..images import filters

samples_dir = pkg_resources.resource_filename('pyramid_frontend.tests', 'data')


def filesize(f):
    orig_pos = f.tell()
    f.seek(0, os.SEEK_END)
    size = f.tell()
    f.seek(orig_pos)
    return size


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

    def test_png_postprocess(self):
        saver = filters.PNGSaver()
        processor = filters.PNGProcessor()
        im = Image.new("RGBA", (25, 25), (255, 0, 0))
        im.putpixel((10, 10), (0, 255, 0))

        f = saver(im)
        nm = Image.open(f)
        self.assertEqual(nm.mode, "RGBA")
        self.assertEqual(nm.getpixel((10, 10)), (0, 255, 0, 255))

        size_before = filesize(f)

        f = processor(f)
        size_after = filesize(f)

        self.assertGreater(size_after, 0)
        self.assertLessEqual(size_after, size_before)

        nm = Image.open(f)
        self.assertEqual(nm.mode, 'RGBA')
        self.assertEqual(nm.size, (25, 25))

    def test_jpeg_save(self):
        saver = filters.JPGSaver()
        im = Image.open(os.path.join(samples_dir, 'smiley-jpeg-rgb.jpg'))
        f = saver(im)

        nm = Image.open(f)
        self.assertEqual(nm.mode, "RGB")
        self.assertEqual(nm.getpixel((300, 300)), (206, 205, 1))

    def test_jpeg_save_low_quality(self):
        saver = filters.JPGSaver(quality=20)
        im = Image.open(os.path.join(samples_dir, 'smiley-jpeg-rgb.jpg'))
        f = saver(im)

        # Should be less than 20K or so.
        self.assertLess(filesize(f), 20000)

    def test_jpeg_save_alpha(self):
        saver = filters.JPGSaver(quality=95)
        im = Image.new('RGBA', (30, 30), (255, 0, 0, 0))
        rect = Image.new('RGBA', (10, 10), (0, 255, 0, 255))
        im.paste(rect, (10, 10))

        f = saver(im)
        nm = Image.open(f)
        self.assertEqual(nm.mode, 'RGB')
        self.assertEqual(nm.getpixel((15, 15)), (0, 255, 0))

    def test_jpeg_save_monochrome(self):
        saver = filters.JPGSaver(quality=95)
        im = Image.new('L', (30, 30), 255)
        rect = Image.new('L', (10, 10), 0)
        im.paste(rect, (10, 10))

        f = saver(im)
        nm = Image.open(f)
        self.assertEqual(nm.mode, 'RGB')
        self.assertEqual(nm.getpixel((15, 15)), (0, 0, 0))

    def test_jpg_postprocess(self):
        saver = filters.JPGSaver()
        processor = filters.JPGProcessor()
        im = Image.new("RGB", (25, 25), (255, 0, 0))
        im.putpixel((10, 10), (0, 255, 0))

        f = saver(im)
        size_before = filesize(f)

        f = processor(f)
        size_after = filesize(f)

        self.assertGreater(size_after, 0)
        self.assertLessEqual(size_after, size_before)

        nm = Image.open(f)
        self.assertEqual(nm.mode, 'RGB')
        self.assertEqual(nm.size, (25, 25))

    def test_vignette_filter(self):
        im = Image.open(os.path.join(samples_dir, 'smiley-jpeg-rgb.jpg'))
        filter = filters.VignetteFilter()
        saver = filters.JPGSaver()

        im = filter(im)
        f = saver(im)

        nm = Image.open(f)
        self.assertNotEqual(nm.getpixel((0, 0)), (255, 255, 255))
