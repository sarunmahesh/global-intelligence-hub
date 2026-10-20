# Global Intelligence Hub

A mobile/desktop responsive, static, free-hosting-compatible news and research directory. Stores original article titles, publisher URLs, dates, category and collection edition, not copyrighted article bodies.

## Run locally

```bash
python3 -m http.server 8000
# Open http://localhost:8000
```

## Deploy free with GitHub Pages

1. Create a new **public** GitHub repository and upload the entire contents of this folder, including `.github/workflows/collect.yml`.
2. In repository **Settings → Pages**, choose **Deploy from a branch**, branch `main`, folder `/ (root)`.
3. In **Actions**, enable workflows if prompted. In repository **Settings → Actions → General**, permit workflow read/write access where available. The workflow uses `permissions: contents: write` to commit collected metadata.
4. Run **Actions → Collect public article metadata → Run workflow** once. Confirm `data/articles.json` has articles and inspect feed health. The Pages site rebuilds after the commit.
5. The resulting public address follows `https://YOUR-USERNAME.github.io/YOUR-REPOSITORY/`. **This is a pattern, not a verified deployed URL.**

Scheduled GitHub Actions jobs run approximately 07:30 and 18:30 IST, and can be delayed or skipped. Public repositories may be subject to platform anti-abuse and usage restrictions. The initial JSON index is empty until a collection job runs. RSS feeds may fail or move; review `feed_status` and maintain `sources.json`.

## What works

- Responsive mobile/desktop layout; installable web app manifest (not offline-capable)
- Archive keyword search with finance/policy synonyms
- External Google News search (not automatic in-app web ingestion)
- Publisher/category/date/edition/access filters and sorting
- Bookmarks saved locally per browser; JSON backup/restore
- CSV, Word-compatible `.doc` and browser print-to-PDF exports
- Source-feed health and last-update timestamp
- RSS/Atom collection and morning/evening first-discovery tagging
- No external JS libraries or API keys needed

## Important limitations

- No guaranteed 90% verified free-to-read coverage. Feeds are not access verification. All ingested records start with `access: Unknown`.
- Live web search opens an external search engine; it is not an API-integrated search inside the archive.
- GitHub Pages site is public. Do not place private credentials or private documents in it.
- GitHub scheduled jobs can be delayed, disabled after inactivity, or blocked by changed source access.
- No push notifications or cross-device bookmark sync in this release. Existing ChatGPT scheduled reminders are separate and do not write to this site.
- Word export is `.doc` (HTML Word-compatible), not a native `.docx`. PDF is browser print-to-PDF.
- This is a functional starter application, not a guarantee of continuous global editorial coverage. The 23 feeds are initial candidates, not a verified inventory of working feeds.
- A single JSON index is capped at 12,000 records to keep client-side performance acceptable. For long-term retention, archive older records separately or migrate to a database.

## Next upgrades

A permanent multi-year database; authenticated bookmarks; email/push notification integration; a verified free-access classification process; richer source-specific ingestion; independent off-site backups; server-side web-wide search and publisher-specific terms compliance.
