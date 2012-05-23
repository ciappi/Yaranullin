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

import argparse
import logging

LOGGER = logging.getLogger(__name__)

from yaranullin.config import __version__, __platform__


def main():
    # Parse input arguments.
    parser = argparse.ArgumentParser(description='Launches Yaranullin')
    parser.add_argument('--debug', action='store_true',
                        help='Print debugging information')
    parser.add_argument('--version', action='version',
                        version='Yaranullin ' + __version__ + ' on ' +
                        __platform__)
    subparsers = parser.add_subparsers(dest='cmd', help='commands')
    client_parser = subparsers.add_parser('client', help='Launch the client')
    client_parser.add_argument('--host', action='store', type=str,
                        help='Specify the address of the server')
    client_parser.add_argument('--port', action='store', type=int,
                        help='Specify the port of the server')
    server_parser = subparsers.add_parser('server', help='Launch the server')
    server_parser.add_argument('--game', action='store', type=str,
                        help='Specify the game to load.')
    args = parser.parse_args()

    # Set logging level
    level = logging.INFO
    fmt = '%(levelname)s: %(message)s'
    if args.debug:
        fmt = '%(levelname)s:%(name)s:%(funcName)s() %(message)s'
        level = logging.DEBUG
    logging.basicConfig(format=fmt, level=level)
    LOGGER.debug('Starting %s...', args.cmd)

    # Import the correct runner
    if args.cmd == 'client':
        from yaranullin.run_client import run
    elif args.cmd == 'server':
        from yaranullin.run_server import run

    # Run
    try:
        run(args)
    except KeyboardInterrupt:
        pass
