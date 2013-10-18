import pkg_resources

from unittest import TestCase

from .. import compile


test_ini_path = pkg_resources.resource_filename('pyramid_frontend.tests',
                                                'test.ini')


class TestCompileCommand(TestCase):

    def test_pcompile_usage(self):
        args = [
            'pcompile',
        ]
        return_code = compile.main(args)
        self.assertEqual(return_code, 2)

    def test_pcompile(self):
        args = [
            'pcompile',
            test_ini_path,
        ]
        return_code = compile.main(args)
        self.assertEqual(return_code, 0)
