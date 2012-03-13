# Bson
Independent BSON codec for Python that doesn't depend on MongoDB.

Only the following types are supported:

* 0x01: "double",
* 0x02: "string",
* 0x03: "document",
* 0x04: "array",
* 0x05: "binary",
* 0x08: "boolean",
* 0x0A: "none",
* 0x10: "int32",
* 0x12: "int64"

For binaries, only the default 0x0 type is supported.
Specifications can be found [here](http://bsonspec.org/#/specification)


## Usage
```python
import bson
a = bson.dumps({"A":[1,2,3,4,5,"6", u"7", {"C":u"DS"}]})
b = bson.loads(a)
b
{'A': [1, 2, 3, 4, 5, '6', u'7', {'C': u'DS'}]}
```

Currently, bson.dumps() and bson.loads() expects everything to be documents, or
dicts in Python-speak.

## Installation
If you want to try out the source package, you do this...

```bash
$ ./setup.py build
$ sudo ./setup.py install
```

Or, you can simply do this instead...

```bash
$ sudo easy_install bson
```
