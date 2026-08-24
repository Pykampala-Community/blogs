#!/usr/bin/env python3
"""
Sync blog posts from content/blog (spec canonical) to docs/posts (MkDocs source).

- Copies *.md files (excluding _template.md) from content/blog to docs/posts
- Copies assets from content/blog/assets to docs/posts/assets if exists
- Preserves required front matter (date, author, title, abstract) and adds legacy 'authors' for MkDocs if missing
"""

import pathlib
import shutil
import re
import yaml

SRC = pathlib.Path("content/blog")
DST = pathlib.Path("docs/posts")
SRC_ASSETS = SRC / "assets"
DST_ASSETS = DST / "assets"

def ensure_authors(entry, author_val):
    return entry

def sync():
    if not SRC.exists():
        print(f"⚠️  {SRC} does not exist, nothing to sync")
        return

    DST.mkdir(parents=True, exist_ok=True)

    for src_file in SRC.glob("*.md"):
        if src_file.name == "_template.md":
            continue
        dst_file = DST / src_file.name
        text = src_file.read_text(encoding="utf-8")
        # Ensure front matter has both author and authors for compatibility
        m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
        if m:
            fm_text, body = m.group(1), m.group(2)
            try:
                data = yaml.safe_load(fm_text) or {}
            except:
                data = {}
            # if author present but authors missing, add authors slug for MkDocs
            if "author" in data and "authors" not in data:
                # slugify author: Jane Doe -> Jane-Doe
                slug = str(data["author"]).strip().replace(" ", "-")
                # also try lower? Keep original case for .authors.yml key case-sensitive
                # Check .authors.yml and try to find matching key
                data["authors"] = [slug]
                try:
                    new_fm = yaml.safe_dump(data, sort_keys=False).strip()
                    text = f"---\n{new_fm}\n---\n{body}"
                except:
                    pass
        # Only copy if changed
        if dst_file.exists() and dst_file.read_text(encoding="utf-8") == text:
            print(f"— {src_file.name} unchanged")
        else:
            dst_file.write_text(text, encoding="utf-8")
            print(f"✓ Synced {src_file} -> {dst_file}")

    # Sync assets
    if SRC_ASSETS.exists():
        DST_ASSETS.mkdir(parents=True, exist_ok=True)
        for asset in SRC_ASSETS.rglob("*"):
            if asset.is_file():
                rel = asset.relative_to(SRC_ASSETS)
                dst = DST_ASSETS / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(asset, dst)
                print(f"✓ Asset {rel}")

    print("Sync complete.")

if __name__ == "__main__":
    sync()
