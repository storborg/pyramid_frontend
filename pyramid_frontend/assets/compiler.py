from __future__ import absolute_import, print_function, division

import os
import tempfile
import time
import subprocess

from contextlib import contextmanager
from hashlib import sha1


class Compiler(object):

    def __init__(self, theme, output_dir, minify=True, verbose=False):
        self.theme = theme
        self.output_dir = output_dir
        self.minify = minify
        self.verbose = verbose

    def run_command(self, argv):
        if self.verbose:
            print('Running command: {0} ...'.format(' '.join(argv)))
        start_time = time.time()
        try:
            subprocess.check_output(argv, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            print(e.output)
            raise
        elapsed_time = time.time() - start_time
        if self.verbose:
            print('Command completed in {:.4f} seconds.'.format(elapsed_time))

    def write(self, key, contents, entry_point):
        if self.verbose:
            print('Write - key: %r, entry_point: %r' % (key, entry_point))
        hash = sha1(contents).hexdigest()

        name = os.path.basename(entry_point)
        file_name = '{name}-{hash}.{ext}'.format(
            name=name, hash=hash, ext=self.name)
        file_path = os.path.join(self.output_dir, file_name)

        if not os.path.isdir(self.output_dir):
            os.makedirs(self.output_dir)

        if self.verbose:
            print('Writing to {0} ...'.format(file_path))
        with open(file_path, 'wb') as f:
            f.write(contents)

        map_path = os.path.join(self.output_dir, key + '.map')
        if self.verbose:
            print('Writing map file to {0} ...'.format(map_path))
        with open(map_path, 'w') as f:
            f.write(file_name)

        return file_path

    def write_from_file(self, key, file_name, entry_point):
        with open(file_name) as f:
            contents = f.read()
        return self.write(key, contents, entry_point)

    @contextmanager
    def tempfile(self, *args, **kwargs):
        fd, name = tempfile.mkstemp(*args, **kwargs)
        try:
            yield fd, name
        finally:
            os.close(fd)
            os.remove(name)
