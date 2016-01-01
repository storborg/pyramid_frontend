from __future__ import absolute_import, print_function, division

import logging

import os

from webhelpers2.html.tags import HTML, literal

from .. import cmd
from .asset import Asset

log = logging.getLogger(__name__)


js_preamble = '''\
if (typeof console === 'undefined') {
  console = {
    log: function () {},
    debug: function () {}
  }
}
'''


def render_js_paths(theme):
    """
    Return a script tag for use client-side which sets up require.js paths for
    all theme directories in use by the supplied theme.
    """
    cls = theme.__class__
    keys = []
    while hasattr(cls, 'key'):
        keys.append(cls.key)
        cls = cls.__bases__[0]
    lines = ["require.paths.%s = '/_%s/js';" % (key, key)
             for key in keys]
    return ''.join(['<script>'] + lines + ['</script>'])


class RequireJSAsset(Asset):
    """
    Asset handler for javascript loaded by require.js.

    Currently assumes r.js is on $PATH.
    """
    extension = 'js'

    def __init__(self, url_path,
                 require_config_path='/_pfe/require_config.js',
                 require_path='/_pfe/require.js',
                 require_base_url='/_pfe/'):
        self.url_path = url_path
        self.require_config_path = require_config_path
        self.require_path = require_path
        self.require_base_url = require_base_url

    def compile(self, key, theme, output_dir, minify=True):
        main_config = theme.static_url_to_filesystem_path(
            self.require_config_path)
        base_url = theme.static_url_to_filesystem_path(
            self.require_base_url)

        log.debug("base_url: %r", base_url)
        log.debug("main_config: %r", main_config)

        # Path to main module relative to baseUrl (can't be absolute)
        main_js_file = theme.static_url_to_filesystem_path(self.url_path)
        main = os.path.relpath(main_js_file, base_url)
        main = os.path.splitext(main)[0]  # Strip .js

        almond_path = \
            theme.static_url_to_filesystem_path('/_pfe/almond.js')
        almond_path = os.path.relpath(almond_path, base_url)
        almond_path = os.path.splitext(almond_path)[0]

        log.debug("main: %r", main)

        args = [
            'r.js', '-o',
            'baseUrl={0}'.format(base_url),
            'mainConfigFile={0}'.format(main_config),
            'name={0}'.format(main),
            'paths.requireLib={0}'.format(almond_path),
            'include=requireLib',
        ]

        if not minify:
            args.append('optimize=none')

        # Add RequireJS paths for theme
        for dir_ref, dir in theme.keyed_static_dirs:
            dir = os.path.join(dir, 'js')
            log.debug("path _%s -> %s", key, dir)
            args.append('paths.{}={}'.format(dir_ref, dir))

        with self.tempfile() as (f, temp_name):
            args.append('out={0}'.format(temp_name))
            cmd.run(args)

            f.seek(0)
            contents = f.read().decode('utf8')
            contents = '\n'.join([js_preamble, contents])

            file_path = self.write(key, contents, self.url_path, output_dir)

        return file_path

    def tag_development(self, theme, url):
        """
        Return an HTML fragment to use a require.js entry point in development.
        """
        return ''.join([
            HTML.script(literal(js_preamble)),
            HTML.script(src=self.require_config_path),
            render_js_paths(theme),
            HTML.script(src=self.require_path),
            HTML.script(src=url),
        ])

    def tag_production(self, theme, url):
        """
        Return an HTML fragment to use a require.js entry point in production.
        """
        return HTML.script(src=url)
