from __future__ import absolute_import, print_function, division

import os.path
import argparse
import sys

from pyramid.paster import bootstrap

from pyramid_frontend.assets.requirejs import RequireJSCompiler
from pyramid_frontend.assets.less import LessCompiler


def compile_theme(settings, theme, minify=True, verbose=False):
    if verbose:
        print("Compiling theme: %s" % theme.key)
    output_dir = os.path.join(
        settings['pyramid_frontend.compiled_asset_dir'],
        theme.key)
    compilers = {
        'requirejs': RequireJSCompiler,
        'less': LessCompiler,
    }
    for key, (entry_point, asset_type) in theme.stacked_assets.iteritems():
        cls = compilers[asset_type]
        compiler = cls(theme, output_dir, minify=minify, verbose=verbose)
        compiler.compile(key, entry_point)


def compile(registry, minify=True, verbose=False):
    settings = registry.settings
    theme_registry = settings['pyramid_frontend.theme_registry']
    for theme in theme_registry.itervalues():
        compile_theme(settings, theme, minify=minify, verbose=verbose)


def main(args=sys.argv):
    parser = argparse.ArgumentParser(description='Compile static assets.')
    parser.add_argument('--no-minify', action='store_true', default=False)
    parser.add_argument('--verbose', action='store_true', default=False)
    parser.add_argument('config_uri')

    options = parser.parse_args(args[1:])

    env = bootstrap(options.config_uri)
    registry = env['registry']
    compile(registry, minify=(not options.no_minify), verbose=options.verbose)
    return 0
