# Just for making memory stack usage easier.
import datetime as _datetime
from typing import TypeVar

INITIAL_MEMORY_TYPES: dict[str, type] = {
    '\\n': str,

    # interaction target
    'user.id': int,
    'user': str,
    'user.name': str,
    'user.created_at': _datetime.datetime,
    'user.account': str,
    'user.mutual_guilds': int,
    'user.roles': int,  # role count, not the actual roles.

    'self.id': int,
    'self': str,
    'self.name': str,
    'self.created_at': _datetime.datetime,
    'self.account': str,
    'self.roles': int,

    'channel': str,
    'channel.id': int,
    'channel.name': str,
    'channel.created_at': _datetime.datetime,
    'channel.jump_url': str,

    'guild': str,
    'guild.id': int,
    'guild.name': str,
    'guild.created_at': _datetime.datetime,
    'guild.members': int,  # member count
    'guild.roles': int,  # still, role count.

    # guild owner
    'owner.id': int,
    'owner': str,
    'owner.name': str,
    'owner.created_at': _datetime.datetime,
    'owner.mutual_guilds': int,
    'owner.account': str,
    'owner.roles': int,

    # Not always available!
    # 'message': int,
    # 'message.jump_url': str,

    # external
    'local_facts': int,
    'global_facts': int,
    'total_facts': int,
}

_T = TypeVar('_T')

def fetch(memory: dict[str, _T], key: str) -> _T | None:
    """
    Get entry from Memory, silently returning None if not found.
    """
    return memory[key] if key in memory.keys() else None

def assign(memory: dict[str, _T], key: str, value: _T) -> None:
    """
    Assign value to memory, raising error if a protected key is to be assigned.
    """
    if key in INITIAL_MEMORY_TYPES.keys():
        raise KeyError(f'Key {key} cannot be overridden as it is in standard memory.')

    memory[key] = value

def reshape(m1: dict[str, _T], m2: dict[str, _T]) -> None:
    """
    Mutates m1 to have values of m2, while also performing a quick memory integrity check s.t. all required keys exist and have the same type.
    """
    # Compare key sets
    m1k, m2k = set(m1.keys()), set(m2.keys())
    missing: set[str] = m1k - m2k
    if missing:
        raise KeyError(f'Missing m1 keys {missing}')

    new: set[str] = m2k - m1k
    for k in m2k:
        if _T != type:
            t1 = type(m1[k])
            t2 = type(m2[k])
        else:
            t1, t2 = m1[k], m2[k]

        # Type checking entries for both versions
        if not t1 == t2 and not k in new:
            raise TypeError(f'm1 key {k} of type {t1} not of type {t2}.')
        m1[k] = m2[k]
