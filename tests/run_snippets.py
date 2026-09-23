"""Execute every runnable snippet on the site.

    python3 tests/run_snippets.py            # all of them
    python3 tests/run_snippets.py do.html    # one page

Snippets tagged data-verify="skip" are not run, but their reasons are printed, so
skips stay visible instead of quietly becoming the majority. This suite hits the
network, so it is meant to be run on a schedule rather than on every edit.
"""

import html as html_mod
import pathlib
import re
import sys
import traceback
import warnings

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from preambles import PREAMBLES  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
SNIPPET = re.compile(r'<div class="snippet"([^>]*)>(.*?)</pre>', re.S)
# Hot-line markup lives inside <pre><code>; strip tags before running the code.
# Tags first, then unescape -- a literal "<" in a snippet is stored as &lt;.
TAG = re.compile(r"<[^>]+>")


def snippets(page):
    text = (ROOT / page).read_text()
    for attrs_raw, body in SNIPPET.findall(text):
        attrs = dict(re.findall(r'data-([a-z-]+)="([^"]*)"', attrs_raw))
        label = re.search(r'snippet__label">([^<]+)', body)
        code = re.search(r"<pre><code>(.*?)</code>", body, re.S)
        yield {
            "setup": attrs.get("setup", "none"),
            "verify": attrs.get("verify", "run"),
            "reason": attrs.get("skip-reason", ""),
            "label": label.group(1) if label else "?",
            "code": html_mod.unescape(TAG.sub("", code.group(1))) if code else "",
        }


def main(pages):
    failures, ran, skipped = [], 0, []

    for page in pages:
        for i, s in enumerate(snippets(page), start=1):
            where = f"{page} #{i} ({s['label']}, setup={s['setup']})"
            if s["verify"] == "skip":
                skipped.append(f"{where}: {s['reason'] or 'NO REASON GIVEN'}")
                continue
            if s["label"] != "python":
                continue

            preamble = PREAMBLES.get(s["setup"])
            if preamble is None:
                failures.append((where, f"unknown data-setup {s['setup']!r}"))
                continue

            ran += 1
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    exec(compile(preamble + "\n" + s["code"], where, "exec"), {})
                print(f"  ok    {where}")
            except Exception:
                line = traceback.format_exc().strip().splitlines()[-1]
                print(f"  FAIL  {where}\n          {line}")
                failures.append((where, line))

    print(f"\nran {ran}, failed {len(failures)}, skipped {len(skipped)}")
    for s in skipped:
        print(f"  skipped {s}")
    if failures:
        print("\nfailures:")
        for where, line in failures:
            print(f"  {where}\n    {line}")
    return 1 if failures else 0


if __name__ == "__main__":
    args = sys.argv[1:] or ["index.html", "do.html", "ask.html"]
    sys.exit(main(args))
