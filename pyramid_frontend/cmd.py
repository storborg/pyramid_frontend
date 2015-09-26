from __future__ import absolute_import, print_function, division

import logging
import time
import subprocess

log = logging.getLogger(__name__)


def run(args):
    log.debug('Running command: %s ...', ' '.join(args))
    start_time = time.time()
    try:
        subprocess.check_output(args, stderr=subprocess.STDOUT, close_fds=True)
    except subprocess.CalledProcessError as e:
        log.error("Called process error: %r", e.output)
        raise
    except OSError as e:
        log.error("OS error: %r", e)
        raise
    except Exception as e:
        log.error("Generic exception: %r", e)
        raise
    finally:
        elapsed_time = time.time() - start_time
        log.debug('Command completed in %0.4f seconds.', elapsed_time)
