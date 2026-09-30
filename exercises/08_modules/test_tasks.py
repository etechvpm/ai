"""Grader for module 08.  Run:  pytest exercises/08_modules -q"""

from __future__ import annotations

import sys
import textwrap

import pytest

from _loader import load

tasks = load(__file__)


# ------------------------------------------------------------- beginner
def test_load_module_from_file(tmp_path):
    src = tmp_path / "greetmod.py"
    src.write_text(textwrap.dedent("""
        GREETING = "hi"

        def greet(name):
            return f"{GREETING} {name}"

        if __name__ == "__main__":
            print(greet("world"))
    """), encoding="utf-8")
    mod = tasks.load_module_from_file(src, "greetmod")
    assert mod.GREETING == "hi"
    assert mod.greet("ada") == "hi ada"
    rep = tasks.module_report(mod)
    assert rep["name"] == "greetmod"
    assert rep["has_main_guard"] is True
    assert rep["file"].endswith("greetmod.py")


def test_module_report_without_guard(tmp_path):
    src = tmp_path / "plain.py"
    src.write_text("X = 1\n", encoding="utf-8")
    mod = tasks.load_module_from_file(src, "plain_mod_x")
    assert tasks.module_report(mod)["has_main_guard"] is False


# --------------------------------------------------------- intermediate
def test_build_package_creates_missing_inits(tmp_path):
    root = tasks.build_package(tmp_path / "proj", {
        "pkg/sub/mod.py": "VALUE = 7\n",
        "pkg/__init__.py": "FROM_INIT = True\n",
    })
    assert (root / "pkg" / "__init__.py").is_file()
    assert (root / "pkg" / "sub" / "__init__.py").is_file(), \
        "missing __init__.py must be created automatically"
    assert (root / "pkg" / "sub" / "mod.py").is_file()


def test_import_from_restores_sys_path_and_cache(tmp_path):
    root = tasks.build_package(tmp_path / "p1", {"pkg/mod.py": "V = 1\n"})
    before = list(sys.path)
    mod = tasks.import_from(root, "pkg.mod")
    assert mod.V == 1
    assert sys.path == before, "sys.path must be restored exactly"

    # fresh code on second call: mutate the file (different length, so the
    # bytecode cache cannot look valid), re-import, expect the new value
    (root / "pkg" / "mod.py").write_text("V = 222\n", encoding="utf-8")
    mod2 = tasks.import_from(root, "pkg.mod")
    assert mod2.V == 222, "stale sys.modules entries must be evicted"
    assert "pkg.mod" not in sys.modules


# ------------------------------------------------------------ industry
def test_discover_plugins_collects_and_isolates_failures(tmp_path):
    (tmp_path / "good.py").write_text(
        'PLUGIN_NAME = "good"\nVALUE = 1\n', encoding="utf-8")
    (tmp_path / "alsogood.py").write_text(
        'PLUGIN_NAME = "second"\n', encoding="utf-8")
    (tmp_path / "broken.py").write_text(
        "PLUGIN_NAME = 'broken'\nraise RuntimeError('boom')\n",
        encoding="utf-8")
    (tmp_path / "_private.py").write_text(
        "PLUGIN_NAME = 'skip'\n", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("not python", encoding="utf-8")
    (tmp_path / "noplugname.py").write_text("X = 1\n", encoding="utf-8")

    registry, errors = tasks.discover_plugins(tmp_path)
    assert set(registry) == {"good", "second"}
    assert registry["good"].VALUE == 1
    assert [name for name, _ in errors] == ["broken.py"]
    assert isinstance(errors[0][1], RuntimeError)


@pytest.mark.parametrize("graph,expected", [
    ({"a": ["b"], "b": ["a"]}, ["a", "b", "a"]),
    ({"a": ["b"], "b": ["c"], "c": []}, None),
    ({"a": ["b"], "b": ["c"], "c": ["a"]}, ["a", "b", "c", "a"]),
    ({"a": ["a"]}, ["a", "a"]),
    ({}, None),
    ({"a": ["missing"]}, None),
])
def test_find_import_cycle(graph, expected):
    got = tasks.find_import_cycle(graph)
    if expected is None:
        assert got is None
    else:
        assert got is not None
        assert got[0] == got[-1], "cycle must start and end at the same node"
        assert len(got) == len(expected)
        for a, b in zip(got, got[1:]):
            assert b in graph.get(a, ()), f"edge {a}->{b} not in the graph"
