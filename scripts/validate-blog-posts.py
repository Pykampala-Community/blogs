#!/usr/bin/env python3
"""
Validate PyKampala blog posts.

Checks:
- Required front matter: date, author, title, abstract (or legacy author/authors)
- date is valid YYYY-MM-DD
- abstract <= 1024 characters
- filename follows YYYY-MM-DD-slug.md
- no duplicate slugs/URLs
- markdown parseable
"""

import re
import sys
import pathlib
import datetime

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False
    yaml = None

# Central blog directories (primary spec: content/blog, legacy: docs/posts)
BLOG_DIRS = [
    pathlib.Path("content/blog"),
    pathlib.Path("docs/posts"),
]

REQUIRED_FIELDS = ["date", "title", "abstract"]
# author is required but legacy uses authors list, we accept either
AUTHOR_FIELDS = ["author", "authors"]

# Supported categories — extensible; keep in sync with mkdocs.yml categories_allowed
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
# For backward compatibility: allow singular 'category' and handle case-insensitive matching
CATEGORY_FIELDS = ["categories", "category"]

FILENAME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
SLUG_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-(.+)\.md$")

def slugify_category(name: str) -> str:
    """URL-safe slug: lowercased, spaces/underscores -> hyphens, keep alnum and hyphens"""
    s = name.strip().lower()
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"[^a-z0-9-]", "-", s)
    s = re.sub(r"-+", "-", s)
    return s.strip("-")

def category_slug(name: str) -> str:
    return slugify_category(name)

