# Contributing a Blog Post

Thank you for contributing to the PyKampala Community Blog! This guide shows how to add a post using Markdown and GitHub.

## Quick Start

```bash
git clone https://github.com/Pykampala-Community/blogs.git
cd blogs
pip install -r docs/requirements.txt
pip install pyyaml markdown pytest
```

## 1. Create Your Post

Copy the template:

```bash
cp content/blog/_template.md content/blog/2026-08-25-my-post-slug.md
```

Or create `content/blog/YYYY-MM-DD-slug.md` manually. **File naming convention:** `YYYY-MM-DD-slug.md` — lowercase, hyphens, e.g. `2026-08-25-building-python-projects.md`. This slug becomes part of your URL.

## 2. Fill Front Matter (Required)

Every post must start with:

```yaml
---
date: 2026-08-25
author: Your Name
title: Your Blog Post Title
abstract: Your short summary. Maximum 1024 characters.
---
```

- **date:** `YYYY-MM-DD` — used for sorting (newest first) and URL `/2026/08/...`
- **author:** Your name as you want it displayed
- **title:** Post title
- **abstract:** Excerpt shown on blog index — **≤ 1024 characters**. Longer abstracts fail CI with:

  ```
  Blog post validation failed:
  content/blog/2026-08-25-my-post.md
  - abstract is 1127 characters long
  - maximum allowed length is 1,024 characters
  ```

  > Hint: `Abstract: Keep this to 1024 characters or fewer. This is displayed as the post summary on the blog index.`

Optional for MkDocs compatibility (auto-added if missing):

```yaml
authors:
  - Your-Name   # must exist in docs/.authors.yml (add yourself there)
categories:
  - Tutorial   # Tutorial | Benchmark | Performance | Data | Ai | Project | General
```

Add yourself to `docs/.authors.yml`:

```yaml
authors:
  Your-Name:
    name: "Your Name"
    description: "Short bio"
    avatar: https://avatars.githubusercontent.com/u/...
```

**Enable comments (Giscus):**

Add to front matter:

```yaml
comments: true
```

This enables the Giscus comment section at the bottom of your post (white background, `data-theme="light"` for legibility). Readers comment with their GitHub account via `Pykampala-Community/blogs` Discussions (see `overrides/partials/comments.html`). No extra setup needed — just set `comments: true`.

> **Troubleshooting “giscus unable to create discussion”:** Giscus requires the **giscus GitHub App** to be installed for the target repo and **Discussions enabled**.
> 1. Install/check at **https://github.com/apps/giscus** → Configure → *Pykampala-Community* → select `blogs` (and grant *Discussions: Read & write*).
> 2. In repo **Settings → General → Features**, ensure **Discussions** is checked.
> 3. Verify category `General` (`DIC_kwDOMANU_M4DEHUm`) exists in **https://github.com/Pykampala-Community/blogs/discussions/categories** — giscus creates a Discussion per `pathname` on first comment. If the app was just installed, wait ~1 min and hard-refresh the post. As fallback, commenters can still use **[View discussions directly](https://github.com/Pykampala-Community/blogs/discussions)**.

## 3. Write Content in Markdown

Below front matter, write normal Markdown:

```markdown
# Your Blog Post Title

![Alt text for image](assets/my-image.png)

## Section

Intro here.

<!-- more -->  # optional excerpt separator for Material blog

## Code Example

```python
def hello(name: str):
    return f"Hello, {name}!"
```

| Feature | Tool |
|---------|------|
| Test | Pytest |

> Blockquote, lists, links, tables, and images all work. See example: `content/blog/2026-08-25-building-python-projects.md`
```

## 4. Add Images

Place images under `content/blog/assets/`:

```
content/blog/assets/my-diagram.png
```

Reference:

```markdown
![Descriptive alt text](assets/my-diagram.png)
```

- Always include meaningful `alt` text (accessibility)
- Prefer PNG/WebP, optimize size
- For `docs/posts` legacy, also place under `docs/posts/assets/` — the sync script copies automatically

## 5. Preview Locally

```bash
# Sync content/blog -> docs/posts (auto-adds authors for MkDocs)
python scripts/sync-blog.py

# Validate (required fields, abstract ≤1024, date, slug, duplicates, markdown parse)
python scripts/validate_blog_posts.py
# or
python scripts/validate-blog-posts.py

# Run tests
pytest -v

# Build & serve
mkdocs serve        # http://127.0.0.1:8000/blogs/
mkdocs build --strict  # validates generation, sorting, slugs
```

- **Blog index:** `/` or `/blogs/` — Metro-style grid, sorted newest first, shows title, author, date, abstract
- **Post URL:** `/{date}/{slug}/` e.g. `/2026/08/25/building-python-projects/` — shows title, author, date, abstract, rendered Markdown with code highlighting
- **Navigation:** Use header `← Back to PyKampala Community` → https://pykampala-community.github.io/

## 6. Submit Pull Request

```bash
git checkout -b post/my-post-slug
git add content/blog/2026-08-25-my-post-slug.md docs/.authors.yml
git commit -m "post: add My Post Slug"
git push -u origin post/my-post-slug
```

Open PR against `main`. **Automated checks run:**

- `Validate Blog` workflow: front matter, abstract 1024, filename convention, duplicate slugs, `pytest`, `mkdocs build --strict`

Fix any errors shown in CI logs.

## 7. What Happens After Merge

1. PR merged to `main`
2. `ci` workflow runs: `sync` → `validate` → `pytest` → `mkdocs gh-deploy --force`
3. Blog index and post page are generated automatically from Markdown
4. Site deployed to **https://pykampala-community.github.io/blogs/** — your post appears within seconds

No manual HTML or index maintenance required.

## Design & Accessibility

- Reuses PyKampala Metro UI tokens from `../Pykampala-Community.github.io/src/styles/main.css` via `docs/stylesheets/metro.css` (brand-yellow `#F2E600`, brand-dark `#121212`, accent `#3776AB`)
- Strong card layouts, clear hierarchy, responsive, keyboard-accessible, focus states, contrast, semantic HTML

## Need Help?

- Read `content/blog/_template.md` and `content/blog/2026-08-25-building-python-projects.md`
- Check `scripts/validate_blog_posts.py` error messages
- Open an issue: https://github.com/Pykampala-Community/blogs/issues
