# All-source recovery (supplemental)

Upload `recover_sources.py`, `recovery-requirements.txt`, and `.github/workflows/recover-sources.yml` to the corresponding paths in the existing GitHub repository. Do not delete `collector.py`, `sources.json`, or `data/articles.json`.

Run Actions > Recover all publication feeds > Run workflow. Inspect logs and `data/articles.json` feed_status for results.

This is a best-effort public metadata recovery process, NOT a guarantee that every publisher can be ingested. It attempts the existing feed, limited candidate feeds, RSS/Atom autodiscovery from official homepages, and JSON-LD article metadata on official landing pages. It never bypasses a paywall or login. Some publishers block GitHub Actions or publish no RSS/JSON-LD; those require documented official APIs or manual publisher-specific integrations. URL candidates are not guaranteed valid. Site directory should link directly to the `homepage` value for unavailable sources.

This workflow runs at 07:45 and 18:45 IST, fifteen minutes after the existing collection schedule, and preserves prior articles. GitHub scheduled runs can be delayed. A source is `ok` only when this recovery run finds usable metadata; status can differ from the primary collector. It does not create verified summaries or deep editorial intelligence. It does not alter the UI's filter behaviour; clear the calendar when exploring publications until a frontend change is deployed.
