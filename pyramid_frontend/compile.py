import os.path
import optparse
import sys

from pyramid.paster import bootstrap
from pyramid.scripts.common import parse_vars

from pyramid_frontend.assets.requirejs import RequireJSCompiler
from pyramid_frontend.assets.less import LessCompiler


def main(argv=sys.argv, quiet=False):
    command = PCompileCommand(argv, quiet)
    return command.run()


def compile_theme(settings, theme):
    print "Compiling theme: %s" % theme.key
    output_dir = os.path.join(
        settings['pyramid_frontend.compiled_asset_dir'],
        theme.key)
    compilers = {
        'requirejs': RequireJSCompiler(theme, output_dir),
        'less': LessCompiler(theme, output_dir),
    }
    for key, (entry_point, asset_type) in theme.stacked_assets.iteritems():
        compilers[asset_type].compile(key, entry_point)


class PCompileCommand(object):
    parser = optparse.OptionParser(
        '%prog config_uri',
        description='Compile static assets.',
    )

    stdout = sys.stdout
    bootstrap = (bootstrap,)  # testing

    def __init__(self, argv, quiet=False):
        self.quiet = quiet
        self.options, self.args = self.parser.parse_args(argv[1:])

    def compile(self, registry):
        settings = registry.settings
        theme_registry = settings['pyramid_frontend.theme_registry']
        for theme in theme_registry.itervalues():
            compile_theme(settings, theme)

    def run(self):
        if not self.args:
            self.out('Requires a config file argument')
            return 2
        config_uri = self.args[0]
        env = self.bootstrap[0](config_uri, options=parse_vars(self.args[1:]))
        registry = env['registry']
        self.compile(registry)
        return 0
