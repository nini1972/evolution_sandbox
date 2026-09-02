"""Validate the integrity of the NoiseGarden workspace."""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SHARED = ROOT.parent.parent / "shared_space"


def check(condition, message):
    if condition:
        print(f"[PASS] {message}")
        return True
    else:
        print(f"[FAIL] {message}")
        return False


def main():
    ok = True

    # Core documentation
    for doc in ["existential_core.md", "README.md", "PROJECT_SUMMARY.md",
                "evolution_log.md", "manifest.md", "index.html", "build_index.py"]:
        ok &= check((ROOT / doc).exists(), f"Top-level doc exists: {doc}")

    # Cycles: every cycle dir should have an entry file and at least one PNG
    entry_names = ("README.md", "index.html", "dashboard.html", "reflection.md")
    cycle_dirs = sorted(ROOT.glob("cycle_*"))
    ok &= check(len(cycle_dirs) >= 14, f"Found {len(cycle_dirs)} cycle directories")
    for d in cycle_dirs:
        entry = next((d / n for n in entry_names if (d / n).is_file()), None)
        ok &= check(entry is not None,
                    f"{d.name} has entry file ({', '.join(entry_names)}): {entry.name if entry else 'none'}")
        pngs = list(d.glob("*.png"))
        ok &= check(len(pngs) > 0, f"{d.name} has {len(pngs)} PNG outputs")

    # index.html references
    index_html = ROOT / "index.html"
    if index_html.exists():
        text = index_html.read_text()
        imgs = re.findall(r'<img[^>]+src="([^"]+)"', text)
        bad_imgs = [src for src in imgs if not (ROOT / src).exists()]
        ok &= check(len(bad_imgs) == 0,
                    f"All {len(imgs)} images in index.html exist (missing: {bad_imgs})")
        links = re.findall(r'<a[^>]+href="([^"]+)"', text)
        bad_links = []
        for link in links:
            if link.startswith("http"):
                continue
            target = ROOT / link
            if not target.exists():
                bad_links.append(link)
        ok &= check(len(bad_links) == 0,
                    f"All local links in index.html exist (missing: {bad_links})")
    else:
        ok = False
        print("[FAIL] index.html not found")

    # CSV data files for data-producing cycles (10-14)
    data_cycles = [f"cycle_{i:02d}_*" for i in range(10, 15)]
    for pattern in data_cycles:
        for d in ROOT.glob(pattern):
            csvs = list(d.glob("*.csv"))
            ok &= check(len(csvs) >= 1, f"{d.name} has CSV data: {len(csvs)} files")

    # Shared-space trace
    trace = SHARED / "noisegarden_cycle14_trace.md"
    trace_img = SHARED / "noisegarden_c14_plastic_vs_fixed.png"
    ok &= check(trace.is_file(), "Shared-space trace file exists")
    ok &= check(trace_img.is_file(), "Shared-space trace image exists")

    print()
    if ok:
        print("Validation PASSED: all core artifacts are present and consistent.")
        return 0
    else:
        print("Validation FAILED: some expected artifacts are missing.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
