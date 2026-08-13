from typing import get_args, Any

from utilities import write_json, load_json
from .local import LocalLoggerConfig, loggable as local_loggable
from .universal import GlobalLoggerConfig, loggable


def build_config(filepath: str):
    """
    Creates a JSON-parsable template config file at target file location.
    Note: requires modification to be valid.
    """
    otc: dict[loggable, bool] = {i: True for i in get_args(loggable)}
    al: dict[loggable, bool] = {i: True for i in get_args(loggable)}

    # On purpose.
    # noinspection bad-assignment
    tc: dict[loggable, int] = {i: None for i in get_args(loggable)}

    # local
    lal: dict[local_loggable, bool] = {i: True for i in get_args(local_loggable)}

    cfg = {
        'output_to_console': otc,
        'actively_logging': al,
        'target_channels': tc,
        'local_active_logging': lal
    }
    write_json(filepath, cfg, sort_keys=False, indent=4)


def from_json(filepath: str) -> tuple[GlobalLoggerConfig, LocalLoggerConfig]:
    """
    Parses input filepath as json to create logger configurations.
    """
    cfg = load_json(filepath)
    # try and get all of the important components
    otc = cfg['output_to_console']
    al = cfg['actively_logging']
    tc = cfg['target_channels']
    lal = cfg['local_active_logging']

    # Perform integrity test.
    def integ(name: str, target_type: type, source: dict[str, Any], target: set[str]):
        temp = target.copy()
        for k, v in source.items():
            if not k in target:
                print(f'Found unsupported key {k} in {name} config')
            elif k not in temp:
                print(f'Found duplicate key {k} in {name} config')
            else:
                # not none to force some setting value. Might need to change in the future
                if not (isinstance(v, target_type) and v is not None):
                    raise TypeError(f'Key {k} of {name} has value of type {type(v)}, expected {target_type.__name__}')
                temp.remove(k)
        if not temp.__len__() == 0:
            raise KeyError(f'{name} config missing keys {temp}')

    validation_global = set(get_args(loggable))
    integ('output_to_console', bool, otc, validation_global)
    integ('actively_logging', bool, al, validation_global)
    integ('target_channels', int, tc, validation_global)

    integ('local_active_logging', bool, lal, set(get_args(local_loggable)))

    # Now construct stuff
    global_config = GlobalLoggerConfig(otc, al, tc, filepath)
    local_config = LocalLoggerConfig(lal, filepath)
    return global_config, local_config
