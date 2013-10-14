from unittest import TestCase

from pyramid import testing
from mako.exceptions import TopLevelLookupException

from ..templating.lookup import SuperTemplateLookup

from .example import base, foo, bar


class TestThemeLookup(TestCase):
    def test_render_foo_index(self):
        theme = foo.FooTheme()
        templ = theme.lookup.get_template('index.html')
        s = templ.render()
        self.assertIn('base theme base.html', s)
        self.assertIn('foo theme base.html', s)
        self.assertIn('base theme index.html', s)
        self.assertNotIn('bar', s)

    def test_render_foo_article(self):
        theme = foo.FooTheme()
        templ = theme.lookup.get_template('article.html')
        s = templ.render()
        self.assertIn('base theme base.html', s)
        self.assertIn('foo theme base.html', s)
        self.assertIn('foo theme article.html', s)
        self.assertNotIn('bar', s)

    def test_render_base_index(self):
        theme = base.BaseTheme()
        templ = theme.lookup.get_template('index.html')
        s = templ.render()
        self.assertIn('base theme base.html', s)
        self.assertIn('base theme index.html', s)
        self.assertNotIn('foo', s)
        self.assertNotIn('bar', s)

    def test_render_missing_template(self):
        theme = foo.FooTheme()
        with self.assertRaises(TopLevelLookupException):
            templ = theme.lookup.get_template('nonexistent-template.html')
