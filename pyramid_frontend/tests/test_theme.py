from unittest import TestCase

from pyramid_frontend.theme import Theme


class TestTheme(TestCase):
    def test_traverse_attributes(self):
        class A(Theme):
            key = 'a'
            template_dir = 'a-templates'

        class B(A):
            key = 'b'
            pass

        class C(B):
            key = 'c'
            template_dir = 'c-templates'

        self.assertEqual(list(C.traverse_attributes('template_dir')),
                         [('c', 'c-templates'),
                          ('b', 'a-templates'),
                          ('a', 'a-templates')])
