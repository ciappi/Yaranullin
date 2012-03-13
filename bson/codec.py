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

"""Base codec functions for bson."""

import struct
import cStringIO
from abc import ABCMeta, abstractmethod


class MissingClassDefinition(ValueError):
    def __init__(self, class_name):
        super(MissingClassDefinition, self).__init__(
        "No class definition for class %s" % (class_name,))


class TraversalStep(object):
    def __init__(self, parent, key):
        self.parent = parent
        self.key = key


class BSONCoding(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def bson_encode(self):
        pass

    @abstractmethod
    def bson_init(self, raw_values):
        pass

classes = {}


def import_class(cls):
    if not issubclass(cls, BSONCoding):
        return

    global classes
    classes[cls.__name__] = cls


def import_classes(*args):
    for cls in args:
        import_class(cls)


def import_classes_from_modules(*args):
    for module in args:
        for item in module.__dict__:
            if hasattr(item, "__new__") and hasattr(item, "__name__"):
                import_class(item)


def encode_object(obj, traversal_stack, generator_func):
    values = obj.bson_encode()
    class_name = obj.__class__.__name__
    values["$$__CLASS_NAME__$$"] = class_name
    return encode_document(values, traversal_stack, obj, generator_func)


def encode_object_element(name, value, traversal_stack, generator_func):
    return "\x03" + encode_cstring(name) + \
            encode_object(value, traversal_stack,
                    generator_func=generator_func)


class _EmptyClass(object):
    pass


def decode_object(raw_values):
    global classes
    class_name = raw_values["$$__CLASS_NAME__$$"]
    cls = None
    try:
        cls = classes[class_name]
    except KeyError:
        raise MissingClassDefinition(class_name)

    retval = _EmptyClass()
    retval.__class__ = cls
    alt_retval = retval.bson_init(raw_values)
    return alt_retval or retval


def encode_string(value):
    value = value.encode("utf8")
    length = len(value)
    return struct.pack("<i%dsb" % (length,), length + 1, value, 0)


def decode_string(data, base):
    length = struct.unpack("<i", data[base:base + 4])[0]
    value = data[base + 4: base + 4 + length - 1]
    value = value.decode("utf8")
    return (base + 4 + length, value)


def encode_cstring(value):
    if isinstance(value, unicode):
        value = value.encode("utf8")
    return value + "\x00"


def decode_cstring(data, base):
    length = 0
    max_length = len(data) - base
    while length < max_length:
        character = data[base + length]
        length += 1
        if character == "\x00":
            break
    return (base + length, data[base:base + length - 1].decode("utf8"))


def encode_binary(value):
    length = len(value)
    return struct.pack("<ib", length, 0) + value


def decode_binary(data, base):
    length, binary_type = struct.unpack("<ib", data[base:base + 5])
    return (base + 5 + length, data[base + 5:base + 5 + length])


def encode_double(value):
    return struct.pack("<d", value)


def decode_double(data, base):
    return (base + 8, struct.unpack("<d", data[base: base + 8])[0])


ELEMENT_TYPES = {
    0x01: "double",
    0x02: "string",
    0x03: "document",
    0x04: "array",
    0x05: "binary",
    0x08: "boolean",
    0x0A: "none",
    0x10: "int32",
    0x12: "int64"
}


def encode_double_element(name, value):
    return "\x01" + encode_cstring(name) + encode_double(value)


def decode_double_element(data, base):
    base, name = decode_cstring(data, base + 1)
    base, value = decode_double(data, base)
    return (base, name, value)


def encode_string_element(name, value):
    return "\x02" + encode_cstring(name) + encode_string(value)


def decode_string_element(data, base):
    base, name = decode_cstring(data, base + 1)
    base, value = decode_string(data, base)
    return (base, name, value)


def encode_value(name, value, buf, traversal_stack, generator_func):
    if isinstance(value, BSONCoding):
        buf.write(encode_object_element(name, value, traversal_stack,
            generator_func))
    elif isinstance(value, float):
        buf.write(encode_double_element(name, value))
    elif isinstance(value, unicode):
        buf.write(encode_string_element(name, value))
    elif isinstance(value, dict):
        buf.write(encode_document_element(name, value,
            traversal_stack, generator_func))
    elif isinstance(value, list) or isinstance(value, tuple):
        buf.write(encode_array_element(name, value,
            traversal_stack, generator_func))
    elif isinstance(value, str):
        buf.write(encode_binary_element(name, value))
    elif isinstance(value, bool):
        buf.write(encode_boolean_element(name, value))
    elif value is None:
        buf.write(encode_none_element(name, value))
    elif isinstance(value, int):
        if value < -0x80000000 or value > 0x7fffffff:
            buf.write(encode_int64_element(name, value))
        else:
            buf.write(encode_int32_element(name, value))
    elif isinstance(value, long):
        buf.write(encode_int64_element(name, value))


def encode_document(obj, traversal_stack, traversal_parent=None,
                    generator_func=None):
    buf = cStringIO.StringIO()
    key_iter = obj.iterkeys()
    if generator_func is not None:
        key_iter = generator_func(obj, traversal_stack)
    for name in key_iter:
        value = obj[name]
        traversal_stack.append(TraversalStep(traversal_parent or obj, name))
        encode_value(name, value, buf, traversal_stack, generator_func)
        traversal_stack.pop()
    e_list = buf.getvalue()
    e_list_length = len(e_list)
    return struct.pack("<i%dsb" % (e_list_length,), e_list_length + 4 + 1,
            e_list, 0)


def encode_array(array, traversal_stack, traversal_parent=None,
                 generator_func=None):
    buf = cStringIO.StringIO()
    for i in xrange(0, len(array)):
        value = array[i]
        traversal_stack.append(TraversalStep(traversal_parent or array, i))
        encode_value(unicode(i), value, buf, traversal_stack, generator_func)
        traversal_stack.pop()
    e_list = buf.getvalue()
    e_list_length = len(e_list)
    return struct.pack("<i%dsb" % (e_list_length,), e_list_length + 4 + 1,
            e_list, 0)


def decode_element(data, base):
    element_type = struct.unpack("<b", data[base:base + 1])[0]
    element_description = ELEMENT_TYPES[element_type]
    decode_func = globals()["decode_" + element_description + "_element"]
    return decode_func(data, base)


def decode_document(data, base):
    length = struct.unpack("<i", data[base:base + 4])[0]
    end_point = base + length
    base += 4
    retval = {}
    while base < end_point - 1:
        base, name, value = decode_element(data, base)
        retval[name] = value
    if "$$__CLASS_NAME__$$" in retval:
        retval = decode_object(retval)
    return (end_point, retval)


def encode_document_element(name, value, traversal_stack, generator_func):
    return "\x03" + encode_cstring(name) + \
            encode_document(value, traversal_stack,
                    generator_func=generator_func)


def decode_document_element(data, base):
    base, name = decode_cstring(data, base + 1)
    base, value = decode_document(data, base)
    return (base, name, value)


def encode_array_element(name, value, traversal_stack, generator_func):
    return "\x04" + encode_cstring(name) + \
            encode_array(value, traversal_stack, generator_func=generator_func)


def decode_array_element(data, base):
    base, name = decode_cstring(data, base + 1)
    base, value = decode_document(data, base)
    retval = []
    try:
        i = 0
        while True:
            retval.append(value[unicode(i)])
            i += 1
    except KeyError:
        pass
    return (base, name, retval)


def encode_binary_element(name, value):
    return "\x05" + encode_cstring(name) + encode_binary(value)


def decode_binary_element(data, base):
    base, name = decode_cstring(data, base + 1)
    base, value = decode_binary(data, base)
    return (base, name, value)


def encode_boolean_element(name, value):
    return "\x08" + encode_cstring(name) + struct.pack("<b", value)


def decode_boolean_element(data, base):
    base, name = decode_cstring(data, base + 1)
    value = not not struct.unpack("<b", data[base:base + 1])[0]
    return (base + 1, name, value)


def encode_none_element(name, value):
    return "\x0a" + encode_cstring(name)


def decode_none_element(data, base):
    base, name = decode_cstring(data, base + 1)
    return (base, name, None)


def encode_int32_element(name, value):
    return "\x10" + encode_cstring(name) + struct.pack("<i", value)


def decode_int32_element(data, base):
    base, name = decode_cstring(data, base + 1)
    value = struct.unpack("<i", data[base:base + 4])[0]
    return (base + 4, name, value)


def encode_int64_element(name, value):
    return "\x12" + encode_cstring(name) + struct.pack("<q", value)


def decode_int64_element(data, base):
    base, name = decode_cstring(data, base + 1)
    value = struct.unpack("<q", data[base:base + 8])[0]
    return (base + 8, name, value)
