# setup.py
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


from distutils.core import setup
import os

from yaranullin.config import __version__


setup(
    name='Yaranullin',
    version=__version__,
    author='Marco Scopesi',
    author_email='marco.scopesi@gmail.com',
    maintainer='Marco Scopesi',
    maintainer_email='marco.scopesi@gmail.com',
    url='https://github.com/ciappi/yaranullin',
    license='BSD',
    description='Interactive map for role-playing games',
    long_description="""\
A piece of software that helps role players to track the position of their
heroes when fighting against monsters and other scary things, such as
skeletons and other derivatives.""",
    packages=['yaranullin', 'yaranullin.game', 'yaranullin.gui',
              'yaranullin.network', 'yaranullin.pygame'],
    data_files=[(os.path.join('share', 'yaranullin'),
               [os.path.join('data', 'yaranullin.ini'), ])],
    scripts=[os.path.join('bin', 'yaranullin')]
)
