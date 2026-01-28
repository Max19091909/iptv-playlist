
# IPTV Playlist (UA+RU) — Blink Player optimized

This repo builds two playlists:
- `full.m3u` — merged UA + RU channels
- `blink.m3u` — short `#EXTINF` entries and 5 buckets: `Movies`, `Music`, `Kids`, `Ukraine`, `Russia`.

GitHub Actions pulls fresh country playlists from iptv-org and merges them with your custom RU list, then publishes to GitHub Pages.

## How to use
1. Create a repository (e.g., `iptv-playlist`) and enable **GitHub Pages** (Source: `GitHub Actions`).
2. Push this folder to your repo.
3. Run the workflow once (**Actions → Build IPTV → Run workflow**).
4. Your permanent URLs will be:
   - `https://<username>.github.io/<repo>/blink.m3u`
   - `https://<username>.github.io/<repo>/full.m3u`

Paste the `blink.m3u` URL into Blink Player → Add playlist → Enter URL.

## Sources
- `sources/ua_source.m3u` — fetched nightly from iptv-org (UA)
- `sources/ru_org.m3u` — fetched nightly from iptv-org (RU)
- `sources/ru_custom.m3u` — your custom RU set

## Notes
- Some channels require special headers (User-Agent); we preserve them in both `#EXTINF` and `#EXTVLCOPT`.
- You can edit `scripts/build.py` to change buckets or naming rules.
