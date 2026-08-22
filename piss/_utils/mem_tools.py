# Just for making memory stack usage easier.
from typing import TypeVar
import datetime as _datetime


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