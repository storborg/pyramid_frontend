from __future__ import absolute_import, print_function, division

import logging

import os

from .compiler import Compiler

log = logging.getLogger(__name__)


class RequireJSCompiler(Compiler):
    """
    Compile JavaScript for theme. Assumes r.js is on $PATH.
    """

    name = 'js'

    def compile(self, key, entry_point):
        main_config = self.theme.static_url_to_filesystem_path(
            self.theme.require_config_path)
        base_url = self.theme.static_url_to_filesystem_path(
            self.theme.require_base_url)

        log.debug("base_url: %r", base_url)
        log.debug("main_config: %r", main_config)

        # Path to main module relative to baseUrl (can't be absolute)
        main_js_file = self.theme.static_url_to_filesystem_path(entry_point)
        main = os.path.relpath(main_js_file, base_url)
        main = os.path.splitext(main)[0]  # Strip .js

        almond_path = \
            self.theme.static_url_to_filesystem_path('/_pfe/almond.js')
        almond_path = os.path.relpath(almond_path, base_url)
        almond_path = os.path.splitext(almond_path)[0]

        log.debug("main: %r", main)

        cmd = [
            'r.js', '-o',
            'baseUrl={0}'.format(base_url),
            'mainConfigFile={0}'.format(main_config),
            'name={0}'.format(main),
            'paths.requireLib={0}'.format(almond_path),
            'include=requireLib',
        ]

        if not self.minify:
            cmd.append('optimize=none')

        # Add RequireJS paths for theme
        for dir_ref, dir in self.theme.keyed_static_dirs:
            dir = os.path.join(dir, 'js')
            log.debug("path _%s -> %s", key, dir)
            cmd.append('paths.{}={}'.format(dir_ref, dir))

        with self.tempfile() as (fd, temp_name):
            cmd.append('out={0}'.format(temp_name))
            self.run_command(cmd)
            file_path = self.write_from_file(key, temp_name, entry_point)

        return file_path