def parse_frontmatter(text: str):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
    if not m:
        return None, text, "Missing front matter (--- delimiters)"
    fm_text, body = m.group(1), m.group(2)
    if HAS_YAML:
        try:
            data = yaml.safe_load(fm_text) or {}
        except Exception as e:
            return None, body, f"YAML parse error: {e}"
    else:
        # minimal parser
        data = {}
        for line in fm_text.splitlines():
            if not line.strip() or line.strip().startswith("#"):
                continue
            if ":" not in line:
                continue
            k, v = line.split(":", 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            data[k] = v
    return data, body, None

def validate_file(path: pathlib.Path):
    errors = []
    warnings = []
    text = path.read_text(encoding="utf-8")
    data, body, err = parse_frontmatter(text)
    if err:
        errors.append(err)
        return errors, warnings

    # Required fields
    for field in REQUIRED_FIELDS:
        if field not in data or data[field] is None or str(data[field]).strip() == "":
            errors.append(f"missing required field '{field}'")

    # Author check (spec requires author singular, but legacy allows authors)
    has_author = any(f in data and str(data[f]).strip() for f in AUTHOR_FIELDS)
    if not has_author:
        errors.append("missing required field 'author' (or 'authors' for legacy)")

    # date validation
    if "date" in data and str(data["date"]).strip():
        date_val = str(data["date"]).strip()
        # yaml may parse date as date object
        if isinstance(data["date"], (datetime.date, datetime.datetime)):
            date_val = data["date"].isoformat()
        try:
            datetime.date.fromisoformat(str(date_val))
        except Exception:
            # try flexible parsing
            try:
                datetime.datetime.strptime(str(date_val), "%Y-%m-%d")
            except Exception:
                errors.append(f"invalid date '{date_val}' — expected YYYY-MM-DD")

    # abstract length
    if "abstract" in data and data["abstract"] is not None:
        abstract = str(data["abstract"])
        if len(abstract) > 1024:
            errors.append(
                f"abstract is {len(abstract)} characters long\n- maximum allowed length is 1,024 characters\n- please shorten the abstract and try again"
            )

    # categories handling — supports 'categories' (array) and legacy singular 'category'
    cats_raw = None
    cats_field = None
    for field in CATEGORY_FIELDS:
        if field in data and data[field] is not None:
            cats_raw = data[field]
            cats_field = field
            break
    if cats_raw is not None:
        # Normalize to list
        if isinstance(cats_raw, str):
            cats_list = [cats_raw]
        elif isinstance(cats_raw, (list, tuple)):
            cats_list = list(cats_raw)
        else:
            errors.append(f"categories field must be a list of strings, got {type(cats_raw).__name__}")
            cats_list = []
        # Validate each category
        seen_lower = set()
        for cat in cats_list:
            if not isinstance(cat, str) or not cat.strip():
                errors.append(f"invalid category '{cat}' — must be non-empty string")
                continue
            cat_stripped = cat.strip()
            lower = cat_stripped.lower()
            if lower in seen_lower:
                warnings.append(f"duplicate category '{cat_stripped}' on this post — deduplicated")
                continue
            seen_lower.add(lower)
            # unknown category — warn, not error (extensible)
            supported_lower = [s.lower() for s in SUPPORTED_CATEGORIES]
            if lower not in supported_lower:
                warnings.append(
                    f"unknown category '{cat_stripped}' — not in supported list {SUPPORTED_CATEGORIES}; handled gracefully but consider adding to SUPPORTED_CATEGORIES"
                )
        # Also warn if categories is not an array but single value was used via 'category' field
        if cats_field == "category":
            warnings.append("using singular 'category' field — prefer 'categories' (array) for consistency")

    # filename convention
    filename = path.name
    if filename == "_template.md":
        # ignore template
        pass
    else:
        if not FILENAME_RE.match(filename):
            errors.append(
                f"filename '{filename}' does not match convention YYYY-MM-DD-slug.md (lowercase, hyphens, e.g. 2026-08-25-building-python-projects.md)"
            )

    # markdown parseable (basic check via python-markdown if available)
    try:
        import markdown
        markdown.markdown(body)
    except ImportError:
        pass
    except Exception as e:
        errors.append(f"markdown parse error: {e}")

    # slug duplicate will be checked globally
    return errors, warnings

def main():
    all_files = []
    for d in BLOG_DIRS:
        if d.exists():
            for p in d.rglob("*.md"):
                # skip template, hidden, and index files (not blog posts)
                if p.name in ("_template.md", "index.md") or p.name.startswith("."):
                    continue
                all_files.append(p)

    # Also check content/blog primary exists
    primary = pathlib.Path("content/blog")
    if not primary.exists():
        print("⚠️  content/blog does not exist — creating it is recommended per spec")
    else:
        # ensure at least one real post
        real = [p for p in primary.glob("*.md") if p.name != "_template.md"]
        if not real:
            print("ℹ️  No posts yet in content/blog (add Markdown files with required front matter)")

    slug_map = {}
    has_errors = False
    per_file_errors = {}

    for path in sorted(all_files):
        # skip writing a blogpost.md legacy that may be intentionally non-conforming for demo? But still report
        errors, warnings = validate_file(path)
        m = SLUG_RE.match(path.name)
        slug = m.group(1) if m else path.stem

        if slug in slug_map:
            slug_map[slug].append(str(path))
        else:
            slug_map[slug] = [str(path)]

        if errors:
            has_errors = True
            per_file_errors[str(path)] = errors
        if warnings:
            for w in warnings:
                print(f"⚠️  {path}: {w}")

    # duplicate slugs — ignore same filename synced across content/blog and docs/posts
    for slug, files in slug_map.items():
        if len(files) > 1:
            # if all files share same basename (synced copy), not a duplicate
            basenames = {pathlib.Path(f).name for f in files}
            if len(basenames) == 1:
                continue
            has_errors = True
            for f in files:
                per_file_errors.setdefault(f, []).append(
                    f"duplicate slug '{slug}' — multiple files would generate same URL: {', '.join(files)}"
                )

    # Pretty output
    if per_file_errors:
        print("\nBlog post validation failed:\n")
        for f, errs in sorted(per_file_errors.items()):
            print(f"{f}")
            for e in errs:
                # handle multi-line abstract error
                for line in e.split("\n"):
                    print(f"- {line.strip()}")
            print("")
        if any("abstract is" in "".join(v) for v in per_file_errors.values()):
            print("Hint: Abstract: Keep this to 1024 characters or fewer. This is displayed as the post summary on the blog index.")
        sys.exit(1)
    else:
        print(f"✅ Validation passed for {len(all_files)} post(s)")
        # Show sorted posts preview
        # Sort by date descending for info
        def get_date(p):
            try:
                txt = pathlib.Path(p).read_text(encoding="utf-8")
                d, _, _ = parse_frontmatter(txt)
                if d and "date" in d:
                    val = d["date"]
                    if isinstance(val, (datetime.date, datetime.datetime)):
                        return val.isoformat()
                    return str(val)
            except: pass
            return "0000-00-00"
        sorted_files = sorted(all_files, key=lambda p: get_date(str(p)), reverse=True)
        if sorted_files:
            print("Posts (newest first):")
            for p in sorted_files[:5]:
                print(f" - {p} ({get_date(str(p))})")
        sys.exit(0)

if __name__ == "__main__":
    main()
