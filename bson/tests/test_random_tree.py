# Copyright (c) 2010, Kou Man Tong
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of Kou Man Tong nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDERS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os
from bson import dumps, loads
from random import randint
from unittest import TestCase


def populate(parent, howmany, max_children):
#    to_add = howmany
    if howmany > max_children:
        children = randint(2, max_children)
        distribution = []
        for i in xrange(0, children - 1):
            distribution.append(int(howmany / children))
        distribution.append(howmany - sum(distribution, 0))
        for i in xrange(0, children):
            steal_target = randint(0, children - 1)
            while steal_target == i:
                steal_target = randint(0, children - 1)
            steal_count = randint(-1 * distribution[i],
                    distribution[steal_target]) / 2
            distribution[i] += steal_count
            distribution[steal_target] -= steal_count

        for i in xrange(0, children):
            make_dict = randint(0, 1)
            baby = None
            if make_dict:
                baby = {}
            else:
                baby = []
            populate(baby, distribution[i], max_children)
            if isinstance(parent, dict):
                parent[os.urandom(8).encode("hex")] = baby
            else:
                parent.append(baby)
    else:
        populate_with_leaves(parent, howmany)


def populate_with_leaves(parent, howmany):
    for i in xrange(0, howmany):
        leaf = os.urandom(4).encode("hex")
        make_unicode = randint(0, 1)
        if make_unicode:
            leaf = unicode(leaf)
        if isinstance(parent, dict):
            parent[os.urandom(4).encode("hex")] = leaf
        else:
            parent.append(leaf)


class TestRandomTree(TestCase):
    def test_random_tree(self):
        for i in xrange(0, 16):
            p = {}
            populate(p, 256, 4)
            sp = dumps(p)
            p2 = loads(sp)
            self.assertEquals(p, p2)
