import os
import os.path
import shutil
import pkg_resources

from unittest import TestCase

from PIL import Image

from ..images.chain import FilterChain, PassThroughFilterChain

from . import utils

samples_dir = pkg_resources.resource_filename('pyramid_frontend.tests', 'data')


class TestFilterChain(TestCase):
    work_dir = os.path.join(utils.work_dir, 'filter-chain-tests')
    test_files = ['smiley-jpeg-rgb.jpg',
                  'smiley-png24-alpha.png',
                  'smiley-gif-alpha.gif',
                  'smiley-jpeg-cmyk.jpg']

    def setUp(self):
        if os.path.exists(self.work_dir):
            shutil.rmtree(self.work_dir)
        os.makedirs(self.work_dir)

    def test_basename(self):
        chain = FilterChain('thumb200', extension='png')
        self.assertEqual(chain.basename('some-cool-image', 'jpg'),
                         'some-cool-image_jpg_thumb200.png')
        self.assertEqual(chain.basename('delicious', 'gif'),
                         'delicious_gif_thumb200.png')

    def test_basename_passthrough(self):
        chain = PassThroughFilterChain()
        self.assertEqual(chain.basename('some-cool-image', 'jpg'),
                         'some-cool-image.jpg')
        self.assertEqual(chain.basename('delicious', 'gif'),
                         'delicious.gif')

    def _process(self, chain, filename):
        orig_path = os.path.join(samples_dir, filename)
        image_data = open(orig_path, 'rb')
        proc_path = os.path.join(self.work_dir, filename)
        chain.run(proc_path, image_data)

        im = Image.open(proc_path)
        return im

    def test_chain_basic(self):
        chain = FilterChain('thumb50', extension='png',
                            width=50, height=50)
        for filename in self.test_files:
            im = self._process(chain, filename)
            self.assertEqual(im.size, (50, 50))

    def test_chain_passthrough_jpeg(self):
        chain = PassThroughFilterChain()
        for filename in self.test_files:
            im = self._process(chain, filename)
            self.assertEqual(im.size, (512, 512))

    def test_run_missing_output_dir(self):
        chain = FilterChain('thumb50', extension='png',
                            width=50, height=50)
        filename = self.test_files[0]
        orig_path = os.path.join(samples_dir, filename)
        image_data = open(orig_path, 'rb')
        proc_path = os.path.join(self.work_dir, 'blah', filename)
        chain.run(proc_path, image_data)
        im = Image.open(proc_path)
        self.assertEqual(im.size, (50, 50))

    def test_run_no_thumb(self):
        chain = FilterChain('thumbless', extension='png', no_thumb=True)
        im = self._process(chain, self.test_files[0])
        self.assertEqual(im.size, (512, 512))
