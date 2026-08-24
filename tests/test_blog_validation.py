import pathlib
import tempfile
import sys
import datetime

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "scripts"))
import validate_blog_posts as v

def test_parse_frontmatter_valid():
    text = """---
date: 2026-08-25
author: Jane Doe
title: Test Post
abstract: Short abstract
---
# Hello
Body"""
    data, body, err = v.parse_frontmatter(text)
    assert err is None
    assert data["title"] == "Test Post"
    assert data["author"] == "Jane Doe"
    assert body.strip().startswith("# Hello")

def test_missing_required_fields():
    with tempfile.TemporaryDirectory() as td:
        p = pathlib.Path(td) / "2026-08-25-test.md"
        p.write_text("""---
date: 2026-08-25
title: Missing author
abstract: hi
---
Body""")
        errors, _ = v.validate_file(p)
        assert any("author" in e for e in errors)

def test_abstract_length_validation():
    long_abstract = "a" * 1025
    with tempfile.TemporaryDirectory() as td:
        p = pathlib.Path(td) / "2026-08-25-test.md"
        p.write_text(f"""---
date: 2026-08-25
author: Jane Doe
title: Long abstract
abstract: {long_abstract}
---
Body""")
        errors, _ = v.validate_file(p)
        assert any("abstract is 1025" in e for e in errors)
        assert any("1,024" in e for e in errors)

def test_abstract_exact_1024_passes():
    abstract = "a" * 1024
    with tempfile.TemporaryDirectory() as td:
        p = pathlib.Path(td) / "2026-08-25-test.md"
        p.write_text(f"""---
date: 2026-08-25
author: Jane Doe
title: Exact
abstract: {abstract}
---
Body""")
        errors, _ = v.validate_file(p)
        assert not any("abstract is" in e for e in errors)

def test_invalid_date():
    with tempfile.TemporaryDirectory() as td:
        p = pathlib.Path(td) / "2026-08-25-test.md"
        p.write_text("""---
date: 2026-13-40
author: Jane Doe
title: Bad date
abstract: ok
---
Body""")
        errors, _ = v.validate_file(p)
        assert any("invalid date" in e or "YAML parse error" in e for e in errors)

def test_filename_convention():
    with tempfile.TemporaryDirectory() as td:
        p = pathlib.Path(td) / "badname.md"
        p.write_text("""---
date: 2026-08-25
author: Jane Doe
title: Bad name
abstract: ok
---
Body""")
        errors, _ = v.validate_file(p)
        assert any("does not match convention" in e for e in errors)

        good = pathlib.Path(td) / "2026-08-25-good-slug.md"
        good.write_text("""---
date: 2026-08-25
author: Jane Doe
title: Good
abstract: ok
---
Body""")
        errors2, _ = v.validate_file(good)
        assert not any("does not match convention" in e for e in errors2)

def test_slug_duplicate_detection():
    # Simulate duplicate slug detection via script's slug_map logic
    import pathlib
    files = ["content/blog/2026-08-25-hello-world.md", "content/blog/2026-08-26-hello-world.md"]
    # These have same slug different date prefix? Actually slug is hello-world both, should be duplicate per spec (same URL slug)
    # But our logic uses slug after date, so they would be duplicate
    slug_map = {}
    for f in files:
        slug = v.SLUG_RE.match(pathlib.Path(f).name).group(1)
        slug_map.setdefault(slug, []).append(f)
    assert len(slug_map["hello-world"]) == 2

def test_discovery_and_sorting(tmp_path=None):
    # Create temp blog dirs and test sorting
    import tempfile, pathlib
    with tempfile.TemporaryDirectory() as td:
        base = pathlib.Path(td)
        blog = base / "content" / "blog"
        blog.mkdir(parents=True)
        (blog / "2026-08-25-second.md").write_text("""---
date: 2026-08-25
author: A
title: Second
abstract: second
---
Body""")
        (blog / "2026-08-24-first.md").write_text("""---
date: 2026-08-24
author: A
title: First
abstract: first
---
Body""")
        files = sorted(blog.glob("*.md"))
        def get_date(p):
            d, _, _ = v.parse_frontmatter(p.read_text())
            return d["date"]
        sorted_files = sorted(files, key=lambda p: get_date(p), reverse=True)
        assert sorted_files[0].name == "2026-08-25-second.md"

def test_markdown_parseable():
    with tempfile.TemporaryDirectory() as td:
        p = pathlib.Path(td) / "2026-08-25-test.md"
        p.write_text("""---
date: 2026-08-25
author: Jane Doe
title: MD test
abstract: ok
---
# Heading

- list
- items

```python
print("hi")
```""")
        errors, _ = v.validate_file(p)
        assert errors == []

def test_graceful_missing_frontmatter():
    with tempfile.TemporaryDirectory() as td:
        p = pathlib.Path(td) / "2026-08-25-test.md"
        p.write_text("No front matter here")
        errors, _ = v.validate_file(p)
        assert any("Missing front matter" in e for e in errors)
