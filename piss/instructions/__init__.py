_terminator: str = ';'
_bounds: set[str] = {'{', '[', '(', "'", '"'}  # Opens another subsection. Input is already stripped of containing surrounding {}
_be_map: dict[str, str] = {'{': '}', '[': ']', '(': ')', '\'': '\'', '"': '"'}
_escapes: set[str] = set(_be_map.values())  # convert to list, makes it easier to work with.
_doubles: list[str] = [b for b in _bounds if _be_map[b] == b]