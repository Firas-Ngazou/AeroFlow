"""
A utility module for robust floating-point number comparison.

This module provides functions to safely compare floats for equality,
inequality, and ordering by using a tolerance, powered by math.isclose().

This module relies on the logic of `math.isclose()`, which uses two types of
tolerances for robust comparisons:

- Relative Tolerance (`rel_tol`): This is a percentage of the larger of the
  two values being compared. It is effective for large numbers where a fixed
  difference might be insignificant.

- Absolute Tolerance (`abs_tol`): This is a fixed, minimum difference value.
  It is essential for comparisons near zero, where a relative tolerance
  would become too small to be useful.

The comparison is considered true if the difference `abs(a - b)` is less than
the larger of these two calculated tolerances.

Author : Gemini
"""

import math

# --- Default tolerance values used across the module ---
# You can change these values to adjust the default precision for all functions.
DEFAULT_REL_TOL = 1e-9
DEFAULT_ABS_TOL = 0.0


def is_close(a: float, b: float, rel_tol=DEFAULT_REL_TOL, abs_tol=DEFAULT_ABS_TOL) -> bool:
    """
    Checks if two floats `a` and `b` are close enough to be considered equal.

    >>> is_close(0.1 + 0.2, 0.3)
    True
    >>> is_close(1.0, 1.1)
    False
    """
    return math.isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol)


def is_not_close(a: float, b: float, rel_tol=DEFAULT_REL_TOL, abs_tol=DEFAULT_ABS_TOL) -> bool:
    """
    Checks if two floats `a` and `b` are not close.

    >>> is_not_close(1.0, 1.1)
    True
    >>> is_not_close(0.1 + 0.2, 0.3)
    False
    """
    return not math.isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol)


def is_greater(a: float, b: float, rel_tol=DEFAULT_REL_TOL, abs_tol=DEFAULT_ABS_TOL) -> bool:
    """
    Checks if `a` is strictly greater than `b`, accounting for tolerance.

    >>> is_greater(0.4, 0.3)
    True
    >>> is_greater(0.1 + 0.2, 0.3)
    False
    """
    return a > b and not math.isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol)


def is_less(a: float, b: float, rel_tol=DEFAULT_REL_TOL, abs_tol=DEFAULT_ABS_TOL) -> bool:
    """
    Checks if `a` is strictly less than `b`, accounting for tolerance.

    >>> is_less(0.2, 0.3)
    True
    >>> is_less(0.1 + 0.2, 0.3)
    False
    """
    return a < b and not math.isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol)


def is_greater_or_close(a: float, b: float, rel_tol=DEFAULT_REL_TOL, abs_tol=DEFAULT_ABS_TOL) -> bool:
    """
    Checks if `a` is greater than or close to `b`.

    >>> is_greater_or_close(0.4, 0.3)
    True
    >>> is_greater_or_close(0.1 + 0.2, 0.3)
    True
    """
    return a > b or math.isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol)


def is_less_or_close(a: float, b: float, rel_tol=DEFAULT_REL_TOL, abs_tol=DEFAULT_ABS_TOL) -> bool:
    """
    Checks if `a` is less than or close to `b`.

    >>> is_less_or_close(0.2, 0.3)
    True
    >>> is_less_or_close(0.1 + 0.2, 0.3)
    True
    """
    return a < b or math.isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol)


def run_doctests():
    """
    Runs all the doctests defined in this module.
    """
    import doctest

    print("Running doctests...")
    results = doctest.testmod()
    if results.failed == 0:
        print(f"All {results.attempted} doctests passed successfully.")
    else:
        print(f"{results.failed} out of {results.attempted} doctests failed.")
    return results


# if __name__ == "__main__":
#     # When the script is executed directly, run the embedded tests.
#     run_doctests()