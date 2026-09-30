#!/usr/bin/env python3
"""Sanity-check generated SVGs: well-formed XML + text inside the viewBox."""
from __future__ import annotations
import glob, os, sys, xml.etree.ElementTree as ET

SVGNS = "{http://www.w3.org/2000/svg}"

def main() -> int:
    bad = 0
    for f in sorted(glob.glob(os.path.join("notes", "figures", "*.svg"))):
        try:
            root = ET.parse(f).getroot()
        except ET.ParseError as e:
            print(f"XML ERROR {f}: {e}"); bad += 1; continue
        W, H = (float(v) for v in root.get("viewBox").split()[2:])
        issues = []
        for tx in root.iter(SVGNS + "text"):
            s = tx.text or ""
            if not s.strip():
                continue
            fs = float(tx.get("font-size", 13))
            mono = "Mono" in (tx.get("font-family") or "")
            wdt = len(s) * fs * (0.62 if mono else 0.548)
            x, y = float(tx.get("x", 0)), float(tx.get("y", 0))
            a = tx.get("text-anchor", "middle")
            x0 = x - wdt / 2 if a == "middle" else (x - wdt if a == "end" else x)
            if x0 < -1 or x0 + wdt > W + 1:
                issues.append(f"X  '{s[:40]}' spans {x0:.0f}..{x0+wdt:.0f} (canvas {W:.0f})")
            if y > H - 1 or y < 6:
                issues.append(f"Y  '{s[:40]}' baseline {y:.0f} (canvas {H:.0f})")
        for r in root.iter(SVGNS + "rect"):
            try:
                x, y = float(r.get("x", 0)), float(r.get("y", 0))
                w, h = float(r.get("width", 0)), float(r.get("height", 0))
            except TypeError:
                continue
            if x + w > W + 1 or y + h > H + 1 or x < -1 or y < -1:
                issues.append(f"RECT {x:.0f},{y:.0f} {w:.0f}x{h:.0f} outside {W:.0f}x{H:.0f}")
        if issues:
            bad += 1
            print(f"CHK {os.path.basename(f)}")
            for i in issues[:6]:
                print("     ", i)
    total = len(glob.glob(os.path.join("notes", "figures", "*.svg")))
    print(f"\n{total} figures checked, {bad} with layout warnings")
    return 1 if bad else 0

if __name__ == "__main__":
    raise SystemExit(main())
