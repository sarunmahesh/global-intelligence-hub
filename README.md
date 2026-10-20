# Global Intelligence Hub: Research Workspace Upgrade

## What is included
- Responsive minimalist research workspace: For You, Explore, Source library, Saved
- Subject, publication, author, source type, access, edition and date filters
- Calendar day/week/month archive search, by publication, collection or edition date
- Preview panel, original publisher links, bookmarks, followed publications, dark mode
- Lazy-loading publisher-provided thumbnails and RSS author names where available
- Existing `data/articles.json` archive retained; no article or bookmark deletion

## Deployment (GitHub Pages)
1. In `sarunmahesh/global-intelligence-hub`, replace the root `index.html`, `styles.css` and `app.js` with the files from this ZIP, using GitHub's web interface or `git`.
2. Add `upgrade_collector.py` at repository root. From a local clone, run `python upgrade_collector.py`, then commit the modified `collector.py`. Alternatively apply the modifications to `collector.py` manually.
3. Keep the existing `sources.json`, `.github/workflows/collect.yml`, `data/articles.json`, `manifest.webmanifest` and other assets unchanged.
4. Trigger the existing Collect GitHub Action manually once to populate author/thumbnail metadata on entries whose feeds expose it.
5. Confirm the site loads and check browser console. Thumbnails may not display if a publisher blocks hotlinking; placeholders are intentional.

## Archive limitations
- Calendar filters past records already retained in `data/articles.json`. It does not reconstruct articles or exact briefings from dates that were never archived.
- 'For You' promotes followed publications; this is lightweight local personalization, not a trained recommendation model.
- No author, summary or image is invented. Missing metadata is labeled or omitted.
- All images remain hosted by publishers; images are not bundled into the repository.
- Saved bookmarks and follows are device-local in browser storage.

## Permission status
GitHub connector write attempt returned 403 Resource not accessible by integration. These files have NOT been deployed to the live site.
