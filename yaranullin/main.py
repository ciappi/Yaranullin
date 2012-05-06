# yaranullin/main.py
#
# Copyright (c) 2012 Marco Scopesi <marco.scopesi@gmail.com>
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

''' Main module '''

import traceback
import sys

from yaranullin.main_server import ServerRunner


def import_client_runner():
    ''' Lazy import client runner '''
    try:
        from yaranullin.main_client import ClientRunner
    except ImportError:
        traceback.print_exc(file=sys.stderr)
        sys.stderr.write('ERROR: Cannot import ClientRunner: %s\n' %
                         'is pygame installed?')
        return None
    else:
        return ClientRunner


def main(args):
    ''' Main function '''

    runner = None
    mode = args.mode
    if mode == 'server':
        runner = ServerRunner(args)
    elif mode == 'client':
        client_runner_class = import_client_runner()
        if client_runner_class:
            runner = client_runner_class(args)
    if runner:
        runner.run()
