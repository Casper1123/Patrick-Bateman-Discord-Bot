terminator: str = ';'
bounds: set[str] = {'{', '[', '(', "'", '"'}  # Opens another subsection. Input is already stripped of containing surrounding {}
be_map: dict[str, str] = {'{': '}', '[': ']', '(': ')', '\'': '\'', '"': '"'}
escapes: set[str] = set(be_map.values())  # convert to list, makes it easier to work with.
doubles: list[str] = [b for b in bounds if be_map[b] == b]