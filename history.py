# ######################################################################
# Copyright (c) 2015, Brookhaven Science Associates, Brookhaven        #
# National Laboratory. All rights reserved.                            #
#                                                                      #
# BSD 3-Clause                                                         #
# ######################################################################

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import six
import logging
import hashlib
import sqlite3
import json
from collections import MutableMapping

logger = logging.getLogger(__name__)


TABLE_NAME = 'HISTORY_1_0'
CREATION_QUERY = """
CREATE TABLE {0} (
        _id CHAR(40),
        N INT,
        blob BLOB)""".format(TABLE_NAME)
INSERTION_QUERY = """
INSERT INTO {0}
(_id, N, blob)
VALUES
(?,
1 + (SELECT COALESCE(MAX(N), 0)
     FROM {0}
     WHERE _id=?),
?)""".format(TABLE_NAME)
SELECTION_QUERY = """
SELECT blob
FROM {0}
WHERE _id=? ORDER BY N DESC LIMIT ?""".format(TABLE_NAME)
SHOW_TABLES_QUERY = """SELECT name FROM sqlite_master WHERE type='table'"""
DELETION_QUERY = "DELETE FROM {0}".format(TABLE_NAME)


class History(MutableMapping):
    """
    A helper class to make persisting configuration data easy.

    This class works by providing a this wrapper over a sqlite
    data base which has a column for the key, the number of times
    the key has been seen, and the data stored as a json-encoded blob.

    The key '__list_of_currently_known_about_keys' is reserved.

    """
    RESERVED_KEY_KEY = '__list_of_currently_known_about_keys'

    def __init__(self, fname):
        self._cache = {}
        self._conn = sqlite3.connect(fname)
        if not self._has_tables():
            logger.debug("Created a fresh table in %s,",
                         fname)
            self._create_tables()
        else:
            logger.debug("Found an existing table in %s", fname)

        for k in self:
            self._cache[k] = self.get(k)

    def __getitem__(self, key):
        return self._cache[key]

    def __setitem__(self, key, val):
        return self.put(key, val)

    def __iter__(self):
        return iter(self.get(self.RESERVED_KEY_KEY))

    def __delitem__(self, key):
        cur_keys = self[self.RESERVED_KEY_KEY]
        if key not in cur_keys:
            raise KeyError(key)
        cur_keys.remove(key)
        # INSERT SQL QUERY TO DELETE ALL INFO ABOUT THIS KEY
        self[self.RESERVED_KEY_KEY] = cur_keys
        raise NotImplementedError()

    def __len__(self):
        return len(self[self.RESERVED_KEY_KEY])

    def get(self, key, num_back=0):
        """
        Retrieve a past state of the data payload associated with `key`,
        by default the most recent state.  Previous states can be accessed
        via the `num_back` kwarg which will retrieve the nth back entry (so
        `num_back=0` get the latest, `num_back=5` gets the fifth most recent.

        Parameters
        ----------
        key : str
            The key to look up data by

        num_back : int, optional
            Number back from the latest entry to retrieve.

        Returns
        -------
        data_blob : object
            Data payload
        """
        if num_back < 0:
            raise ValueError("num_back must be nonnegative")

        if num_back == 0 and key in self._cache:
            return self._cache[key]

        key = hashlib.sha1(str(key).encode('utf-8')).hexdigest()
        res = self._conn.execute(SELECTION_QUERY, (key, 1 + num_back))
        try:
            blob, = res.fetchall()[-1]
        except IndexError:
            raise KeyError("No such data key in the database.")
        v = json.loads(blob)
        self._cache[key] = v
        return v

    def put(self, key, data):
        """
        Store a data blob into the database

        Parameters
        ----------
        key : str
            The key to look up data by later

        data : object
            The data to be stored.  Can be any object that
            json can serialize.
        """
        hk = hashlib.sha1(str(key).encode('utf-8')).hexdigest()
        data_str = json.dumps(data)
        self._conn.execute(INSERTION_QUERY, (hk, hk, data_str))  # yes, twice
        self._conn.commit()

        cur_keys = self.get(self.RESERVED_KEY_KEY)
        if key != self.RESERVED_KEY_KEY and key not in cur_keys:

            cur_keys.append(key)
            self[self.RESERVED_KEY_KEY] = list(cur_keys)
        self._cache[key] = data

    def clear(self):
        self._conn.execute(DELETION_QUERY)
        self.put(self.RESERVED_KEY_KEY, [])
        self._cache = dict()

    def trim(self, N=1):
        """
        Trim the databaase to keep at most N entries for
        all keys.

        Parameters
        ----------
        N : int, optional
            The number of entries to keep.  N < 1 is treated as 1
        """
        raise NotImplementedError("TODO")

    def _create_tables(self):
        """
        Create the required tables for data storage
        """
        self._conn.execute(CREATION_QUERY)
        self.put(self.RESERVED_KEY_KEY, [])

    def _has_tables(self):
        """
        Determine of the opened file has the needed tables
        """
        res = self._conn.execute(SHOW_TABLES_QUERY)
        tables = [t[0] for t in res.fetchall()]
        return TABLE_NAME in tables
