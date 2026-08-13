from __future__ import annotations

import asyncio
import heapq
from time import monotonic
from typing import TypeVar

_T = TypeVar('_T')


# Tree-structure, nodes are RecursiveCacheHandlers, leaves are values.
# Index through levels in dict by keys.
class RecursiveCacheEntry:
    def __init__(self, val, timeout: float):
        self.val = val
        self.timeout = timeout


# TODO: WARNING FOR USING THIS IN IMPLEMENTATION; ARE THERE RACING CONDITIONS FOR AROUND AWAIT CALLS?
class RecursiveCacheHandler:
    """
    Automated data caching handler using a Tree-node structure. Try not to go too deep.
    """

    def __init__(self, root: RecursiveCacheHandler | None = None, path: tuple[str, ...] | None = None):
        """
        Leave empty for manual initialization as a Root node. Use class methods otherwise.
        """
        self.children: dict[str, RecursiveCacheHandler | RecursiveCacheEntry] = {}
        self._maintenance_loop: bool | None = False  # If None is in shutdown mode.


        if not root:
            self.root = self  # is_root <==> self.root == self
            self._timeouts: list[tuple[float, tuple[str, ...]]] = []
        else:
            self.root = root
            self._timeouts = self.root._timeouts  # Not to be used, just here just in case.
        self._timeouts: list[tuple[float, tuple[str, ...]]]

        self.path: tuple[str, ...] = () if not path else path
        self.path_as_string: str = '/'.join(('ROOT',) + self.path)

    def register(self, keys: tuple[str], val, timeout: float) -> None:
        """
        Create a new cache entry leaf, creating required nodes along the way.
        If no path was given, raises an AttributeError.
        Re-registering raises an Exception.
        """
        if not keys:
            raise AttributeError(f'Received empty keys at path {self.path_as_string}')
        curr, *rest = keys
        if rest:
            if not curr in self.children.keys():
                new_node: RecursiveCacheHandler = RecursiveCacheHandler(root=self.root, path=self.path + (curr,))
                self.children[curr] = new_node
            if not isinstance(self.children[curr], RecursiveCacheHandler):
                raise Exception(
                    f'Walk down path into cache of {self.path_as_string}/{curr}/{'/'.join(rest)} cannot be completed as {self.path_as_string}/{curr} does not yield a tree node.')
            # noinspection unresolved-references
            # Ensured child at key curr is Handler not Entry
            # noinspection bad-argument-type
            # rest may be treated as tuple.
            self.children[curr].register(rest, val, timeout)
        else:
            if curr not in self.children.keys():
                raise Exception(f'{self.path_as_string}/{curr} is already registered, use Refresh instead.')

            timeout = monotonic() + timeout
            self.children[curr] = RecursiveCacheEntry(val, timeout)
            heapq.heappush(self.root._timeouts, (timeout, self.path + (curr,)))

    def refresh(self, keys: tuple[str], timeout: float) -> None:
        """
        Refreshes the timeout on the given data path, assuming it exists.
        If it does not, raises an Exception. If no keys were given, it raises an AttributeError.
        """
        if not keys:
            raise AttributeError(f'Received empty keys at path {self.path_as_string}')
        curr, *rest = keys
        if curr not in self.children.keys():
            raise KeyError(
                f'{self.path_as_string}/{curr}{'/' + '/'.join(rest) if rest else ''} cannot be refreshed as {self.path_as_string}/{curr} does not exist.')

        if rest:
            if not isinstance(self.children[curr], RecursiveCacheHandler):
                raise Exception(
                    f'Walk down path into cache of {self.path_as_string}/{curr}/{'/'.join(rest)} cannot be completed as {self.path_as_string}/{curr} does not yield a tree node.')

            # noinspection unresolved-references
            # Ensured child at key curr is Handler not Entry
            # noinspection bad-argument-type
            # rest may be treated as tuple.
            self.children[curr].refresh(rest, timeout)
        else:
            if not isinstance(self.children[curr], RecursiveCacheEntry):
                raise Exception(
                    f'Walk down path into cache of {self.path_as_string}/{curr} cannot be completed as {self.path_as_string}/{curr} does not yield a tree leaf.')

            timeout = monotonic() + timeout
            # noinspection unresolved-references
            # Child MUST be leaf, given the check above.
            self.children[curr].timeout = timeout
            heapq.heappush(self.root._timeouts, (timeout, self.path + (curr,)))

    def unregister(self, keys: tuple[str]) -> None:
        """
        Early-unregisters cached entry leaves AND NODES (if path ends early) for given path.
        Higher up the tree is first in the list.

        Raises an Exception if the path somehow collides with a Leaf early.
        Silently quits if any node along the way was not registered.
        """
        self._prune_entry(keys, clean_empty_nodes=True)

    def _prune_entry(self, keys: tuple[str, ...], clean_empty_nodes: bool) -> None:
        """
        Removes entry at path (or removes entire subtree at path) rooted at call node.
        :param keys: Path to entry / subtree root node.
        :param clean_empty_nodes: Delete any remaining empty internal nodes?
        """
        if not keys:
            return

        curr, *rest = keys
        if rest:
            if not curr in self.children.keys():
                return
            if not isinstance(self.children[curr], RecursiveCacheHandler):
                raise Exception(
                    f'Walk down path into cache of {self.path_as_string}/{curr}/{'/'.join(rest)} cannot be completed as {self.path_as_string}/{curr} does not yield a tree node.')
            # noinspection unresolved-references
            # Ensured child at key curr is Handler not Entry
            # noinspection bad-argument-type
            # rest may be treated as tuple.
            self.children[curr]._prune_entry(rest, clean_empty_nodes)

            # noinspection unresolved-references
            # Ensured child at key curr is Handler not Entry
            if clean_empty_nodes and not self.children[curr].children:
                del self.children[curr]
        else:
            del self.children[curr]

    def is_cached(self, keys: tuple[str, ...]) -> bool:
        if not keys:
            return False
        curr, *rest = keys
        if not curr in self.children.keys():
            return False
        if isinstance(self.children[curr], RecursiveCacheHandler):
            # noinspection unresolved-references
            # Ensured child at key curr is Handler not Entry
            # noinspection bad-argument-type
            # rest may be treated as tuple.
            return self.children[curr].is_cached(rest)
        else:
            return True

    def get_cached(self, keys: tuple[str, ...], out_type: type[_T]) -> _T | None:
        """
        Get cached value, if it exists.
        :param keys: Target path to cached value.
        :param out_type: Expected type of output.
        :return: Target object or None if not found.
        """
        val: RecursiveCacheEntry | None = self._find(keys)
        if val is None:
            return None
        if not isinstance(val.val, out_type):
            raise TypeError(
                f'Return value at path {self.path_as_string}/{'/'.join(keys)} is of type {type(val.val)} (wanted {out_type})')
        return val.val

    def _find(self, keys: tuple[str, ...]) -> RecursiveCacheEntry | None:
        """
        Find Entry in data tree, if it exists.
        :param keys: Target path to cached value.
        :return: Direct `RecursiveCacheEntry`
        """
        if not keys:
            raise AttributeError(f'Received empty keys at path {self.path_as_string}')
        curr, *rest = keys
        if not curr in self.children.keys():
            return None

        if rest:
            if not isinstance(self.children[curr], RecursiveCacheHandler):
                raise Exception(
                    f'Walk down path into cache of {self.path_as_string}/{curr}/{'/'.join(rest)} cannot be completed as {self.path_as_string}/{curr} does not yield a tree node.')
            # noinspection unresolved-references
            # Ensured child at key curr is Handler not Entry
            # noinspection bad-argument-type
            # rest may be treated as tuple.
            return self.children[curr]._find(rest)
        else:
            if not isinstance(self.children[curr], RecursiveCacheEntry):
                raise Exception(
                    f'Walk down path into cache of {self.path_as_string}/{curr} cannot be completed as {self.path_as_string}/{curr} does not yield a tree leaf.')

            # Ensured child at key curr is Entry
            # noinspection bad-return
            return self.children[curr]

    async def maintenance_loop(self, timeout: float, clean_empty_nodes: bool = True) -> None:
        """
        Automatically and periodically remove expired entries.
        :param timeout: timeout to check again if the cache is empty
        :param clean_empty_nodes: whether to clean empty nodes.

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
            while not self._timeouts:
                await asyncio.sleep(timeout)

            now = monotonic()  # Maybe move inside loop below if things take too long.

            while self._timeouts:
                # check first entry (min-heap moment)
                var_timeout, path = self._timeouts[0]
                if var_timeout > now:
                    await asyncio.sleep(min(var_timeout - now + 1, timeout))  # wait 1 more second
                    break  # Try again after countdown

                heapq.heappop(self._timeouts)  # pops it out, we have data in (timeout, path) anyways

                entry: RecursiveCacheEntry | None = self._find(path)

                if entry is None:
                    continue

                if entry.timeout > var_timeout:  # current entry timeout is invalid
                    continue

                self._prune_entry(path, clean_empty_nodes=clean_empty_nodes)

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

    def _check_complete(self, clean_empty_child_nodes: bool, time: float | None = None, ):
        """
        Checks children for timeout removal using tree walk at the given time.
        """
        # Note: just here as old implementation. Idk, might just keep this around for funsies.
        if time is None:
            time = monotonic()

        marked: list[str] = []
        for k, v in self.children.items():
            if isinstance(v, RecursiveCacheEntry):
                if v.timeout < time:
                    marked.append(k)
            else:
                v._check_complete(clean_empty_child_nodes, time)
                if len(v.children.keys()) == 0 and clean_empty_child_nodes:
                    marked.append(k)

        for k in marked:
            del self.children[k]
