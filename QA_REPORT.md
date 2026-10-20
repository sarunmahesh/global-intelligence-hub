# Quality assurance status — Global Intelligence Hub

## Passed automated checks
- `python3 -m py_compile collector.py`: passed.
- `node --check app.js`: passed.
- RSS parser test with valid RSS entry: passed (title, HTTPS canonical URL, publication timestamp).
- Atom parser test with valid Atom entry: passed.
- Invalid javascript: URL rejected by collector.
- Package contains `index.html`, `styles.css`, `app.js`, `manifest.webmanifest`, `icon.svg`, `collector.py`, `sources.json`, `data/articles.json`, `.github/workflows/collect.yml`, `README.md`, `about.html`.

## Not passed / not yet tested
- Full interactive browser QA: attempted at desktop 1440×900 and mobile 390×844; browser sandbox returned `ERR_BLOCKED_BY_ADMINISTRATOR` for local and file URLs. No visual or interactive pass is claimed.
- Live RSS feed availability: outbound access unavailable in the container; source endpoints must be checked during the first GitHub Actions run.
- GitHub Pages deployment and scheduled execution: not tested because no authorized GitHub account was connected.
- Real cross-device bookmark sync and phone notifications: not implemented.
- Word output is Word-compatible `.doc`, not `.docx`; PDF is browser print-to-PDF.
- Free-access status is intentionally Unknown until independently verified; no claim of 90% verified free articles.
- Data is empty until the first successful collection job.

## Operational risks
- GitHub Actions scheduled runs may be delayed or skipped.
- RSS feeds can fail, move, block automated clients, or require different parsing.
- Static index retains up to 12,000 latest entries; a database/archive upgrade is needed for unbounded retention.
- Browser-local bookmarks do not synchronize across devices.
- Google News search opens a new tab and is not indexed into the archive.
