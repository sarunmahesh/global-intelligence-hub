# One-time activation checklist — Global Intelligence Hub

**This repository currently lacks `data/articles.json` and `.github/workflows/collect.yml` according to the read-only GitHub API check on 20 Oct 2026.**

1. In your GitHub repository, upload the contents of this package, **preserving the `data/` and `.github/workflows/` directories**. In the GitHub browser file uploader, drag the extracted folders from a desktop file manager, or use GitHub web editor to create each missing nested file. Existing root files can remain unchanged if the UI blocks overwriting them.
2. Verify GitHub Code tab shows **data/articles.json** and **.github/workflows/collect.yml**. This is the key step that was missed.
3. In repository **Actions**, select **Collect public article metadata** and click **Run workflow**. Select `manual`, `5`, then run. This requests a five-day metadata backfill from working feeds.
4. Open the Actions run: verify green success and check the source feed status in `data/articles.json`. The run requires repository Actions permission to write contents; if a git push returns 403, enable **Settings → Actions → General → Workflow permissions → Read and write permissions** where offered, or adjust repository/organization policies.
5. Wait for GitHub Pages deployment, then refresh the public website. GitHub Pages can cache briefly.

## Truthful scope

- `data/articles.json` includes **19 previously curated entries** across 16, 17, 19 and 20 Oct; this is not a complete five-day research archive.
- Additional feeds are **candidates, not all tested**. The workflow reports failures per source, and some will need replacement.
- RSS/Atom collection automatically populates article titles, dates, publisher and URLs. It **does not** produce fact-checked quotations, original arguments, credible counterarguments or /100 editorial scores. These fields require a separate editorial research process.
- The existing ChatGPT 8 AM and 7 PM tasks send their own responses/notifications, but **do not publish to this GitHub website**. There is no supported direct ChatGPT-task-to-GitHub publication connection in this package.
- No website push notifications or cross-device bookmark sync are implemented.
- Source URLs and access status are not guaranteed to be correct or free-to-read.
