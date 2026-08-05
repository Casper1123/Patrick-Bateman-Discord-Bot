from typing import Literal

_favour = Literal['lower', 'higher']


def cram_options(n: int, i: int, k: int, favour: _favour = 'higher') -> tuple[int, int]:
    """
    :param n: n item options to select from.
    :param i: Central index of item. Indexing starting at 0.
    :param k: Selection width.
    :param favour: If not perfectly centered, favour taking a lower or higher option.
    :returns: tuple[lower, upper] slicing indices giving at most k options centering index i.
    """
    # Base cases
    if n <= 0:
        # Bad n input
        return 0, 0
    if k >= n:
        # More selection than options
        return 0, n
    # I recentering on out of bounds i
    if i < 0:
        i = 0
    elif i >= n:
        i = n - 1

    # Left and right offset from i
    if favour == "higher":
        left = (k - 1) // 2
    else:
        left = k // 2

    right = k - left

    # Actual indices
    lower = i - left
    upper = i + right

    # Final adjustment for values to close to the bounds.
    if lower < 0:
        upper -= lower
        lower = 0
    if upper > n:
        lower -= upper - n
        upper = n

    assert upper - lower == k, 'Not of width k'
    assert 0 <= lower <= upper <= n, '0 <= lower <= upper <= n not valid.'
    return lower, upper

