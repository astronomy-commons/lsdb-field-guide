# LSDB Field Guide

A quick reference for [LSDB](https://github.com/astronomy-commons/lsdb), aimed at people
meeting it for the first time at a conference hack day.

**Live site:** https://astronomy-commons.github.io/lsdb-field-guide/

## What this is

A field guide, not documentation. It is deliberately short, and it does not try to cover
the API — [docs.lsdb.io](https://docs.lsdb.io) already does that well. This exists for the
person who sat down an hour ago wanting to do some science, and would rather not spend
that hour reading.

Three pages:

- **Start** (`index.html`) — what this is, and one snippet that gets a plot on screen
- **Do** (`do.html`) — copy-pasteable recipes, phrased as "I want to…"
- **Ask** (`ask.html`) — short answers to foundational questions, phrased as questions

Start exists so that Do can open straight into "I want to…" items. When the starter
lived on Do, you had to scroll past it before seeing anything that completed the
sentence in the heading.

It is also distinct from the [per-event tutorial repos](https://docs.lsdb.io/en/stable/tutorials.html):
those are event-scoped and disposable, this one outlives them.

## Working on it

Plain HTML, CSS, and JavaScript. No build step, no framework, no dependencies.

```bash
python -m http.server 8000
# then open http://localhost:8000
```

Edit the HTML directly and reload. That's the whole workflow.

Two checks, neither of which needs a build:

```bash
python3 tests/check_markup.py    # anchors, assets, compute badges — instant
python3 tests/run_snippets.py    # actually executes every snippet — minutes, hits the network
```

`check_markup.py` is the one to run constantly. `run_snippets.py` executes each
snippet against live `data.lsdb.io` catalogs, so it runs weekly in CI rather than on
every push — a flaky catalog read shouldn't block a CSS change.

### Conventions worth keeping

- **The sidebar is generated, not hand-written.** After adding or renaming a section,
  run `python3 tools/sync_sidebar.py`. It rebuilds each page's sidebar from that page's
  own headings, so the two can't drift; `check_markup.py` fails if they have.
- **Every section has a hand-written `id`.** Links get pasted into Slack during hack days
  and should keep working. Never let an anchor be auto-generated.
- **Snippets that trigger computation carry the `⚡ triggers computation` badge**, and
  nothing else carries a badge. There is deliberately no `lazy` badge: when almost every
  snippet is lazy, saying so on each one is noise, and the loud badge stops being loud.
  Check the badge whenever you touch a snippet — `.head()`, `.compute()`, `len()`, and
  the `plot_*` methods all execute.
- **Snippets have no `>>>` prompts**, so selecting one gives you runnable code.
- **`snippet__src` says "used in", not "from".** These snippets were written and
  executed against live catalogs for this site; they are not copied out of the LSDB
  notebooks. The link points at a notebook where the same operation appears in a
  real workflow. Don't relabel it as provenance unless a snippet is genuinely lifted.
- **Links live in the subsection they serve**, not in one pile at the end of the
  section. Readers stop as soon as they have what they came for, so a link at the
  bottom of a long section is a link most people never see.
- **Snippets carry `data-setup` and `data-verify` attributes** for the verification
  harness. `data-verify="skip"` requires a `data-skip-reason`.

## License

BSD 3-Clause, matching LSDB.
