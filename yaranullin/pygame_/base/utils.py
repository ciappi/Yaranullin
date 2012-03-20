# yaranullin/pygame_/base/utils.py
#
# Copyright (c) 2011 Marco Scopesi <marco.scopesi@gmail.com>
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

import pygame


def sign(x):
    if x > 0:
        return 1
    elif x == 0:
        return 0
    else:
        return -1


def saturation(x, low=None, high=None):
    if (low is not None and x < low):
        return low
    elif (high is not None and x > high):
        return high
    else:
        return x


def load_image(f, size, alpha=False):
    surf = pygame.image.load(f)
#    size = surf.get_size()
#    ratio = size[0] / float(size[1])
#    if ratio >= 1:
#        size = tw, int(tw / float(size[0]) * size[1])
#    else:
#        size = int(tw / float(size[1]) * size[0]), tw
    surf = pygame.transform.smoothscale(surf, size)
    if alpha:
        surf = surf.convert_alpha()
    else:
        surf = surf.convert()
    return surf
