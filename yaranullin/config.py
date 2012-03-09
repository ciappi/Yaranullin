# yaranullin/config.py
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

"""Global configuration."""

import os
import sys
import ConfigParser

# Global version.
__version__ = '0.1.0'

HOME_DIR = os.environ['HOME']
YR_DIR = os.path.join(HOME_DIR, '.yaranullin')
# If YR_DIR do not exist, we are in the source folder.
if not os.path.exists(YR_DIR):
    this_dir = os.path.split(os.path.dirname(__file__))[0]
    YR_DIR = os.path.join(this_dir, 'data')
# Define resources and saves folders.
YR_RES_DIR = os.path.join(YR_DIR, 'resources')
YR_CACHE_DIR = os.path.join(YR_RES_DIR, 'cache')
YR_SAVE_DIR = os.path.join(YR_DIR, 'saves')
# Installed config file.
MAIN_CONFIG_FILE = os.path.join(sys.prefix, 'share', 'yaranullin',
                                'yaranullin.ini')
# If there is no installed config file, we are in the source folder.
if not os.path.exists(MAIN_CONFIG_FILE):
    MAIN_CONFIG_FILE = os.path.join(os.path.split(\
                       os.path.dirname(__file__))[0], 'data', 'yaranullin.ini')

# Colors to use for pawns.
COLORS = ['red', 'violetred', 'gold', 'maroon', 'turquoise', 'green',
          'forestgreen', 'darkseagreen', 'dodgerblue3']

# Log related stuff.
LOG_FILE_CLIENT = os.path.join(YR_DIR, 'client.log')
LOG_FILE_SERVER = os.path.join(YR_DIR, 'server.log')
LOG_LEVEL = 'DEBUG'

# Create a global configuration object and use args to update configuration
_conf = ConfigParser.RawConfigParser(allow_no_value=True)
# TODO: check if this file exists, otherwise provide a default one.
_conf.readfp(open(MAIN_CONFIG_FILE))
# If the user has a custom 'yaranullin.ini' file, read it.
_conf.read(os.path.join(YR_DIR, 'yaranullin.ini'))
CONFIG = _conf
