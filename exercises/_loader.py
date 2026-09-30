"""Shared helper for the exercise packs.

Every ``test_tasks.py`` does::

    from _loader import load
    tasks = load(__file__)

``load`` imports ``tasks.py`` from the same folder as the test - or
``solution.py`` instead when the environment variable ``PYCOURSE_SOLUTION=1``
is set, so you can watch the reference answers pass before you start.
"""

from __future__ import annotations

import importlib.util
import os
import pathlib
import sys


def load(test_file: str, name: str | None = None):
    here = pathlib.Path(test_file).resolve().parent
    use_solution = os.environ.get("PYCOURSE_SOLUTION", "") == "1"
    module_name = "solution" if use_solution else "tasks"
    path = here / (module_name + ".py")
    if not path.exists():
        raise FileNotFoundError(f"{path} does not exist")
    unique = f"{here.name}_{module_name}_{id(sys.modules)}"
    spec = importlib.util.spec_from_file_location(unique, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[unique] = mod
    spec.loader.exec_module(mod)
    return mod
