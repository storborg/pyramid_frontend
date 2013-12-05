from __future__ import absolute_import, print_function, division

import logging

import os
import tempfile
import time
import subprocess

from contextlib import contextmanager
from hashlib import sha1

log = logging.getLogger(__name__)


class Compiler(object):

    def __init__(self, theme, output_dir, minify=True):
        self.theme = theme
        self.output_dir = output_dir
        self.minify = minify

    def run_command(self, argv):
        log.debug('Running command: %s ...', ' '.join(argv))
        start_time = time.time()
        try:
            subprocess.check_output(argv, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            log.error(e.output)
            raise
        elapsed_time = time.time() - start_time
        log.debug('Command completed in %0.4f seconds.', elapsed_time)

    def write(self, key, contents, entry_point):
        log.debug('Write - key: %r, entry_point: %r', key, entry_point)
        hash = sha1(contents).hexdigest()

        name = os.path.basename(entry_point)
        file_name = '{name}-{hash}.{ext}'.format(
            name=name, hash=hash, ext=self.name)
        file_path = os.path.join(self.output_dir, file_name)

        if not os.path.isdir(self.output_dir):
            os.makedirs(self.output_dir)

        log.debug('Writing to %s ...', file_path)
        with open(file_path, 'wb') as f:
            f.write(contents)

        map_path = os.path.join(self.output_dir, key + '.map')
        log.debug('Writing map file to %s ...', map_path)
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
