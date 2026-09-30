"""Module 08 - reference solutions."""

from __future__ import annotations

import importlib.util
import inspect
import pathlib
import sys

# ------------------------------------------------------------------ tier: B


def load_module_from_file(path, name: str):
    path = pathlib.Path(path)
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path} as {name!r}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop(name, None)
        raise
    return module


def module_report(mod) -> dict:
    file = getattr(mod, "__file__", None)
    has_guard = False
    if file:
        try:
            source = pathlib.Path(file).read_text(encoding="utf-8")
        except OSError:
            source = ""
        has_guard = 'if __name__ == "__main__"' in source or \
                    "if __name__ == '__main__'" in source
    return {"name": mod.__name__,
            "file": str(pathlib.Path(file).resolve()) if file else None,
            "has_main_guard": has_guard}


# -------------------------------------------------------------- tier: I
def build_package(root, files: dict) -> pathlib.Path:
    root = pathlib.Path(root)
    dirs_needing_init = set()
    for rel in files:
        parts = pathlib.PurePosixPath(rel).parts
        for depth in range(1, len(parts)):      # every ancestor dir
            dirs_needing_init.add("/".join(parts[:depth]))
    for rel, source in files.items():
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(source, encoding="utf-8")
    for d in sorted(dirs_needing_init):
        init = root / d / "__init__.py"
        if not init.exists():
            init.parent.mkdir(parents=True, exist_ok=True)
            init.write_text("", encoding="utf-8")
    return root


def import_from(root, dotted: str):
    import importlib
    root = str(pathlib.Path(root).resolve())
    imported = []
    importlib.invalidate_caches()
    sys.path.insert(0, root)
    try:
        module = importlib.import_module(dotted)
        # remember everything that came from root so we can evict it
        for name, mod in list(sys.modules.items()):
            file = getattr(mod, "__file__", None) or ""
            if file.startswith(root):
                imported.append(name)
        return module
    finally:
        sys.path.remove(root)
        for name in imported:
            sys.modules.pop(name, None)


# -------------------------------------------------------------- tier: Ind
def discover_plugins(directory):
    directory = pathlib.Path(directory)
    registry: dict = {}
    errors: list = []
    for path in sorted(directory.glob("*.py")):
        if path.name.startswith("_"):
            continue
        name = f"_plugin_{path.stem}"
        try:
            module = load_module_from_file(path, name)
        except Exception as exc:            # noqa: BLE001 - collect, don't raise
            errors.append((path.name, exc))
            continue
        plugin_name = getattr(module, "PLUGIN_NAME", None)
        if plugin_name is not None:
            registry[plugin_name] = module
    return registry, errors


def find_import_cycle(modules: dict):
    WHITE, GREY, BLACK = 0, 1, 2
    colour: dict = {}
    stack: list = []

    def visit(node):
        colour[node] = GREY
        stack.append(node)
        for nxt in modules.get(node, ()):
            state = colour.get(nxt, WHITE)
            if state == GREY:
                return stack[stack.index(nxt):] + [nxt]
            if state == WHITE:
                found = visit(nxt)
                if found:
                    return found
        stack.pop()
        colour[node] = BLACK
        return None

    for node in list(modules):
        if colour.get(node, WHITE) == WHITE:
            found = visit(node)
            if found:
                return found
    return None
