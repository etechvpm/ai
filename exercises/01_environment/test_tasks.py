"""Grader for module 01.  Run:  pytest exercises/01_environment -q"""

from __future__ import annotations

import pathlib
import subprocess
import sys

import pytest

from _loader import load

tasks = load(__file__)


# ------------------------------------------------------------- beginner
def test_interpreter_info_keys_and_types():
    info = tasks.interpreter_info()
    assert set(info) == {"version", "executable", "in_venv"}
    assert isinstance(info["version"], tuple) and len(info["version"]) == 3
    assert all(isinstance(n, int) for n in info["version"])
    assert info["version"] == tuple(sys.version_info[:3])
    assert isinstance(info["executable"], str)
    assert pathlib.Path(info["executable"]).is_absolute()
    assert isinstance(info["in_venv"], bool)


def test_write_first_program_runs(tmp_path):
    target = tmp_path / "sub" / "hello.py"
    text = tasks.write_first_program(target)
    assert target.is_file(), "the file was not created (parents included)"
    assert target.read_text(encoding="utf-8") == text
    out = subprocess.run([sys.executable, str(target)],
                         capture_output=True, text=True, check=True)
    assert out.stdout.strip() == "Hello, industry."


# --------------------------------------------------------- intermediate
def test_inspect_bytecode_returns_consts_and_opnames():
    consts, ops = tasks.inspect_bytecode("x = 1")
    assert isinstance(consts, tuple) and 1 in consts
    assert isinstance(ops, list) and ops
    assert all(isinstance(o, str) for o in ops)
    assert "STORE_NAME" in ops and "LOAD_CONST" in ops


@pytest.mark.parametrize("src,expected", [
    ("x = 1 + 2", True),
    ("x = 2 * 3 - 4", True),
    ("x = a + 2", False),
    ("y = n * n", False),
])
def test_constant_folding_detection(src, expected):
    assert tasks.is_constant_folded(src) is expected


# ------------------------------------------------------------ industry
def test_make_project_skeleton_creates_tree(tmp_path):
    root = tmp_path / "proj"
    tasks.make_project_skeleton(root)
    for rel in ("pyproject.toml", ".gitignore", "README.md",
                "src/myproject/__init__.py", "src/myproject/py.typed",
                "tests/test_smoke.py"):
        assert (root / rel).is_file(), f"missing {rel}"
    assert "[project]" in (root / "pyproject.toml").read_text()


def test_validate_project_clean_skeleton(tmp_path):
    root = tmp_path / "good"
    tasks.make_project_skeleton(root)
    assert tasks.validate_project(root) == []


def test_validate_project_detects_every_break(tmp_path):
    root = tmp_path / "bad"
    root.mkdir()
    problems = tasks.validate_project(root)
    assert "missing pyproject.toml" in problems
    assert "missing src/myproject/__init__.py" in problems
    assert "missing src/myproject/py.typed" in problems
    assert "missing tests/test_smoke.py" in problems

    tasks.make_project_skeleton(root)
    (root / "src" / "myproject" / "py.typed").unlink()
    gi = root / ".gitignore"
    gi.write_text("*.pyc\n", encoding="utf-8")
    (root / "pyproject.toml").write_text("[tool.nothing]\n", encoding="utf-8")
    problems = tasks.validate_project(root)
    assert "pyproject.toml has no [project] table" in problems
    assert "missing src/myproject/py.typed" in problems
    assert ".gitignore does not ignore .venv/" in problems
    assert ".gitignore does not ignore __pycache__/" in problems
