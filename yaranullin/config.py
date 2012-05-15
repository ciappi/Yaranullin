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
import platform


# Global information
__version__ = '0.5.0'
__platform__ = platform.system()

# Check home folder
if 'HOME' not in os.environ:
    if __platform__ == 'Windows':
        HOME_DIR = os.path.join(os.environ['HOMEDRIVE'], os.environ['HOMEPATH'])
    else:
        sys.exit('Cannot find home folder')
else:
    HOME_DIR = os.environ['HOME']
YR_DIR = os.path.join(HOME_DIR, '.yaranullin')
# Define resources and saves folders.
YR_RES_DIR = os.path.join(YR_DIR, 'resources')
YR_CACHE_DIR = os.path.join(YR_RES_DIR, 'cache')
YR_SAVE_DIR = os.path.join(YR_DIR, 'saves')
for folder in (YR_RES_DIR, YR_CACHE_DIR, YR_SAVE_DIR):
    try:
        os.makedirs(folder)
    except OSError:
        pass
# Installed config file.
MAIN_CONFIG_FILE = os.path.join(sys.prefix, 'share', 'yaranullin',
                                'yaranullin.ini')
# If there is no installed config file, we assume to be in the source folder.
if not os.path.exists(MAIN_CONFIG_FILE):
    MAIN_CONFIG_FILE = os.path.join(os.path.split(\
                       os.path.dirname(__file__))[0], 'data', 'yaranullin.ini')

# User provided config file
USER_CONFIG_FILE = os.path.join(YR_DIR, 'yaranullin.ini')

# Colors to use for pawns. XXX this is not their place...
COLORS = ['red', 'violetred', 'gold', 'maroon', 'turquoise', 'green',
          'forestgreen', 'darkseagreen', 'dodgerblue3']

# Log related stuff.
LOG_FILE_CLIENT = os.path.join(YR_DIR, 'client.log')
LOG_FILE_SERVER = os.path.join(YR_DIR, 'server.log')
LOG_FILE_EDITOR = os.path.join(YR_DIR, 'editor.log')
LOG_LEVEL = 'DEBUG'

# Create a global configuration object and use args to update configuration
CONFIG = ConfigParser.RawConfigParser(allow_no_value=True)
# check if this file exists, otherwise exit.
try:
    CONFIG.readfp(open(MAIN_CONFIG_FILE))
except:
    sys.exit('Cannot find the main configuration file')
# If the user has a custom config file, read it.
CONFIG.read(USER_CONFIG_FILE)
