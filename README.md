# HistoryDict

HistoryDict is a light weight mapping backed by sqlite which remember the
history of values.  The intent is for tracking relatively complex
configurations.


## Examples

The interface is very simple and can be accessed either via `[]` like
a dictionary

```python
In [1]: from historydict import HistoryDict

In [2]: fn = '/tmp/testing'

In [3]: hist = HistoryDict(fn)

In [4]: hist['key'] = 'foo'

In [5]: hist['key']
Out[5]: 'foo'

```

or via `past`

```python
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

All `MutableMapping` methods work.


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
