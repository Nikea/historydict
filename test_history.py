from nose.tools import assert_equal
from history import History
import tempfile

from nose.tools import assert_raises
OBJ_ID_LEN = 36
h = None


def setup():
    global h
    h = History(':memory:')


def test_history():
    run_id = ''.join(['a'] * OBJ_ID_LEN)
    # Simple round-trip: put and past
    config1 = {'plot_x': 'long', 'plot_y': 'island'}
    h.put(run_id, config1)
    result1 = h.past(run_id)
    assert_equal(result1, config1)

    # Put a second entry. Check that past returns most recent.
    config2 = {'plot_x': 'new', 'plot_y': 'york'}
    h.put(run_id, config2)
    result2 = h.past(run_id)
    assert_equal(result2, config2)
    # And.past(..., 1) returns previous.
    result1 = h.past(run_id, 1)
    assert_equal(result1, config1)


def test_clear():
    h.put('hi', 'mom')
    h.clear()
    assert_raises(KeyError, lambda: h.past('hi'))


def test_trim():
    assert_raises(NotImplementedError, h.trim)


def test_neg_numback_fails():
    assert_raises(ValueError, h.past, 'test', -1)


def test_gs_items():
    h[123] = 'aardvark'
    assert_equal(h[123], 'aardvark')


def test_opening():
    with tempfile.NamedTemporaryFile(delete=False) as fn:
        filename = fn.name
    h1 = History(filename)
    h1['aardvark'] = 'ants'
    del h1

    h2 = History(filename)
    assert_equal(h2['aardvark'], 'ants')


def test_iter():
    h.clear()
    keys = set('abcd')
    for k in keys:
        h[k] = k
    for k, v in h.items():
        assert_equal(k, v)


def test_no_del():
    h.clear()
    h['a'] = 123
    with assert_raises(NotImplementedError):
        del h['a']


def test_no_key_in_del():
    h.clear()
    with assert_raises(KeyError):
        del h['aardvark']


def test_len():
    h.clear()
    keys = set('abcd')
    for k in keys:
        h[k] = k

    assert_equal(len(keys), len(h))


def test_get():
    h.clear()
    b = h.get('b', 'aardvark')
    assert_equal(b, 'aardvark')
