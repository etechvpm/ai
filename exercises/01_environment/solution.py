"""Module 01 - reference solutions.  Read only after a genuine attempt."""

from __future__ import annotations

import contextlib
import dis
import io
import pathlib
import sys

# ------------------------------------------------------------------ tier: B


def interpreter_info() -> dict:
    return {
        "version": tuple(sys.version_info[:3]),
        "executable": str(pathlib.Path(sys.executable).resolve()),
        "in_venv": sys.prefix != sys.base_prefix,
    }


PROGRAM = 'print("Hello, industry.")\n'


def write_first_program(path) -> str:
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(PROGRAM, encoding="utf-8")
    return PROGRAM


# -------------------------------------------------------------- tier: I


def inspect_bytecode(source: str):
    code = compile(source, "<exercise>", "exec")
    opnames = [instr.opname for instr in dis.get_instructions(code)]
    return tuple(code.co_consts), opnames


def is_constant_folded(source: str) -> bool:
    _, opnames = inspect_bytecode(source)
    return not any(op.startswith("BINARY_") for op in opnames)


# -------------------------------------------------------------- tier: Ind

PYPROJECT = """\
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "myproject"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = []

[project.optional-dependencies]
dev = ["pytest", "ruff", "mypy"]
"""

GITIGNORE = """\
.venv/
__pycache__/
*.pyc
.pytest_cache/
dist/
build/
"""

SMOKE = """\
def test_ok() -> None:
    assert True
"""


def make_project_skeleton(root) -> None:
    root = pathlib.Path(root)
    pkg = root / "src" / "myproject"
    tests = root / "tests"
    pkg.mkdir(parents=True, exist_ok=True)
    tests.mkdir(parents=True, exist_ok=True)
    (root / "pyproject.toml").write_text(PYPROJECT, encoding="utf-8")
    (root / ".gitignore").write_text(GITIGNORE, encoding="utf-8")
    (root / "README.md").write_text("# myproject\n", encoding="utf-8")
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    (pkg / "py.typed").write_text("", encoding="utf-8")
    (tests / "test_smoke.py").write_text(SMOKE, encoding="utf-8")


def validate_project(root) -> list[str]:
    root = pathlib.Path(root)
    problems: list[str] = []

    pp = root / "pyproject.toml"
    if not pp.is_file():
        problems.append("missing pyproject.toml")
    elif "[project]" not in pp.read_text(encoding="utf-8"):
        problems.append("pyproject.toml has no [project] table")

    if not (root / "src" / "myproject" / "__init__.py").is_file():
        problems.append("missing src/myproject/__init__.py")
    if not (root / "src" / "myproject" / "py.typed").is_file():
        problems.append("missing src/myproject/py.typed")

    smoke = root / "tests" / "test_smoke.py"
    if not smoke.is_file():
        problems.append("missing tests/test_smoke.py")
    elif "def test_ok" not in smoke.read_text(encoding="utf-8"):
        problems.append("missing tests/test_smoke.py")

    gi = root / ".gitignore"
    if not gi.is_file():
        problems.append(".gitignore does not ignore .venv/")
        problems.append(".gitignore does not ignore __pycache__/")
    else:
        text = gi.read_text(encoding="utf-8")
        if ".venv/" not in text:
            problems.append(".gitignore does not ignore .venv/")
        if "__pycache__/" not in text:
            problems.append(".gitignore does not ignore __pycache__/")
    return problems
