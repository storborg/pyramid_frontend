from __future__ import absolute_import, print_function, division

import argparse
import sys

from pyramid.paster import bootstrap


def compile(registry, minify=True, verbose=False):
    settings = registry.settings
    theme_registry = settings['pyramid_frontend.theme_registry']
    for theme in theme_registry.itervalues():
        theme.compile(minify=minify, verbose=verbose)


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
