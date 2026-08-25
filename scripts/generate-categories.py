#!/usr/bin/env python3
"""
Generate category pages for PyKampala blog.

Reads posts from content/blog (primary) and generates:
- docs/categories.md (index of all categories)
- docs/categories/<slug>.md for each category, listing posts in that category

Uses same slugify logic as validate_blog_posts.py for URL consistency.
"""

import pathlib
import re
import sys
import datetime

try:
    import yaml
except ImportError:
    yaml = None

BLOG_DIR = pathlib.Path("content/blog")
OUTPUT_DIR = pathlib.Path("docs/categories")
SUPPORTED_CATEGORIES = [
    "Web",
    "AI and Machine-Learning",
    "Data Science",
    "Cyber Security",
    "Programming",
    "Career",
    "Graphics",
    "Software",
]

def slugify_category(name: str) -> str:
    s = name.strip().lower()
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"[^a-z0-9-]", "-", s)
    s = re.sub(r"-+", "-", s)
    return s.strip("-")

def parse_frontmatter(path: pathlib.Path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
    if not m:
        return {}, text
    fm_text = m.group(1)
    try:
        data = yaml.safe_load(fm_text) or {} if yaml else {}
    except:
        data = {}
    return data, m.group(2)

def main():
    if not BLOG_DIR.exists():
        print(f"⚠️  {BLOG_DIR} not found")
        sys.exit(0)

    # Collect posts
    posts = []
    for p in BLOG_DIR.glob("*.md"):
        if p.name == "_template.md" or p.name.startswith("."):
            continue
        data, _ = parse_frontmatter(p)
        # Get categories (handle both 'categories' and legacy 'category')
        cats = data.get("categories", data.get("category"))
        if cats is None:
            cats = []
        elif isinstance(cats, str):
            cats = [cats]
        elif not isinstance(cats, (list, tuple)):
            cats = []
        # Normalize and dedupe (case-insensitive)
        seen = set()
        norm_cats = []
        for c in cats:
            if not isinstance(c, str) or not c.strip():
                continue
            c = c.strip()
            lower = c.lower()
            if lower not in seen:
                seen.add(lower)
                norm_cats.append(c)
        # Get date for sorting
        date_val = data.get("date", "1970-01-01")
        if isinstance(date_val, (datetime.date, datetime.datetime)):
            date_str = date_val.isoformat()
        else:
            date_str = str(date_val)
        try:
            date_obj = datetime.date.fromisoformat(date_str)
        except:
            try:
                date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            except:
                date_obj = datetime.date(1970,1,1)

        posts.append({
            "path": p,
            "title": data.get("title", p.stem),
            "date": date_str,
            "date_obj": date_obj,
            "author": data.get("author", data.get("authors", "")),
            "abstract": data.get("abstract", ""),
            "categories": norm_cats,
            "slug": p.stem,  # full filename stem
            "url": f"/{p.stem}/",  # will be overridden by mkdocs blog URL, but keep for reference
        })

    # Build category map
    cat_map = {}
    for post in posts:
        for cat in post["categories"]:
            slug = slugify_category(cat)
            if slug not in cat_map:
                # Find canonical name from SUPPORTED or use first seen
                canonical = next((s for s in SUPPORTED_CATEGORIES if s.lower() == cat.lower()), cat)
                cat_map[slug] = {"name": canonical, "slug": slug, "posts": []}
            cat_map[slug]["posts"].append(post)

    # Also include supported categories with zero posts for discoverability
    for cat in SUPPORTED_CATEGORIES:
        slug = slugify_category(cat)
        if slug not in cat_map:
            cat_map[slug] = {"name": cat, "slug": slug, "posts": []}

    # Sort posts within each category by date descending
    for cat in cat_map.values():
        cat["posts"].sort(key=lambda x: x["date_obj"], reverse=True)

    # Sort categories alphabetically
    sorted_cats = sorted(cat_map.values(), key=lambda x: x["name"].lower())

    # Ensure output dir
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Generate docs/categories.md index
    index_path = pathlib.Path("docs/categories.md")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write("# Categories\n\n")
        f.write('<div class="metro-divider" style="width:48px; height:4px; background: var(--brand-primary); margin: 16px 0;"></div>\n\n')
        f.write("Browse posts by category. Each category shows all posts assigned to it — a post in multiple categories appears in each.\n\n")
        f.write('<div style="margin: 20px 0; display:flex; flex-wrap:wrap; gap:10px;">\n')
        for cat in sorted_cats:
            count = len(cat["posts"])
            # From docs/categories.md (site/categories/) link to site/categories/<slug>/ is "<slug>/"
            f.write(f'  <a href="{cat["slug"]}/" class="md-button" style="border:1px solid #E8E8E6; background:#fff; color:#000; font-weight:700; padding:8px 14px; border-radius:2px; text-decoration:none;">{cat["name"]} <span style="background: var(--brand-primary); color:#000; padding:2px 6px; border-radius:2px; font-size:0.75em; margin-left:6px;">{count}</span></a>\n')
        f.write('</div>\n\n')

        f.write("## All Categories\n\n")
        f.write("| Category | Posts | URL |\n")
        f.write("|----------|-------|-----|\n")
        for cat in sorted_cats:
            slug = cat["slug"]
            count = len(cat["posts"])
            url = f"/categories/{slug}/"
            # Markdown link from docs/categories.md (site/categories/) to site/categories/<slug>/ is "categories/<slug>.md" for source (docs/categories.md -> docs/categories/<slug>.md)
            f.write(f"| [{cat['name']}](categories/{slug}.md) | {count} | `{url}` |\n")
        f.write("\n")
        f.write("> **For authors:** add categories in front matter:\n>\n> ```yaml\n> categories:\n>   - AI and Machine-Learning\n>   - Programming\n> ```\n")
        f.write("\n---\n\n")
        f.write("[← Back to Blog](index.md)\n")

    print(f"✓ Generated {index_path} with {len(sorted_cats)} categories")

    # Generate individual category pages
    for cat in sorted_cats:
        slug = cat["slug"]
        name = cat["name"]
        posts_in_cat = cat["posts"]
        out_path = OUTPUT_DIR / f"{slug}.md"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(f"# {name}\n\n")
            f.write('<div class="metro-divider" style="width:48px; height:4px; background: var(--brand-primary); margin: 16px 0;"></div>\n\n')
            f.write(f"**Category:** `{name}`  •  **Slug:** `{slug}`  •  **Posts:** {len(posts_in_cat)}\n\n")
            f.write(f"[← All Categories](../categories.md)  •  [← Blog](../index.md)  •  [← Main Site](https://pykampala-community.github.io/)\n\n")
            f.write("---\n\n")
            if not posts_in_cat:
                f.write(f"*No posts yet in **{name}**.*\n\n")
                f.write("Be the first to contribute — see [`content/blog/_template.md`](https://github.com/Pykampala-Community/blogs/blob/main/content/blog/_template.md).\n")
            else:
                f.write(f"Showing **{len(posts_in_cat)} post(s)** in **{name}** — sorted newest first.\n\n")
                for post in posts_in_cat:
                    # Find the corresponding docs/posts file for link
                    # The blog post URL is typically /posts/<slug>/ or /<date>/<slug>/ — we link via relative to docs/posts
                    # For simplicity, link to the blog post via its date/slug URL pattern used by Material
                    # Material with blog_dir posts and post_url_format {date}/{slug} gives /posts/2026/08/25/slug/
                    # But we can also link directly to the markdown file path for robustness
                    # Use absolute URL to blog post as /posts/<filename>/
                    post_file = post["path"].name
                    # Try to find the post in docs/posts for link
                    # Link using mkdocs blog URL: use posts/<filename> without extension
                    # Material will resolve correctly
                    f.write(f"### [{post['title']}](../posts/{post_file})\n\n")
                    f.write(f"**{post['author']}** · {post['date']}\n\n")
                    if post['abstract']:
                        # Truncate abstract for preview
                        abs_text = post['abstract'][:200].strip()
                        f.write(f"{abs_text}  \n")
                    # Show all categories for this post as clickable tags
                    if post['categories']:
                        tags = " ".join([f"[`{c}`](./{slugify_category(c)}.md)" for c in post['categories']])
                        f.write(f"*Categories: {tags}*\n\n")
                    f.write(f"[Read →](../posts/{post_file})\n\n")
                    f.write("---\n\n")
            f.write("\n[← All Categories](../categories.md) | [← Blog](../index.md)\n")
        print(f"✓ Generated {out_path} ({len(posts_in_cat)} posts)")

    # Also ensure docs/categories/index.md is not needed — we use docs/categories.md as index
    # But mkdocs needs navigation; ensure no stray files
    print(f"Done. Categories: {len(cat_map)}, Posts: {len(posts)}")

if __name__ == "__main__":
    main()
