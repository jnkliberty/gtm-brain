#!/usr/bin/env python3
"""Check the link graph of the brain. Standard library only.

Usage: python3 scripts/graph_check.py [--root DIR] | --self-test

Exits 1 when a relative link in a Markdown file under brain/ or skills/ does not resolve, or when a
file under brain/ cannot be reached from brain/index.md by following links. A link to a folder
reaches every file inside it. Only inline links count, so a reference-style definition ([id]: path)
is reported with a request to use an inline link. Links inside code (fenced or inline), external
URLs, and bare #anchors are skipped; a ?query or #fragment is dropped and %-escapes are decoded
before the path is checked.
"""
import argparse
import os
import re
import sys
import tempfile
from pathlib import Path
from urllib.parse import unquote, urlsplit

INLINE = re.compile(r"\]\(\s*(<[^>]*>|[^)\s]+)")
REFDEF = re.compile(r"^ {0,3}\[(?!\^)([^\]]+)\]:", re.M)
# A fenced block, or an inline code span closed by a backtick run of the same length.
CODE = re.compile(r"^ {0,3}(`{3,}|~{3,}).*?^ {0,3}\1|(?<!`)(`+)(?!`)[^\n]*?(?<!`)\2(?!`)", re.S | re.M)


def text_of(page):
    """A page's Markdown with fenced blocks and inline code removed."""
    return CODE.sub("", page.read_text(encoding="utf-8"))


def links(page):
    """Where each relative inline link in one Markdown file points, as a path."""
    found = []
    for raw in INLINE.findall(text_of(page)):
        url = urlsplit(raw.strip("<>"))
        if not (url.scheme or url.netloc) and url.path:
            found.append(Path(os.path.normpath(page.parent / unquote(url.path))))
    return found


def reached(root):
    """Every file brain/index.md reaches through pages under brain/."""
    brain, seen, todo = root / "brain", set(), [root / "brain" / "index.md"]
    while todo:
        page = todo.pop()
        if page not in seen and page.exists():
            seen.add(page)
            if page.suffix == ".md" and brain in page.parents:
                for dest in links(page):
                    todo += list(dest.rglob("*")) if dest.is_dir() else [dest]
    return seen


def problems(root):
    pages = [p for folder in ("brain", "skills") for p in sorted((root / folder).rglob("*.md"))]
    seen = reached(root)
    broken = [f"{p.relative_to(root)}: broken link {os.path.relpath(t, root)}" for p in pages for t in links(p) if not t.exists()]
    refs = [f"{p.relative_to(root)}: reference-style link [{label}]; use an inline link" for p in pages for label in REFDEF.findall(text_of(p))]
    lost = [f"{p.relative_to(root)}: not reachable from brain/index.md" for p in sorted((root / "brain").rglob("*")) if p.is_file() and p not in seen]
    return broken + refs + lost


def self_test():
    good = {
        "brain/index.md": "[a](a.md) [d](data/) [w](https://x.example) [p](//x.example/a) [t](#t)\n"
                          "[^1]: A footnote, not a link.\n"
                          "```\n[skip](nope.md)\n```\n~~~\n[skip](nope.md)\n~~~\n"
                          "See `[skip](code.md)` and ``[skip](code.md)``.\n",
        "brain/a.md": "[b](b.md#part) [q](b.md?raw=1) [ang](<b.md>) [enc](%62.md)",
        "brain/b.md": "", "brain/data/x.csv": "",
        "skills/s/SKILL.md": "[i](../../brain/index.md)",
    }
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for rel, text in good.items():
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_text(text, encoding="utf-8")
        assert problems(root) == [], problems(root)
        (root / "brain/orphan.md").write_text("", encoding="utf-8")
        (root / "brain/code.md").write_text("", encoding="utf-8")  # named only inside code in the index
        (root / "skills/s/SKILL.md").write_text("[g](../../brain/gone.md) [r][ref]\n\n[ref]: ../../brain/index.md\n", encoding="utf-8")
        assert problems(root) == ["skills/s/SKILL.md: broken link brain/gone.md",
                                  "skills/s/SKILL.md: reference-style link [ref]; use an inline link",
                                  "brain/code.md: not reachable from brain/index.md",
                                  "brain/orphan.md: not reachable from brain/index.md"], problems(root)
    print("all self-tests passed")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Check that brain/ links resolve and brain/index.md reaches every brain file.")
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)
    if args.self_test:
        return self_test()
    found = problems(args.root)
    print("\n".join(found) or "graph ok")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
