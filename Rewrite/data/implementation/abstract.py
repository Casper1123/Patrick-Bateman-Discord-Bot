from __future__ import annotations

import asyncio
from time import monotonic
import sqlite3 as _sql
from abc import ABC
import os
from typing import TypeVar

_T = TypeVar('_T')
# Tree-structure, nodes are RecursiveCacheHandlers, leaves are values.
# Index through levels in dict by keys.
# todo: remove assertions for proper logging purposes
# todo: remove most of the checking logic and just.. idk.. have a helper function for getting the node?
class RecursiveCacheEntry:
    def __init__(self, val, timeout: float):
        self.val = val
        self.timeout = timeout

class RecursiveCacheHandler:
    """
    Automated data caching handler using a Tree-noded structure. Try not to go too deep.
    """
    def __init__(self, root: RecursiveCacheHandler = None, path: tuple[str, ...] = None):
        """
        Leave empty for manual initialization as a Root node. Use class methods otherwise.
        """
        self.children: dict[str, RecursiveCacheHandler | RecursiveCacheEntry] = {}
        self._maintenance_loop: bool | None = False # If None is in shutdown mode.

        self._timeouts: list[tuple[float, tuple[str, ...]]]
        if not root:
            self.root = self # is_root <==> self.root == self
            self._timeouts: list[tuple[float, tuple[str, ...]]] = []
        else:
            self.root = root
            self._timeouts = self.root._timeouts # Not to be used, just here just in case.

        self.path: tuple[str, ...] = () if not path else path
        self.path_as_string: str = '/'.join(('ROOT',) + self.path)

    def register(self, keys: tuple[str], val, timeout: float) -> None:
        """
        Create a new cache entry leaf, creating required nodes along the way.
        If no path was given, raises an AttributeError.
        Re-registering raises an AssertionError.
        """
        if not keys:
            raise AttributeError(f'Received empty keys at path {self.path_as_string}')
        curr, *rest = keys
        if rest:
            if not curr in self.children.keys():
                new_node: RecursiveCacheHandler = RecursiveCacheHandler(root=self.root, path=self.path + (curr,))
                self.children[curr] = new_node
            assert isinstance(self.children[curr], RecursiveCacheHandler), f'Walk down path into cache of {self.path_as_string}/{curr}/{'/'.join(rest)} cannot be completed as {self.path_as_string}/{curr} does not yield a tree node.'
            self.children[curr].register(rest, val, timeout)
        else:
            assert curr not in self.children.keys(), f'{self.path_as_string}/{curr} is already registered, use Refresh instead.'
            self.children[curr] = RecursiveCacheEntry(val, monotonic() + timeout)

    def refresh(self, keys: tuple[str], timeout: float) -> None:
        """
        Refreshes the timeout on the given data path, assuming it exists.
        If it does not, raises an AssertionError. If no keys were given, it raises an AttributeError.
        """
        if not keys:
            raise AttributeError(f'Received empty keys at path {self.path_as_string}')
        curr, *rest = keys
        assert curr in self.children.keys(), f'{self.path_as_string}/{curr}{'/' + '/'.join(rest) if rest else ''} cannot be refreshed as {self.path_as_string}/{curr} does not exist.'
        if rest:
            assert isinstance(self.children[curr], RecursiveCacheHandler), f'Walk down path into cache of {self.path_as_string}/{curr}/{'/'.join(rest)} cannot be completed as {self.path_as_string}/{curr} does not yield a tree node.'
            self.children[curr].refresh(rest, timeout)
        else:
            assert isinstance(self.children[curr], RecursiveCacheEntry), f'Walk down path into cache of {self.path_as_string}/{curr} cannot be completed as {self.path_as_string}/{curr} does not yield a tree leaf.'
            self.children[curr].timeout = monotonic() + timeout

    def unregister(self, keys: tuple[str]) -> None:
        """
        Early-unregisters cached entry leaves AND NODES (if path ends early) for given path.
        Higher up the tree is first in the list.

        Raises an AssertionError if the path somehow collides with a Leaf early.
        Silently quits if any node along the way was not registered.
        """
        if not keys:
            return

        curr, *rest = keys
        if rest:
            if not curr in self.children.keys():
                return
            assert isinstance(self.children[curr], RecursiveCacheHandler), f'Walk down path into cache of {self.path_as_string}/{curr}/{'/'.join(rest)} cannot be completed as {self.path_as_string}/{curr} does not yield a tree node.'
            self.children[curr].unregister(rest)
        else:
            del self.children[curr]

    def is_cached(self, keys: tuple[str]) -> bool:
        if not keys:
            return False
        curr, *rest = keys
        if not curr in self.children.keys():
            return False
        if isinstance(self.children[curr], RecursiveCacheHandler):
            return self.children[curr].is_cached(rest)
        else:
            return True

    def get_cached(self, keys: tuple[str], out_type: type[_T]) -> _T:
        if not keys:
            raise AttributeError(f'Received empty keys at path {self.path_as_string}')
        curr, *rest = keys
        assert curr in self.children.keys(), f'{self.path_as_string}/{curr}{'/' + '/'.join(rest) if rest else ''} cannot be obtained as {self.path_as_string}/{curr} does not exist.'
        if rest:
            assert isinstance(self.children[curr], RecursiveCacheHandler), f'Walk down path into cache of {self.path_as_string}/{curr}/{'/'.join(rest)} cannot be completed as {self.path_as_string}/{curr} does not yield a tree node.'
            return self.children[curr].get_cached(rest, out_type)
        else:
            assert isinstance(self.children[curr], RecursiveCacheEntry), f'Walk down path into cache of {self.path_as_string}/{curr} cannot be completed as {self.path_as_string}/{curr} does not yield a tree leaf.'
            val: RecursiveCacheEntry = self.children[curr]
            if not isinstance(val.val, out_type):
                raise TypeError(f'Return value at path {self.path_as_string}/{curr} is of type {type(val.val)} (wanted {out_type})')
            return val.val

    async def maintenance_loop(self, timeout: float, clean_empty_nodes: bool = False) -> None:
        """
        Timeout in seconds. Automatically and periodically cleans out tree nodes.
        Can only be used on tree roots (self.root == self) and might raise an Exception if the starting fails.
        """
        if not self.root == self:
            raise Exception('This node is not the root of its own tree.')
        if self._maintenance_loop:
            raise Exception('Maintenance loop is already running')
        if self._maintenance_loop is None:
            raise Exception('Maintenance loop shutdown command issued.')

        self._maintenance_loop = True
        while self._maintenance_loop:
            self._check_now(monotonic(), clean_empty_nodes)
            await asyncio.sleep(timeout)

            # todo: for the heap version, see below.
            # min heap
            # now = monotonic()
            # while heap is not empty
            #   if earliest timeout is after this, break that shii and set the sleeper to then.
            #   If it's not, pop it out and
                # find its entry
                # Do it still exist? If not, just skip
                # If it does, check if it's current value is still timeout.
                # If it is (as it was not updated) remove it.
            # When refreshing, add new copy to the heap, as the older ones will fizzle automatically anyways.

        self._maintenance_loop = False

    def stop_maintenance_loop(self) -> bool:
        """
        Stops any running maintenance loops.
        :returns: Shutdown command successfully issued.
        """
        if self._maintenance_loop:
            self._maintenance_loop = None
            return True
        return False

    def _check_now(self, time: float, clean_empty_child_nodes: bool):
        """
        Checks children for timeout removal using tree walk at the given time.
        """ # fixme: optimization possible with heapq
        marked: list[str] = []
        for k, v in self.children.items():
            if isinstance(v, RecursiveCacheEntry):
                if v.timeout < time:
                    marked.append(k)
            else:
                v._check_now(time, clean_empty_child_nodes)
                if len(v.children.keys()) == 0 and clean_empty_child_nodes:
                    marked.append(k)

        for k in marked:
            del self.children[k]

class AbstractSQLDatabase(ABC):
    def __init__(self, db_path: str, schema_path: str) -> None:
        self.path = db_path

        if not os.path.isfile(schema_path):
            raise FileNotFoundError(f"Schema at {schema_path} does not exist")

        with _sql.connect(db_path) as conn:
            with open(schema_path, "r") as f:
                conn.executescript(f.read())

    def _connection(self) -> _sql.Connection:
        conn = _sql.connect(self.path)
        conn.row_factory = _sql.Row
        return conn