from unittest import TestCase

from mako.exceptions import TopLevelLookupException

from ..templating.lookup import SuperTemplateLookup

from .example import base, foo


class TestThemeLookup(TestCase):
    settings = {
        'pyramid_frontend.compiled_asset_dir': '.'
    }

    def test_render_foo_index(self):
        theme = foo.FooTheme(self.settings)
        templ = theme.lookup.get_template('index.html')
        s = templ.render()
        self.assertIn('base theme base.html', s)
        self.assertIn('foo theme base.html', s)
        self.assertIn('base theme index.html', s)
        self.assertNotIn('bar', s)

    def test_render_foo_article(self):
        theme = foo.FooTheme(self.settings)
        templ = theme.lookup.get_template('article.html')
        s = templ.render()
        self.assertIn('base theme base.html', s)
        self.assertIn('foo theme base.html', s)
        self.assertIn('foo theme article.html', s)
        self.assertNotIn('bar', s)

    def test_render_base_index(self):
        theme = base.BaseTheme(self.settings)
        templ = theme.lookup.get_template('index.html')
        s = templ.render()
        self.assertIn('base theme base.html', s)
        self.assertIn('base theme index.html', s)
        self.assertNotIn('foo', s)
        self.assertNotIn('bar', s)

    def test_render_missing_template(self):
        theme = foo.FooTheme(self.settings)
        with self.assertRaises(TopLevelLookupException):
            theme.lookup.get_template('nonexistent-template.html')


class TestLookupOptions(TestCase):
    def test_filesystem_checks(self):
        # XXX Fill this in
        dirs = []
        SuperTemplateLookup(directories=dirs,
                            filesystem_checks=True)
