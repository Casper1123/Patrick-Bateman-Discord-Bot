# Just for making memory stack usage easier.
from typing import TypeVar

_T = TypeVar('_T')

def _flatten(memory_stack: list[dict[str, _T]]) -> dict[str, _T]:
    """
    Flatten a given memory stack into available entries in local scope.
    """
    mem: dict[str, _T] = {}
    for scope in reversed(memory_stack):
        for k, v in scope.items():
            mem[k] = v

    return mem

def _find_scope(memory_stack: list[dict[str, _T]], key: str) -> int | None:
    """
    Find the scope the given key belongs to. Returns scope index, with 0 being top-level.
    """
    if not memory_stack:
        raise IndexError('Memory stack is empty.')

    for i, scope in enumerate(memory_stack):
        if key in scope.keys():
            return i
    return None

def fetch(memory_stack: list[dict[str, _T]], key: str) -> _T | None:
    """
    Find entry in memory_stack. Returns None if not found.
    """
    mem = _flatten(memory_stack)
    return mem[key] if key in mem.keys() else None

def assign(memory_stack: list[dict[str, _T]], key: str, value: _T) -> None:
    """
    Assign value to the key's corresponding scope.
    Creates local scope entry
    """
    # Find scope
    scope: int | None = _find_scope(memory_stack, key)
    if scope is None:
        scope = len(memory_stack) - 1
    scope: int

    memory_stack[scope][key] = value