"""Grader for module 18.  Run:  pytest exercises/18_packaging -q"""

from __future__ import annotations

import pytest

from _loader import load

tasks = load(__file__)

PYPROJECT = """
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "acme-reports"
version = "1.4.2"
requires-python = ">=3.11"
dependencies = ["httpx>=0.27", "pydantic>=2.7"]

[project.optional-dependencies]
dev = ["pytest>=8", "ruff"]
postgres = ["asyncpg>=0.29"]

[project.scripts]
acme-report = "acme_reports.cli:main"
"""


# ------------------------------------------------------------- beginner
def test_parse_pyproject_full():
    out = tasks.parse_pyproject(PYPROJECT)
    assert out["name"] == "acme-reports"
    assert out["version"] == "1.4.2"
    assert out["requires_python"] == ">=3.11"
    assert out["dependencies"] == ["httpx>=0.27", "pydantic>=2.7"]
    assert out["extras"]["dev"] == ["pytest>=8", "ruff"]
    assert out["scripts"] == {"acme-report": "acme_reports.cli:main"}


def test_parse_pyproject_defaults_and_errors():
    out = tasks.parse_pyproject("[project]\nname = 'x'\n")
    assert out["version"] is None and out["dependencies"] == []
    assert out["extras"] == {} and out["scripts"] == {}
    assert tasks.parse_pyproject("")["name"] is None
    with pytest.raises(ValueError):
        tasks.parse_pyproject("[project\nname = ")


def test_bump_semver():
    assert tasks.bump("1.2.3", "patch") == "1.2.4"
    assert tasks.bump("1.2.3", "minor") == "1.3.0"
    assert tasks.bump("1.2.3", "major") == "2.0.0"
    assert tasks.bump("0.0.9", "patch") == "0.0.10"
    for bad in [("1.2", "patch"), ("v1.2.3", "minor"), ("1.2.3", "big")]:
        with pytest.raises(ValueError):
            tasks.bump(*bad)


def test_is_newer():
    assert tasks.is_newer("1.10.0", "1.9.9")
    assert tasks.is_newer("2.0", "1.99.99")
    assert not tasks.is_newer("1.2.3", "1.2.3")
    assert not tasks.is_newer("1.2", "1.2.1")
    with pytest.raises(ValueError):
        tasks.is_newer("1.2.beta", "1.2.0")


# --------------------------------------------------------- intermediate
COMMITS = [
    "feat(api): add pagination",
    "fix: handle empty body",
    "docs: readme",
    "chore: bump deps",
    "refactor(core): split module",
    "random message without prefix",
]


def test_classify_commits():
    groups = tasks.classify_commits(COMMITS)
    assert groups["feat"] == ["add pagination"]
    assert groups["fix"] == ["handle empty body"]
    assert groups["docs"] == ["readme"]
    assert groups["chore"] == ["bump deps"]
    assert groups["refactor"] == ["split module"]
    assert groups["other"] == ["random message without prefix"]
    assert groups["breaking"] == []


def test_classify_breaking_forms():
    groups = tasks.classify_commits(["feat!: drop py38",
                                     "feat(x)!: rename",
                                     "fix: y\n\nBREAKING CHANGE: z"])
    assert len(groups["breaking"]) == 3


def test_next_version_rules():
    assert tasks.next_version("1.4.2", COMMITS) == "1.5.0"
    assert tasks.next_version("1.4.2", ["fix: x"]) == "1.4.3"
    assert tasks.next_version("1.4.2", ["feat!: x"]) == "2.0.0"
    assert tasks.next_version("1.4.2", ["random"]) is None
    assert tasks.next_version("1.4.2", []) is None


def test_render_workflow_yaml():
    yml = tasks.render_workflow("CI", ["3.11", "3.12"],
                                ["ruff check .", "pytest"])
    assert "name: CI" in yml
    assert "on:" in yml and "jobs:" in yml
    assert "runs-on: ubuntu-latest" in yml
    assert "strategy:" in yml and "matrix:" in yml
    assert '- "3.11"' in yml and '- "3.12"' in yml
    assert yml.index("- run: ruff check .") < yml.index("- run: pytest")
    assert yml.endswith("\n")
    # every non-empty line uses 2-space indentation steps
    for line in yml.splitlines():
        indent = len(line) - len(line.lstrip(" "))
        assert indent % 2 == 0, f"bad indent: {line!r}"


# ------------------------------------------------------------ industry
def test_make_manifest():
    files = ["src/pkg/__init__.py", "src/pkg/core.py", "tests/test_core.py",
             "README.md", "dist/old.whl", "src/pkg/data/schema.json",
             "src/pkg/junk.pyc"]
    out = tasks.make_manifest(files, ["src/**/*.py", "*.md"],
                              ["*.pyc", "tests/*"])
    assert out == ["README.md", "src/pkg/__init__.py", "src/pkg/core.py"]
    assert tasks.make_manifest(["a.py"], ["*.py"], ["a.py"]) == []
    with pytest.raises(ValueError):
        tasks.make_manifest(["a.py"], [])


def test_resolve_install_order_is_topological_and_deterministic():
    packages = {
        "app": {"requires": ["web", "db"]},
        "web": {"requires": ["core"]},
        "db": {"requires": ["core"]},
        "core": {"requires": []},
    }
    order = tasks.resolve_install_order(packages)
    assert order.index("core") < order.index("web")
    assert order.index("web") < order.index("app")
    assert order.index("db") < order.index("app")
    assert order == ["core", "db", "web", "app"], "alphabetical tie-break"
    assert tasks.resolve_install_order({}) == []


def test_resolve_install_order_errors():
    with pytest.raises(tasks.UnknownDependency) as ei:
        tasks.resolve_install_order({"a": {"requires": ["ghost"]}})
    assert "ghost" in str(ei.value)
    with pytest.raises(tasks.CyclicDependency) as ei2:
        tasks.resolve_install_order({"a": {"requires": ["b"]},
                                     "b": {"requires": ["a"]}})
    assert "a" in str(ei2.value) and "b" in str(ei2.value)


def test_check_pins():
    report = tasks.check_pins(
        ["httpx>=0.27", "pydantic==2.7.0", "rich", "missing==1.0",
         "ok==1.0"],
        {"httpx": "0.27.1", "pydantic": "2.6.0", "rich": "13.0",
         "ok": "1.0"})
    assert report["ok"] == ["httpx", "ok"]
    assert report["mismatched"] == ["pydantic"]
    assert report["missing"] == ["missing"]
    assert report["unpinned"] == ["rich"]


def test_release_plan():
    plan = tasks.release_plan("1.4.2", COMMITS)
    assert plan["current"] == "1.4.2"
    assert plan["next"] == "1.5.0" and plan["bump"] == "minor"
    assert plan["breaking"] is False
    assert plan["changelog"]["feat"] == ["add pagination"]

    plan2 = tasks.release_plan("1.4.2", ["feat!: drop py38", "fix: x"])
    assert (plan2["next"], plan2["bump"], plan2["breaking"]) == \
        ("2.0.0", "major", True)

    plan3 = tasks.release_plan("1.4.2", ["random"])
    assert plan3["next"] == "1.4.2" and plan3["bump"] is None
