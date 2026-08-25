import pathlib
import tempfile
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "scripts"))
import validate_blog_posts as v

def test_single_category():
    with tempfile.TemporaryDirectory() as td:
        p = pathlib.Path(td) / "2026-08-25-test.md"
        p.write_text("""---
date: 2026-08-25
author: Jane Doe
title: Single Cat
abstract: ok
categories:
  - Programming
---
Body""")
        errors, warnings = v.validate_file(p)
        assert errors == []

def test_multiple_categories():
    with tempfile.TemporaryDirectory() as td:
        p = pathlib.Path(td) / "2026-08-25-test.md"
        p.write_text("""---
date: 2026-08-25
author: Jane Doe
title: Multi Cat
abstract: ok
categories:
  - AI and Machine-Learning
  - Programming
  - Web
---
Body""")
        errors, warnings = v.validate_file(p)
        assert errors == []
        # Check that categories are parsed correctly
        text = p.read_text()
        data, _, _ = v.parse_frontmatter(text)
        assert data["categories"] == ["AI and Machine-Learning", "Programming", "Web"]

def test_missing_categories_no_error():
    with tempfile.TemporaryDirectory() as td:
        p = pathlib.Path(td) / "2026-08-25-test.md"
        p.write_text("""---
date: 2026-08-25
author: Jane Doe
title: No Cats
abstract: ok
---
Body""")
        errors, warnings = v.validate_file(p)
        # Missing categories should not cause error
        assert not any("categories" in e.lower() for e in errors)

def test_unknown_category_warning():
    with tempfile.TemporaryDirectory() as td:
        p = pathlib.Path(td) / "2026-08-25-test.md"
        p.write_text("""---
date: 2026-08-25
author: Jane Doe
title: Unknown
abstract: ok
categories:
  - UnknownCat
---
Body""")
        errors, warnings = v.validate_file(p)
        # Unknown should be warning, not error
        assert errors == []
        assert any("unknown category" in w for w in warnings)

def test_duplicate_category_warning():
    with tempfile.TemporaryDirectory() as td:
        p = pathlib.Path(td) / "2026-08-25-test.md"
        p.write_text("""---
date: 2026-08-25
author: Jane Doe
title: Dup
abstract: ok
categories:
  - Programming
  - programming
---
Body""")
        errors, warnings = v.validate_file(p)
        assert any("duplicate category" in w for w in warnings)

def test_category_slug_generation():
    assert v.slugify_category("AI and Machine-Learning") == "ai-and-machine-learning"
    assert v.slugify_category("Data Science") == "data-science"
    assert v.slugify_category("Web") == "web"
    assert v.slugify_category("Cyber Security") == "cyber-security"
    assert v.category_slug("Programming") == "programming"

def test_singular_category_field():
    with tempfile.TemporaryDirectory() as td:
        p = pathlib.Path(td) / "2026-08-25-test.md"
        p.write_text("""---
date: 2026-08-25
author: Jane Doe
title: Single
abstract: ok
category: Web
---
Body""")
        errors, warnings = v.validate_file(p)
        assert errors == []
        assert any("singular" in w for w in warnings)

def test_invalid_category_type():
    with tempfile.TemporaryDirectory() as td:
        p = pathlib.Path(td) / "2026-08-25-test.md"
        p.write_text("""---
date: 2026-08-25
author: Jane Doe
title: Bad
abstract: ok
categories: 123
---
Body""")
        errors, _ = v.validate_file(p)
        assert any("must be a list" in e for e in errors)

def test_category_filtering_and_multiple_listings():
    # Simulate category filtering: post with multiple categories should appear in each
    import tempfile, pathlib
    with tempfile.TemporaryDirectory() as td:
        base = pathlib.Path(td)
        blog = base / "content" / "blog"
        blog.mkdir(parents=True)
        (blog / "2026-08-25-post1.md").write_text("""---
date: 2026-08-25
author: A
title: Post1
abstract: a
categories:
  - Programming
  - Web
---
Body""")
        (blog / "2026-08-26-post2.md").write_text("""---
date: 2026-08-26
author: A
title: Post2
abstract: a
categories:
  - Programming
---
Body""")
        # Simulate cat_map building as in generate-categories.py
        posts = []
        for p in blog.glob("*.md"):
            text = p.read_text()
            data, _, _ = v.parse_frontmatter(text)
            cats = data.get("categories", [])
            if isinstance(cats, str):
                cats = [cats]
            posts.append({"title": data["title"], "categories": cats, "date": data["date"]})
        # Filter for Programming
        prog_posts = [p for p in posts if any(c.lower() == "programming" for c in p["categories"])]
        assert len(prog_posts) == 2
        # Filter for Web
        web_posts = [p for p in posts if any(c.lower() == "web" for c in p["categories"])]
        assert len(web_posts) == 1
        assert web_posts[0]["title"] == "Post1"

def test_existing_functionality_still_works():
    # Ensure that a post without categories still validates and would render
    with tempfile.TemporaryDirectory() as td:
        p = pathlib.Path(td) / "2026-08-25-test.md"
        p.write_text("""---
date: 2026-08-25
author: Jane Doe
title: No Cats Still Works
abstract: ok
---
Body with **bold** and `code`""")
        errors, _ = v.validate_file(p)
        assert errors == []
