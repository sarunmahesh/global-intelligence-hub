# V1 Magazines & Newsletters — English-only

This is an additive, independent page for the existing static Global Intelligence Hub V1. It does not replace or modify the daily article feed, collector, or bookmarks.

## Install

1. Copy `magazines.html` to the root of the V1 GitHub repository, alongside `index.html`.
2. In the existing `index.html` sidebar `<nav id="nav">`, add `<a href="magazines.html">▤ Magazines & Newsletters</a>` and style it like the other navigation items, or add a simple link anywhere on the site.
3. Commit and wait for the existing GitHub Pages deployment.

## Features

- English-only directory; no Hindi entries.
- Free-access source pages for UPSC, science/Nature, institutions, think tanks and business/economics.
- Category, frequency, text search and saved-only filters.
- Publisher links open in new tabs; local browser bookmarks.
- Frequency is publisher-level metadata, not a claim that a new issue exists in any given month.
- No external JavaScript libraries or PHP.

## Limitations

- Curated publication directory, not an automated issue/article scraper.
- Free access is not guaranteed for every linked article or report, especially NBER and Chatham House.
- Issue-level month/date, verified article titles, quotations and PDFs require a separate ingestion and verification process.
- The existing repository's connector currently rejects writes with HTTP 403; this package has not been deployed.
