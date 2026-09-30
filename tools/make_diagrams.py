#!/usr/bin/env python3
"""Generate every SVG figure used by the course into notes/figures/.

    python tools/make_diagrams.py            # build all
    python tools/make_diagrams.py gil        # build only names containing 'gil'

Regenerate after editing tools/diagrams_*.py.  The Markdown notes reference
these files as ``![caption](figures/<name>.svg)``; tools/build_site.py inlines
them into the website so they inherit the site's dark/light theme.
"""

from __future__ import annotations

import os
import sys
import time
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import diagrams_a
import diagrams_b
import diagrams_c
import diagrams_d

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "notes", "figures")

ALL: dict[str, object] = {}
ALL.update(diagrams_a.DIAGRAMS)
ALL.update(diagrams_b.DIAGRAMS)
ALL.update(diagrams_c.DIAGRAMS)
ALL.update(diagrams_d.DIAGRAMS)


def main(argv: list[str]) -> int:
    os.makedirs(OUT, exist_ok=True)
    wanted = [a for a in argv if not a.startswith("-")]
    names = [n for n in ALL if not wanted or any(w in n for w in wanted)]
    ok = fail = 0
    t0 = time.perf_counter()
    for name in sorted(names):
        fn = ALL[name]
        dest = os.path.join(OUT, name)
        try:
            fn(dest)
            size = os.path.getsize(dest)
            print(f"  \u2713 {name:<34} {size / 1024:6.1f} KiB")
            ok += 1
        except Exception:
            print(f"  \u2717 {name}")
            traceback.print_exc()
            fail += 1
    dt = (time.perf_counter() - t0) * 1000
    print(f"\n{ok} figure(s) written, {fail} failed  ({dt:.0f} ms)")
    print(f"output: {OUT}")
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
