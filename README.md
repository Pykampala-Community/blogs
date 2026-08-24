# PyKampala Community Blog

Technical and community stories from [PyKampala Community](https://pykampala-community.github.io/) — Python developers in Uganda, established 2016.  
Live blog: **https://pykampala-community.github.io/blogs/** • Main site: **https://pykampala-community.github.io/**

> Native extension of the main PyKampala website — same Metro UI (`--brand-primary: #F2E600`, `--brand-dark: #121212`, `--brand-accent: #3776AB`), typography, spacing, navigation, and branding from `../Pykampala-Community.github.io/src/styles/main.css` via `docs/stylesheets/metro.css`.

## Features

- **Blog index** `/` — Metro grid of cards (title, author, date, abstract) sorted newest-first, responsive, `← Back to PyKampala Community`
- **Post pages** `/{date}/{slug}/` — title, author, date, abstract, Markdown content with code highlighting, `← Back to Blog` + `← Back to PyKampala Community`
- **Markdown-first** — posts in `content/blog/` as `YYYY-MM-DD-slug.md` with front matter `date/author/title/abstract` (abstract ≤1024)
- **Auto-generation** — index and post pages derived from Markdown; merging PR publishes automatically
- **RSS** `feed_rss_created.xml` / `feed_rss_updated.xml` (Material blog `rss: true`)
- **SEO** — title/description from abstract, Open Graph, canonical `site_url`
- **Accessibility** — semantic HTML, heading hierarchy, keyboard focus, contrast, alt text

## Quick Start

```bash
git clone https://github.com/Pykampala-Community/blogs.git
cd blogs
pip install -r docs/requirements.txt
pip install pyyaml markdown pytest  # validation & tests

# Create post from template
cp content/blog/_template.md content/blog/2026-08-25-my-post.md
# Edit front matter + Markdown

# Sync (content/blog → docs/posts) + validate + test + build
python scripts/sync-blog.py
python scripts/validate_blog_posts.py  # also: python scripts/validate-blog-posts.py
pytest -v
mkdocs serve          # http://127.0.0.1:8000/blogs/
mkdocs build --strict # validates generation
```

## Content Model

`content/blog/_template.md`:

```yaml
---
date: YYYY-MM-DD
author: Your Name
title: Your Blog Post Title
abstract: Your short summary. Maximum 1024 characters.
---

# Your Blog Post Title

Write your post here.
```

Required: `date` (YYYY-MM-DD), `author`, `title`, `abstract` (≤1024). Validation fails with actionable error if missing/invalid/long.

File naming: `YYYY-MM-DD-slug.md` (lowercase hyphens, e.g. `2026-08-25-building-python-projects.md`) → URL `/{date}/{slug}/`. Duplicate slugs fail validation.

Example: `content/blog/2026-08-25-building-python-projects.md` (and synced to `docs/posts/`)

## Images

Place under `content/blog/assets/`:

```
content/blog/assets/my-image.png
```

Reference:

```markdown
![Descriptive alt text](assets/my-image.png)
```

- Always add alt text
- Optimize size
- Sync copies to `docs/posts/assets/` via `sync-blog.py`

## Validation

```bash
python scripts/validate_blog_posts.py
```

Checks: required fields, date valid, abstract ≤1024, filename convention, no duplicate slugs, markdown parseable. Errors are human-readable:

```
Blog post validation failed:

content/blog/2026-08-25-my-post.md
- abstract is 1127 characters long
- maximum allowed length is 1,024 characters
```

PRs run this automatically (`.github/workflows/blog-validate.yml`).

## Tests

```bash
pytest -v  # tests/test_blog_validation.py: front matter, abstract length, date, slug, discovery, sorting, duplicates
```

## Deployment

```bash
mkdocs gh-deploy --force  # builds and pushes to gh-pages
```

CI does this automatically on `push` to `main` (`.github/workflows/blog-ci.yml`): `sync` → `validate` → `pytest` → `mkdocs build --strict` → `mkdocs gh-deploy --force` → https://pykampala-community.github.io/blogs/

## Repository Structure

```
.
├── content/blog/
│   ├── _template.md
│   ├── 2026-08-25-building-python-projects.md
│   └── assets/
├── docs/
│   ├── index.md              # Blog landing (Metro hero)
│   ├── posts/                # MkDocs source (synced from content/blog)
│   ├── .authors.yml
│   ├── stylesheets/metro.css # Metro UI override (reuses main site tokens)
│   └── requirements.txt
├── overrides/
│   ├── main.html             # Top banner ← Back to PyKampala Community
│   └── partials/comments.html
├── scripts/
│   ├── sync-blog.py
│   ├── validate_blog_posts.py  # also validate-blog-posts.py
├── tests/
│   └── test_blog_validation.py
├── mkdocs.yml                # site_url, blog plugin, rss, seo, extra_css
├── CONTRIBUTING.md
└── .github/workflows/
    ├── blog-ci.yml           # deploy on push to main
    └── blog-validate.yml     # validate on PR
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) and template `content/blog/_template.md`. PR template at `.github/pull_request_template.md` enforces checklist.

After merge, the normal site build publishes your post — no manual HTML.

## Design

Metro-inspired from main site: rectangular cards, `border-left: 4px solid var(--brand-primary)`, bold hierarchy, `Inter` typography, generous spacing, flat colors. Responsive, focus states, `← Back to PyKampala Community` header/footer.

## License

Community open-source — PRs welcome.
