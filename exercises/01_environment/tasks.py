"""Module 01 - How Python runs.  Student task sheet.

Fill in every ``TODO``.  Do not rename functions or change signatures:
``test_tasks.py`` imports this module and grades it.

    pytest exercises/01_environment -q
"""

from __future__ import annotations

import pathlib


# ------------------------------------------------------------------ tier: B
def interpreter_info() -> dict:
    """Return a dict describing the interpreter running this code.

    Keys (exact names):
      "version"     -> tuple of the three version numbers, e.g. (3, 11, 2)
      "executable"  -> absolute path of the running interpreter (str)
      "in_venv"     -> True when running inside a virtual environment (bool)

    Hint: everything you need lives in the ``sys`` module. A virtualenv is
    active when ``sys.prefix`` differs from ``sys.base_prefix``.
    """
    # TODO: implement
    raise NotImplementedError


def write_first_program(path: str | pathlib.Path) -> str:
    """Write a tiny program to *path* and return the exact text written.

    The program must, when executed, print ``Hello, industry.`` on one line.
    Create parent directories if needed. The returned string must equal the
    file's content byte for byte.
    """
    # TODO: implement
    raise NotImplementedError


# -------------------------------------------------------------- tier: I
def inspect_bytecode(source: str) -> tuple[tuple, list[str]]:
    """Compile *source* and report what the compiler produced.

    Returns ``(constants, opnames)`` where
      constants -> tuple(code object's ``co_consts``)
      opnames   -> list of opcode names in order, e.g. ["LOAD_CONST", ...]

    Use ``compile(..., "exec")`` and the ``dis`` module. Do not let ``dis``
    print anything to stdout while you collect the names.
    """
    # TODO: implement
    raise NotImplementedError


def is_constant_folded(source: str) -> bool:
    """True when an arithmetic expression in *source* was folded at compile time.

    ``is_constant_folded("x = 1 + 2")``  -> True   (only LOAD_CONST remains)
    ``is_constant_folded("x = a + 2")``  -> False  (a BINARY_OP survives)
    """
    # TODO: implement
    raise NotImplementedError


# -------------------------------------------------------------- tier: Ind
def make_project_skeleton(root: str | pathlib.Path) -> None:
    """Create a minimal installable src-layout project under *root*.

    Must create exactly this tree (package name ``myproject``)::

        root/
            pyproject.toml        # contains a [project] table with name + version
            .gitignore            # contains '.venv/' and '__pycache__/'
            README.md
            src/myproject/__init__.py     # may be empty
            src/myproject/py.typed        # empty marker file
            tests/test_smoke.py           # must contain a function named test_ok
    """
    # TODO: implement
    raise NotImplementedError


def validate_project(root: str | pathlib.Path) -> list[str]:
    """Return a list of problems found in the project at *root*.

    An empty list means the skeleton is healthy. Report at least:
      "missing pyproject.toml"
      "pyproject.toml has no [project] table"
      "missing src/myproject/__init__.py"
      "missing src/myproject/py.typed"
      "missing tests/test_smoke.py"
      ".gitignore does not ignore .venv/"
      ".gitignore does not ignore __pycache__/"
    (only the problems that actually apply, in any order)
    """
    # TODO: implement
    raise NotImplementedError
