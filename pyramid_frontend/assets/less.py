from __future__ import absolute_import, print_function, division

import os
import re

from .compiler import Compiler


class LessCompiler(Compiler):

    name = 'css'

    import_re = re.compile(r'@import[ ]+"(?P<path>.*)";')

    def compile(self, key, entry_point):
        entry_point = self.theme.static_url_to_filesystem_path(entry_point)

        lessc_flags = []
        lessc_flags.append('--verbose')
        if self.minify:
            lessc_flags.append('--compress')

        with self.tempfile() as (in_fd, in_name):
            os.write(in_fd, self.concatenate(entry_point))
            cmd = ['lessc'] + lessc_flags + [in_name]
            with self.tempfile() as (out_fd, out_name):
                cmd.append(out_name)
                self.run_command(cmd)
                file_path = self.write_from_file(key, out_name, entry_point)

        return file_path

    def concatenate(self, start_path):
        """Concatenate a file and its `@import`s, recursively."""
        err = 'File does not exist {0}'.format(start_path)
        assert os.path.isfile(start_path), err
        contents = []
        directory = os.path.dirname(start_path)
        with open(start_path) as fp:
            for line in fp:
                match = self.import_re.match(line.strip())
                if match:
                    path = match.groupdict()['path']
                    ext = os.path.splitext(path)[1]
                    if ext not in ('.css', '.less'):
                        path = '.'.join((path, 'less'))
                    if os.path.isabs(path):
                        path = self.theme.static_url_to_filesystem_path(path)
                    else:
                        path = os.path.join(directory, path)
                    contents.append(self.concatenate(path))
                else:
                    contents.append(line)
        return ''.join(contents)