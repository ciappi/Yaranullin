# yaranullin/tests/weakcallback.py
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

import unittest
import sys

if __name__ == '__main__':
    sys.path.insert(0, ".")


from yaranullin.weakcallback import WeakCallback


class Test:
    def t(self):
        return 'called'


class TestWeakCallback(unittest.TestCase):

    def test(self):
        test = Test()
        weak_t = WeakCallback(test.t)
        self.failUnlessEqual('called', weak_t()())
        weak_t2 = WeakCallback(test.t)
        self.assertIs(weak_t, weak_t2)
        del test
        self.assertIsNone(weak_t())
        self.assertRaises(TypeError, WeakCallback, 'not a function or method')


if __name__ == '__main__':
    unittest.main()
