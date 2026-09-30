"""Module 18 - Packaging & CI.  Reference solutions."""

from __future__ import annotations

import fnmatch
import re
import tomllib

TYPES = ("feat", "fix", "docs", "refactor", "chore")
BUCKETS = TYPES + ("breaking", "other")


# ------------------------------------------------------------------ tier: B
def parse_pyproject(text: str) -> dict:
    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        raise ValueError(f"invalid pyproject.toml: {exc}") from exc
    project = data.get("project", {})
    return {
        "name": project.get("name"),
        "version": project.get("version"),
        "requires_python": project.get("requires-python"),
        "dependencies": list(project.get("dependencies", [])),
        "extras": {k: list(v) for k, v in
                   project.get("optional-dependencies", {}).items()},
        "scripts": dict(project.get("scripts", {})),
    }


def _parse_semver(version: str) -> tuple[int, int, int]:
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", version.strip())
    if not match:
        raise ValueError(f"not a semver version: {version!r}")
    return tuple(int(g) for g in match.groups())  # type: ignore[return-value]


def bump(version: str, part: str) -> str:
    major, minor, patch = _parse_semver(version)
    if part == "major":
        return f"{major + 1}.0.0"
    if part == "minor":
        return f"{major}.{minor + 1}.0"
    if part == "patch":
        return f"{major}.{minor}.{patch + 1}"
    raise ValueError(f"unknown part: {part!r}")


def _components(version: str) -> tuple[int, ...]:
    parts = version.strip().split(".")
    out = []
    for p in parts:
        if not p.isdigit():
            raise ValueError(f"non-numeric version component: {p!r}")
        out.append(int(p))
    return tuple(out)


def is_newer(a: str, b: str) -> bool:
    ca, cb = _components(a), _components(b)
    size = max(len(ca), len(cb))
    ca += (0,) * (size - len(ca))
    cb += (0,) * (size - len(cb))
    return ca > cb


# -------------------------------------------------------------- tier: I
def classify_commits(messages) -> dict:
    out: dict = {bucket: [] for bucket in BUCKETS}
    for raw in messages:
        message = str(raw).strip()
        subject = message.splitlines()[0] if message else ""
        body = message
        breaking = subject.endswith("!") or "!" in subject.split(":")[0] \
            or "BREAKING CHANGE" in body
        match = re.match(r"([a-z]+)(\([^)]*\))?!?:\s*(.*)$", subject)
        kind = match.group(1) if match else None
        text = match.group(3) if match else subject
        if breaking:
            out["breaking"].append(text or subject)
        elif kind in TYPES:
            out[kind].append(text)
        else:
            out["other"].append(subject)
    return out


def next_version(current: str, messages) -> str | None:
    groups = classify_commits(messages)
    if groups["breaking"]:
        return bump(current, "major")
    if groups["feat"]:
        return bump(current, "minor")
    if any(groups[t] for t in ("fix", "docs", "refactor", "chore")):
        return bump(current, "patch")
    return None


def render_workflow(name: str, py_versions, steps) -> str:
    versions = list(py_versions)
    lines = [
        f"name: {name}",
        "on:",
        "  push:",
        "    branches: [main]",
        "  pull_request:",
        "jobs:",
        "  test:",
        "    runs-on: ubuntu-latest",
        "    strategy:",
        "      matrix:",
        "        python-version:",
    ]
    lines += [f'          - "{v}"' for v in versions]
    lines += [
        "    steps:",
        "      - uses: actions/checkout@v4",
        "      - uses: actions/setup-python@v5",
        "        with:",
        '          python-version: "${{ matrix.python-version }}"',
        "      - run: pip install -e '.[dev]'",
    ]
    lines += [f"      - run: {step}" for step in steps]
    return "\n".join(lines) + "\n"


# -------------------------------------------------------------- tier: Ind
class CyclicDependency(Exception):
    pass


class UnknownDependency(Exception):
    pass


def make_manifest(files, include, exclude=()) -> list:
    include = list(include)
    if not include:
        raise ValueError("include must not be empty")
    exclude = list(exclude)

    def wanted(path: str, globs) -> bool:
        return any(fnmatch.fnmatch(path, g) or
                   fnmatch.fnmatch(path.rsplit("/", 1)[-1], g)
                   for g in globs)

    return sorted({p for p in files
                   if wanted(p, include) and not wanted(p, exclude)})


def resolve_install_order(packages) -> list:
    indegree = {name: 0 for name in packages}
    for name, meta in packages.items():
        for dep in meta.get("requires", []):
            if dep not in indegree:
                raise UnknownDependency(dep)
            indegree[name] += 1
    ready = sorted(n for n, d in indegree.items() if d == 0)
    order: list = []
    while ready:
        node = ready.pop(0)
        order.append(node)
        for name, meta in packages.items():
            if node in meta.get("requires", []):
                indegree[name] -= 1
                if indegree[name] == 0:
                    ready.append(name)
        ready.sort()
    if len(order) != len(packages):
        stuck = sorted(n for n, d in indegree.items() if d > 0)
        raise CyclicDependency(f"cyclic dependencies: {', '.join(stuck)}")
    return order


_SPEC = re.compile(r"^\s*([A-Za-z0-9_.\-]+)\s*(==|>=|<=|~=|!=|>|<)?\s*(.*)$")


def check_pins(requirements, lock) -> dict:
    report = {"ok": [], "mismatched": [], "missing": [], "unpinned": []}
    for req in requirements:
        match = _SPEC.match(req)
        if not match:
            raise ValueError(f"cannot parse requirement: {req!r}")
        name, op, spec = match.group(1), match.group(2), match.group(3).strip()
        locked = lock.get(name)
        if op is None or not spec:
            report["unpinned"].append(name)
        elif locked is None:
            report["missing"].append(name)
        elif op == "==" and locked != spec:
            report["mismatched"].append(name)
        else:
            report["ok"].append(name)
    for key in report:
        report[key].sort()
    return report


def release_plan(current: str, messages) -> dict:
    groups = classify_commits(messages)
    nxt = next_version(current, messages)
    if groups["breaking"]:
        kind = "major"
    elif groups["feat"]:
        kind = "minor"
    elif any(groups[t] for t in ("fix", "docs", "refactor", "chore")):
        kind = "patch"
    else:
        kind = None
    return {"current": current, "next": nxt or current, "bump": kind,
            "changelog": groups, "breaking": bool(groups["breaking"])}
