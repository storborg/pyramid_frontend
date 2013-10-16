import os.path
import optparse
import sys

from pyramid.paster import bootstrap
from pyramid.scripts.common import parse_vars

from pyramid_frontend.assets.requirejs import RequireJSCompiler
from pyramid_frontend.assets.less import LessCompiler


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


def compile(registry):
    settings = registry.settings
    theme_registry = settings['pyramid_frontend.theme_registry']
    for theme in theme_registry.itervalues():
        compile_theme(settings, theme)


def main(argv=sys.argv, quiet=False):
    parser = optparse.OptionParser(
        '%prog config_uri',
        description='Compile static assets.',
    )

    options, args = parser.parse_args(argv[1:])

    if not args:
        print "Requires a config file argument"
        return 2
    config_uri = args[0]
    env = bootstrap(config_uri, options=parse_vars(args[1:]))
    registry = env['registry']
    compile(registry)
    return 0
