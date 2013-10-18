from unittest import TestCase

from .. import compile

from . import utils



class TestCompileCommand(TestCase):

    def test_pcompile_usage(self):
        args = [
            'pcompile',
        ]
        return_code = compile.main(args)
        self.assertEqual(return_code, 2)

    def test_pcompile(self):
        retcode = utils.compile_assets()
        self.assertEqual(retcode, 0)
