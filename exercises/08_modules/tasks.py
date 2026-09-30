"""Module 08 - Modules & packages.  Student task sheet."""

from __future__ import annotations

import pathlib


# ------------------------------------------------------------------ tier: B
def load_module_from_file(path, name: str):
    """Import the .py file at *path* under module name *name* and return the
    module object. Use importlib.util.spec_from_file_location."""
    raise NotImplementedError


def module_report(mod) -> dict:
    """{"name": mod.__name__, "file": absolute path or None,
    "has_main_guard": True if the source contains an
    `if __name__ == "__main__":` block}."""
    raise NotImplementedError


# -------------------------------------------------------------- tier: I
def build_package(root, files: dict) -> pathlib.Path:
    """Write a package tree under *root* from {relative posix path: source}.

    Any directory that will be imported as a package but has no __init__.py
    in *files* gets an empty one created automatically. Returns root as Path.
    """
    raise NotImplementedError


def import_from(root, dotted: str):
    """Import *dotted* with *root* temporarily at the FRONT of sys.path.

    sys.path must be exactly restored afterwards, even on error, and any
    modules imported from root must be removed from sys.modules so repeated
    calls see fresh code.
    """
    raise NotImplementedError


# -------------------------------------------------------------- tier: Ind
def discover_plugins(directory):
    """Mimic entry-point discovery over a directory of .py files.

    Returns (registry, errors):
      registry: {PLUGIN_NAME: module} for each module exposing PLUGIN_NAME
      errors:   list of (filename, exception) for files that failed to import
    Non-.py files and files starting with '_' are skipped. Failures must NOT
    propagate.
    """
    raise NotImplementedError


def find_import_cycle(modules: dict) -> list | None:
    """Given {module_name: iterable_of_imported_names}, return one cyclic
    chain as a list starting and ending with the same name
    (e.g. ['a', 'b', 'a']), or None when the graph is acyclic.
    Names imported but absent from the dict keys are leaf nodes."""
    raise NotImplementedError
