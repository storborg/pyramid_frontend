#from __future__ import absolute_import, print_function, division

import os

from .compiler import Compiler


class RequireJSCompiler(Compiler):
    """
    Compile JavaScript for theme. Assumes r.js is on $PATH.
    """

    name = 'js'

    def compile(self, key, entry_point):
        base_url = self.theme.static_url_to_filesystem_path('/_pfe/')
        main_config = self.theme.static_url_to_filesystem_path(
            self.theme.require_config_path)

        print "requirejs - base_url: %r" % base_url
        print "requirejs - main_config: %r" % main_config

        # Path to main module relative to baseUrl (can't be absolute)
        main_js_file = self.theme.static_url_to_filesystem_path(entry_point)
        main = os.path.relpath(main_js_file, base_url)
        main = os.path.splitext(main)[0]  # Strip .js

        print "requirejs - main: %r" % main

        cmd = [
            'r.js', '-o',
            'baseUrl={0}'.format(base_url),
            'mainConfigFile={0}'.format(main_config),
            'name={0}'.format(main),
            'paths.requireLib=almond',
            'include=requireLib',
        ]

        if not self.minify:
            cmd.append('optimize=none')

        # Add RequireJS paths for theme
        for dir_ref, dir in self.theme.keyed_static_dirs:
            print "requirejs - path _%s - %s" % (key, dir)
            cmd.append('paths._{}={}'.format(dir_ref, dir))

        with self.tempfile() as (fd, temp_name):
            cmd.append('out={0}'.format(temp_name))
            self.run_command(cmd)
            file_path = self.write_from_file(key, temp_name, entry_point)

        return file_path
