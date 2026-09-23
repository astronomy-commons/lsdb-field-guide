"""Structural checks for the field guide. Run with: python3 tests/check_markup.py

Deliberately dependency-free, so it works the same on a laptop as in CI.
"""

import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from tools.sync_sidebar import sync  # noqa: E402

# Methods that execute. Listed here so the badge audit is mechanical rather than
# something a reviewer has to remember.
COMPUTES = (
    ".head(", ".compute(", ".tail(", "len(", ".sample(",
    ".plot_points(", ".plot_pixels(", ".plot_coverage(",
    ".to_hats(", ".write_catalog(",
)

ROOT = pathlib.Path(__file__).resolve().parent.parent


def check() -> list[str]:
    problems: list[str] = []
    pages = {p.name: p.read_text() for p in ROOT.glob("*.html")}

    for name, html in pages.items():
        ids = set(re.findall(r'id="([^"]+)"', html))

        # Anchors get pasted into Slack during hack days; they must resolve.
        for href in re.findall(r'href="#([^"]+)"', html):
            if href not in ids:
                problems.append(f"{name}: #{href} has no matching id")

        for href in re.findall(r'href="([^"#:]+\.html)', html):
            if href not in pages:
                problems.append(f"{name}: links to missing page {href}")

        # Cross-page deep links are the ones pasted into Slack; a fragment that
        # points at nothing fails silently in the browser.
        for target, fragment in re.findall(r'href="([^"#:]+\.html)#([^"]+)"', html):
            if target not in pages:
                continue
            if f'id="{fragment}"' not in pages[target]:
                problems.append(f"{name}: links to {target}#{fragment}, which does not exist")

        for src in re.findall(r'(?:src|href)="(assets/[^"]+)"', html):
            if not (ROOT / src).exists():
                problems.append(f"{name}: missing asset {src}")

        for snippet in re.findall(r'<div class="snippet"[^>]*>.*?</pre>', html, re.S):
            attrs = dict(re.findall(r'data-([a-z-]+)="([^"]*)"', snippet))
            body = re.search(r"<pre><code>(.*?)</code>", snippet, re.S).group(1)
            label = re.search(r'snippet__label">([^<]+)', snippet)
            label = label.group(1) if label else "?"

            if "setup" not in attrs or "verify" not in attrs:
                problems.append(f"{name}: snippet ({label}) missing data-setup/data-verify")
            if attrs.get("verify") == "skip" and not attrs.get("skip-reason"):
                problems.append(f"{name}: skipped snippet ({label}) has no data-skip-reason")

            # The badge must match reality in both directions: an unbadged snippet
            # that computes misleads, and a badged one that doesn't cries wolf.
            executes = any(call in body for call in COMPUTES)
            badged = "badge--hot" in snippet
            if executes and not badged:
                problems.append(f"{name}: snippet ({label}) computes but carries no badge")
            if badged and not executes:
                problems.append(f"{name}: snippet ({label}) is badged but nothing executes")

            # Hot-line marks must agree with the badge too. A .hot line has to be
            # a line that actually computes, and it only earns its keep when some
            # line in the snippet is cool -- when every line computes, the badge
            # has already said it and marking them all is noise.
            code_lines = [ln for ln in body.split("\n") if ln.strip()]
            hot_lines = [ln for ln in code_lines if 'class="hot"' in ln]
            all_compute = bool(code_lines) and all(
                any(call in ln for call in COMPUTES) for ln in code_lines
            )
            if hot_lines and not badged:
                problems.append(f"{name}: snippet ({label}) marks a hot line but carries no badge")
            for ln in hot_lines:
                # The opening line of a multi-line marked call is the one that computes.
                if not any(call in ln for call in COMPUTES):
                    problems.append(
                        f"{name}: snippet ({label}) marks a line that does not compute"
                    )
            if badged and not hot_lines and not all_compute:
                problems.append(
                    f"{name}: snippet ({label}) computes on some lines but marks none"
                )

    # The sidebar must list every heading, in order, with the heading's own words.
    for name in sync(write=False):
        problems.append(f"{name}: sidebar is out of sync — run python3 tools/sync_sidebar.py")

    return problems


if __name__ == "__main__":
    found = check()
    print("\n".join(found) if found else "markup + badge audit pass")
    sys.exit(1 if found else 0)
