###Continuous Integration
[![Build Status](https://travis-ci.org/Nikea/history.svg?branch=master)](https://travis-ci.org/Nikea/history)
[![Coverage Status](https://coveralls.io/repos/Nikea/history/badge.svg?branch=master&service=github)](https://coveralls.io/github/Nikea/history?branch=master)
[![codecov.io](http://codecov.io/github/Nikea/history/coverage.svg?branch=master)](http://codecov.io/github/Nikea/history?branch=master)


# History

History is a light weight mapping backed by sqlite which remember the
history of values.  The intent is for tracking relatively complex
configurations.


## Examples

The interface is very simple and can be accessed either via `[]` like
a dictionary or

```python
In [1]: from history import History

In [2]: fn = '/tmp/testing'

In [3]: hist = History(fn)

In [4]: hist['key'] = 'foo'

In [5]: hist['key']
Out[5]: 'foo'

```

via `put` and `past`

```python
In [6]: hist.put('k', 'bar')

In [7]: hist.past('k')
Out[7]: 'bar'

```

Using `past` you can extract past values

```python
In [8]: hist['key'] = 'baz'

In [9]: hist['key'] = 'buz'

In [10]: hist['key'] = 'aardvark'

In [11]:

In [11]: hist['key']
Out[11]: 'aardvark'

In [12]: hist.past('key', 1)
Out[12]: 'buz'

In [13]: hist.past('key', 2)
Out[13]: 'baz'

In [14]: hist.past('key', 3)
Out[14]: 'foo'

```

All `MutableMapping` methods except `del` and `pop` work.


## Known limitation

The keys are stored in the underlying sqlite table via the
hash of their string representation.  This means things like:

```python
hist[{'a': 123, 'b': 456}] = 'cat'
```

will work without error, but in python 3 will only get the same hash
half of the time.  Only use keys which have stable and unique
string representations.

The values are stored via a json blob, thus only values which can be
converted to json can be stored (no numpy arrays currently).

`h.del` and `h.pop` do not work (yet).  Just need to write the
sql query to delete them.