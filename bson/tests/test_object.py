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

from bson import BSONCoding, dumps, loads, import_class
from unittest import TestCase


class TestData(BSONCoding):
    def __init__(self, *args):
        self.args = list(args)
        self.nested = None

    def bson_encode(self):
        return {"args": self.args, "nested": self.nested}

    def bson_init(self, raw_values):
        self.args = raw_values["args"]
        self.nested = raw_values["nested"]

    def __eq__(self, other):
        if not isinstance(other, TestData):
            return NotImplemented
        if self.args != other.args:
            return False
        if self.nested != other.nested:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)


class TestObjectCoding(TestCase):
    def test_codec(self):
        import_class(TestData)
        data = TestData(u"Lorem ipsum dolor sit amet",
                "consectetur adipisicing elit",
                42)

        data2 = TestData(u"She's got both hands in her pockets",
                "and she won't look at you won't look at you eh",
                66,
                23.54,
                None,
                True,
                False,
                u"Alejandro")
        data2.nested = data

        serialized = dumps(data2)
        data3 = loads(serialized)
        self.assertTrue(data2 == data3)
