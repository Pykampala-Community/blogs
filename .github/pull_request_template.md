# Blog Post Contribution

## Post Checklist

- [ ] File location: `content/blog/YYYY-MM-DD-slug.md` (lowercase, hyphens)
- [ ] Front matter includes: `date` (YYYY-MM-DD), `author`, `title`, `abstract` (≤1024 chars)
- [ ] Added myself to `docs/.authors.yml` if new author
- [ ] Added images to `content/blog/assets/` with descriptive alt text (if any)
- [ ] Ran `python scripts/sync-blog.py` and `python scripts/validate_blog_posts.py` locally — no errors
- [ ] Ran `pytest -v` and `mkdocs build --strict` locally — both pass

## Abstract Length

> Keep abstract to 1024 characters or fewer. This is displayed as summary on blog index.

Current abstract length: <!-- run: python -c "import yaml; print(len(yaml.safe_load(open('content/blog/YYYY-MM-DD-slug.md').read().split('---')[1])['abstract']))" -->

## Preview

- Branch preview via `mkdocs serve`
- Post should appear in blog index newest-first, with clean URL `/{date}/{slug}/`

## Notes for Reviewers

<!-- Any context, categories (Tutorial/Benchmark/Performance/Data/Ai/Project/General), or special handling -->

---
Fixes validation error (if any):

```
Blog post validation failed:
content/blog/...
- ...
```
