from unittest import TestCase
from cStringIO import StringIO

from webtest import TestApp
from pyramid.mako_templating import MakoRenderingException

from PIL import Image

from .app import make_app


class TestTemplatingFunctional(TestCase):
    def setUp(self):
        self.app = TestApp(make_app())

    def test_render_index(self):
        resp = self.app.get('/')
        resp.mustcontain('base theme base.html')
        resp.mustcontain('foo theme base.html')
        resp.mustcontain('base theme index.html')

    def test_render_bad_return(self):
        with self.assertRaises(ValueError):
            self.app.get('/bad-return')

    def test_render_bad_template(self):
        with self.assertRaises(MakoRenderingException):
            self.app.get('/bad-template')


class TestImagesFunctional(TestCase):
    def setUp(self):
        self.app = TestApp(make_app())

    def test_fetch_image(self):
        url_resp = self.app.get('/image-url')
        img_resp = self.app.get(url_resp.body)
        # This image should be 200x200
        f = StringIO(img_resp.body)
        im = Image.open(f)
        self.assertEqual(im.size, (200, 200))
