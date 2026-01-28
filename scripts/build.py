
#!/usr/bin/env python3
import re, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
UA = (ROOT / "sources" / "ua_source.m3u").read_text(encoding="utf-8", errors="ignore")
RU_ORG = (ROOT / "sources" / "ru_org.m3u").read_text(encoding="utf-8", errors="ignore")
RU_CUSTOM = (ROOT / "sources" / "ru_custom.m3u").read_text(encoding="utf-8", errors="ignore")

def merge(*parts):
    out = ["#EXTM3U"]
    for part in parts:
        for line in part.splitlines():
            if not line.startswith("#EXTM3U"):
                out.append(line)
    return "
".join(out) + "
"

full = merge(UA, RU_ORG, RU_CUSTOM)
(ROOT / "full.m3u").write_text(full, encoding="utf-8")

# --- Blink: короткие EXTINF + 5 категорий
import re

def entries(m3u):
    cur, opts = None, []
    for ln in m3u.splitlines():
        if ln.startswith("#EXTINF"):
            cur, opts = ln, []
        elif ln.startswith("#EXTVLCOPT") or ln.startswith("#KODIPROP"):
            if cur: opts.append(ln)
        elif ln and not ln.startswith("#") and cur:
            yield cur, opts[:], ln.strip()
            cur, opts = None, []

def ga(inf, key):
    m = re.search(fr'{key}="([^"]+)"', inf)
    return m.group(1) if m else ""

def clean(name):
    name = re.sub(r"\s*\(\d+p\)", "", name, flags=re.I)
    name = re.sub(r"\s*\[(.*?)\]", "", name)
    name = name.replace(" (HD)", "").replace(" (SD)", "")
    return re.sub(r"\s{2,}", " ", name).strip()

MOVIE = ['kino','movie','cinema','кино','кин','bestseller','roman','illusion','patriot','start ','russkoe kino','evrokino','feniks','pro100','dom kino']
MUSIC = ['music','муз','музыка','radio ','rutv','bridge','europa plus','viva russia','songtv','o2тв','muz',' m1',' m2','strana fm']
KIDS  = ['kids','дет','мульт','ani','ryzhiy','карусел','tamyr','smile']

def bucket(name, inf):
    low = name.lower()
    g = ga(inf, "group-title").lower()
    tvg = ga(inf, "tvg-id").lower()
    if any(k in low for k in MOVIE) or "movies" in g: return "Movies"
    if any(k in low for k in MUSIC) or "music" in g:  return "Music"
    if any(k in low for k in KIDS)  or "kids" in g or "animation" in g: return "Kids"
    if ".ua" in tvg or " ua" in g or "suspilne" in low or "kyiv" in low or "київ" in low: return "Ukraine"
    return "Russia"

blink = ["#EXTM3U"]
for inf, opts, url in entries(full):
    m = re.search(r",\s*(.+)$", inf)
    name = clean(m.group(1)) if m else "Channel"
    group = bucket(name, inf)
    httpua = ga(inf, "http-user-agent")
    if httpua:
        blink.append(f'#EXTINF:-1 group-title="{group}" http-user-agent="{httpua}",{name}')
    else:
        blink.append(f'#EXTINF:-1 group-title="{group}",{name}')
    for o in opts:
        if o.lower().startswith("#extvlcopt:http-user-agent"):
            blink.append(o)
    blink.append(url)

(ROOT / "blink.m3u").write_text("
".join(blink) + "
", encoding="utf-8")
print("OK: full.m3u + blink.m3u")
