# ============================================================
# app.py - Stylist Buddy with Email Validation & Password Recovery
# ============================================================
import streamlit as st
import base64
import io
import sqlite3
import hashlib
import hmac
import itertools
import json
import re
import secrets
import shutil
import zlib
import os
import time
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from html import escape as _esc
from pathlib import Path
from urllib.parse import quote_plus

APP_DIR = Path(__file__).parent
DB_PATH = APP_DIR / "aistylist.db"
UPLOAD_DIR = APP_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

DEMO_CACHE_DIR = APP_DIR / "demo_cache"
DEMO_CACHE_DIR.mkdir(exist_ok=True)

st.set_page_config(
    page_title="Stylist Buddy",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ----------------------------- Theme -------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=DM+Sans:wght@400;500;600&display=swap');

:root {
  --cream:#f4ecdf; --cream-2:#ebdfcb; --paper:#fffbf4; --brown:#6a4630; --brown-2:#8b5e3c;
  --tan:#c8ab87; --ink:#151311; --muted:#7b6b5b; --line:#e0d2bc; --shadow:rgba(60,38,20,.10);
}

html, body, .stApp, .stApp button, .stApp input, .stApp textarea, .stApp select { font-family:'DM Sans', system-ui, sans-serif; }
.stApp { background: var(--cream); color: var(--ink); }
.stApp p, .stApp label, .stApp li, .stApp span, .stApp div[data-testid="stMarkdownContainer"] { color: inherit; }
header[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }
section[data-testid="stSidebar"], [data-testid="collapsedControl"], [data-testid="stSidebarCollapsedControl"] { display:none !important; }
.block-container { max-width: 1240px; padding: 1.4rem 1.6rem 3rem; }
h1, h2, h3, h4 { font-family:'Fraunces', Georgia, serif !important; color: var(--ink); font-weight:500 !important; letter-spacing:-.01em; }
hr { border-color: var(--line) !important; }
a { color: var(--brown-2); }

/* ---------- Buttons ---------- */
.stButton > button, .stFormSubmitButton > button, .stDownloadButton > button {
  border-radius: 999px; border: 1px solid var(--line); background: var(--paper); color: var(--ink);
  font-weight:500; transition: all .18s ease; min-height: 2.5rem;
}
.stButton > button:hover, .stFormSubmitButton > button:hover, .stDownloadButton > button:hover {
  border-color: var(--brown-2); color: var(--brown); background:#fff;
}
button[kind="primary"], button[data-testid="stBaseButton-primary"], button[data-testid="stBaseButton-primaryFormSubmit"] {
  background: var(--ink) !important; color: var(--cream) !important; border: 1px solid var(--ink) !important;
}
button[kind="primary"]:hover, button[data-testid="stBaseButton-primary"]:hover {
  background: var(--brown) !important; border-color: var(--brown) !important; color:#fff !important;
}

/* ---------- Inputs ---------- */
div[data-baseweb="input"], div[data-baseweb="textarea"], div[data-baseweb="select"] > div {
  background: var(--paper) !important; border-color: var(--line) !important; border-radius: 12px !important; color: var(--ink) !important;
}
div[data-baseweb="input"] input, div[data-baseweb="textarea"] textarea { color: var(--ink) !important; -webkit-text-fill-color: var(--ink) !important; }
div[data-baseweb="input"]:focus-within, div[data-baseweb="textarea"]:focus-within { border-color: var(--brown-2) !important; }
div[data-baseweb="popover"] div, div[data-baseweb="popover"] li, div[data-baseweb="popover"] ul { background: var(--paper); color: var(--ink); }
div[data-baseweb="tag"] { background: var(--cream-2) !important; color: var(--ink) !important; }
[data-testid="stFileUploaderDropzone"] { background: var(--paper); border:1px dashed var(--tan); border-radius:14px; }
[data-testid="stExpander"] { border:1px solid var(--line); border-radius:14px; background: var(--paper); }
[data-testid="stExpander"] summary p { font-weight:500; }
.stTabs [data-baseweb="tab-list"] { gap:.2rem; border-bottom:1px solid var(--line); overflow-x:auto; }
.stTabs [data-baseweb="tab"] { color: var(--muted); }
.stTabs [aria-selected="true"] { color: var(--ink) !important; }
.stTabs [data-baseweb="tab-highlight"] { background: var(--brown) !important; }
.stProgress > div > div > div > div { background: var(--brown) !important; }
.stProgress > div > div > div { background: var(--cream-2) !important; }
div[data-testid="stVerticalBlockBorderWrapper"] { border-color: var(--line); border-radius: 20px; }

/* ---------- Pills ---------- */
div[role="radiogroup"] { gap:.45rem; flex-wrap:wrap; }
div[role="radiogroup"] label {
  padding:.42rem 1rem; border-radius:999px; border:1px solid var(--line); background:var(--paper);
  cursor:pointer; transition: all .18s ease; margin:0;
}
div[role="radiogroup"] label:hover { border-color: var(--brown-2); }
div[role="radiogroup"] label:has(input:checked) { background: var(--ink); border-color: var(--ink); }
div[role="radiogroup"] label:has(input:checked) * { color: var(--cream) !important; }
div[role="radiogroup"] label > div:first-child { display:none; }
div[role="radiogroup"] label p { font-size:.9rem; font-weight:500; }

/* ---------- Top bar ---------- */
.brand { display:flex; align-items:center; gap:.7rem; }
.brand-mark { width:42px; height:42px; border-radius:14px; background:var(--ink); color:var(--cream);
  display:flex; align-items:center; justify-content:center; flex:0 0 auto; }
.brand-mark svg { width:28px; height:28px; display:block; }
.brand-mark .spark { fill:var(--tan); stroke:none; }
.brand.light .brand-mark { background:var(--cream); color:var(--ink); }
.brand.light .brand-mark .spark { fill:var(--brown-2); }
.brand.light .brand-name { color:var(--cream); }
.brand.light .brand-sub { color:#d8c4a6; }
.brand-name { font-family:'Fraunces',serif; font-size:1.3rem; line-height:1.05; }
.brand-sub { font-size:.78rem; color:var(--muted); }
.user-chip { display:flex; align-items:center; justify-content:flex-end; gap:.6rem; height:42px; }
.user-chip .avatar { width:36px; height:36px; border-radius:50%; background:var(--brown); color:var(--cream);
  display:flex; align-items:center; justify-content:center; font-weight:600; }
.user-chip .uname { font-size:.9rem; font-weight:500; }

/* ---------- Hero / headings ---------- */
.hero { padding:2.6rem 2.4rem; border-radius:28px; margin:.6rem 0 1.4rem; color:var(--cream);
  background: linear-gradient(120deg, #2a1d14 0%, var(--brown) 60%, #8b5e3c 120%); box-shadow:0 18px 40px var(--shadow); }
.stApp .hero h1 { color:var(--cream) !important; font-size:2.8rem; line-height:1.08; margin:0 0 .5rem; padding:0; }
.hero p { color:#e9dac3; max-width:520px; font-size:1.02rem; margin:0; }
.page-head { margin:.8rem 0 1.2rem; }
.stApp .page-head h1 { font-size:2.3rem; margin:0; padding:0; }
.page-head p { color:var(--muted); margin:.25rem 0 0; }
.section-title { font-family:'Fraunces',serif; font-size:1.55rem; margin:1.8rem 0 .15rem; }
.section-sub { color:var(--muted); font-size:.92rem; margin-bottom:.8rem; }
.small-muted { color:var(--muted); font-size:.88rem; }

/* ---------- Look tiles & cards ---------- */
.tile { position:relative; border-radius:16px; overflow:hidden; display:flex; width:100%; background:var(--cream-2); }
.tile .blk { flex:1; }
.tile img { width:100%; height:100%; object-fit:cover; display:block; }
.tile .collage { display:grid; width:100%; height:100%; gap:2px; }
.tile-cap { position:absolute; left:10px; bottom:10px; background:rgba(255,251,244,.92); color:var(--ink);
  border-radius:999px; padding:.18rem .7rem; font-size:.76rem; font-weight:500; }
.look-name { font-family:'Fraunces',serif; font-size:1.3rem; line-height:1.2; margin:.65rem 0 .2rem; }
.look-meta { font-size:.82rem; color:var(--muted); }
.item-row { display:flex; gap:.8rem; padding:.42rem 0; border-top:1px solid var(--line); font-size:.92rem; }
.item-row small { flex:0 0 74px; color:var(--muted); font-size:.8rem; padding-top:.1rem; }
.detail-note { font-size:.84rem; color:var(--muted); margin:.3rem 0; line-height:1.45; }
.tag { display:inline-block; padding:.16rem .65rem; border-radius:999px; border:1px solid var(--line); background:var(--paper);
  color:var(--muted); font-size:.76rem; margin:.1rem .25rem .1rem 0; }
.tag.dark { background:var(--ink); border-color:var(--ink); color:var(--cream); }
.tag.brown { background:var(--cream-2); border-color:var(--tan); color:var(--brown); }
.swatches { display:flex; flex-wrap:wrap; gap:.3rem .7rem; margin:.3rem 0 .5rem; }
.swatch-wrap { display:inline-flex; align-items:center; gap:.35rem; font-size:.78rem; color:var(--muted); }
.swatch { width:13px; height:13px; border-radius:50%; border:1px solid rgba(0,0,0,.25); display:inline-block; }
.why li { margin:.25rem 0; font-size:.9rem; }
.shop-item { padding:.55rem 0; border-top:1px solid var(--line); font-size:.9rem; }
.shop-item .why-text { color:var(--muted); font-size:.82rem; margin:.15rem 0 .3rem; }
.shop-item a { display:inline-block; margin-right:.8rem; font-size:.84rem; font-weight:500; }
.bar-row { display:flex; align-items:center; gap:.7rem; margin:.35rem 0; font-size:.88rem; }
.bar-row .lbl { flex:0 0 110px; }
.bar-row .bar { flex:1; height:8px; border-radius:99px; background:var(--cream-2); overflow:hidden; }
.bar-row .bar i { display:block; height:100%; background:var(--brown); border-radius:99px; }

/* ---------- Steps ---------- */
.stepper { display:flex; gap:.5rem; margin:.2rem 0 1rem; flex-wrap:wrap; }
.stepper .s { padding:.3rem .9rem; border-radius:999px; border:1px solid var(--line); background:var(--paper); font-size:.85rem; color:var(--muted); }
.stepper .s.on { background:var(--ink); border-color:var(--ink); color:var(--cream); }
.stepper .s.done { background:var(--cream-2); border-color:var(--tan); color:var(--brown); }
.step-title { font-family:'Fraunces',serif; font-size:1.35rem; }
.step-desc { font-size:.88rem; color:var(--muted); margin-bottom:.6rem; }

/* ---------- Before / after ---------- */
.ba-label { font-size:.85rem; color:var(--muted); margin-bottom:.4rem; font-weight:500; }
.ba-placeholder { min-height:300px; border-radius:16px; border:1px dashed var(--tan); display:flex; align-items:center;
  justify-content:center; color:var(--muted); text-align:center; padding:1rem; background:var(--paper); }
[data-testid="stImage"] img { border-radius:16px; }

/* ---------- Landing ---------- */
.landing { position:relative; height:calc(100vh - 4.5rem); min-height:560px; border-radius:28px; overflow:hidden; background:var(--cream-2); }
.landing .wall { column-count:4; column-gap:14px; padding:14px; }
.landing .wall .tile { margin-bottom:14px; break-inside:avoid; }
.landing::after { content:""; position:absolute; inset:0; pointer-events:none;
  background:linear-gradient(180deg, rgba(21,19,17,.62) 0%, rgba(21,19,17,.12) 36%, rgba(21,19,17,.70) 100%); }
.landing-top { position:absolute; z-index:2; left:2rem; top:1.6rem; }
.landing-copy { position:absolute; z-index:2; left:2.2rem; bottom:2.2rem; max-width:470px; color:var(--cream); }
.stApp .landing-copy h2 { color:var(--cream) !important; font-size:2.9rem; line-height:1.08; margin:0 0 .6rem; padding:0; }
.landing-copy p { color:#eadcc5; font-size:1.02rem; margin:0; }
.st-key-auth_float { position:fixed; top:50%; right:max(2rem, calc((100vw - 1240px)/2 + 2.4rem)); transform:translateY(-50%);
  width:min(420px, 92vw); z-index:1000; background:var(--paper); border:1px solid var(--line); border-radius:24px;
  padding:1.4rem 1.5rem 1.2rem; box-shadow:0 24px 60px rgba(30,18,8,.35); max-height:90vh; overflow-y:auto; }
.auth-checks { display:flex; flex-direction:column; gap:.2rem; font-size:.82rem; color:var(--muted); margin:.1rem 0 .7rem; }
.auth-checks .ok { color:#3f6b3a; }
.pw-meter { height:6px; border-radius:99px; background:var(--cream-2); overflow:hidden; margin:.3rem 0 .15rem; }
.pw-meter i { display:block; height:100%; border-radius:99px; }
.login-title { font-family:'Fraunces',serif; font-size:2.1rem; margin:0; }
.login-sub { color:var(--muted); margin:.2rem 0 1rem; }
.footer { text-align:center; color:var(--muted); font-size:.8rem; padding:.5rem 0 1rem; }

@media (max-width: 900px) { .landing .wall { column-count:3; } }
.act-marker, .grid-marker { display:none; }
</style>
""", unsafe_allow_html=True)

COLOR_HEX = {
    "Black": "#151311", "White": "#f5f2ea", "Blue": "#4a78c2", "Navy": "#1c2b4d",
    "Grey": "#8a8a8a", "Beige": "#d8c7a5", "Brown": "#6b4a2f", "Green": "#3f6b4a",
    "Maroon": "#6b1f2a", "Pink": "#e59ab0",
}

LOGO_SVG = ('<svg viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg" fill="none" stroke="currentColor" '
            'stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
            '<path d="M24 20.5v-2.6c0-1.7 1.5-2.6 3-3.2 2.1-.9 3.2-2.5 3.2-4.4a5.2 5.2 0 0 0-10.4 0"/>'
            '<path d="M24 20.5 40.6 31.7a2.4 2.4 0 0 1-1.4 4.4H8.8a2.4 2.4 0 0 1-1.4-4.4Z"/>'
            '<path class="spark" d="M38 3.5c.6 3.4 1.6 4.4 5 5-3.4.6-4.4 1.6-5 5-.6-3.4-1.6-4.4-5-5 3.4-.6 4.4-1.6 5-5Z"/></svg>')

def brand_html(light=False, sub=True):
    sub_html = '<div class="brand-sub">Your personal stylist</div>' if sub else ""
    return (f'<div class="brand{" light" if light else ""}"><div class="brand-mark">{LOGO_SVG}</div>'
            f'<div><div class="brand-name">Stylist Buddy</div>{sub_html}</div></div>')

def swatches(colors):
    parts = "".join(
        f'<span class="swatch-wrap"><span class="swatch" style="background:{COLOR_HEX.get(c, "#888")}"></span>{_esc(str(c))}</span>'
        for c in colors
    )
    return f'<div class="swatches">{parts}</div>'

def tags_html(items, cls=""):
    return "".join(f'<span class="tag {cls}">{_esc(str(t))}</span>' for t in items if t)

def page_header(title, subtitle=""):
    st.markdown(f'<div class="page-head"><h1>{_esc(title)}</h1><p>{_esc(subtitle)}</p></div>', unsafe_allow_html=True)

def section_title(title, sub=""):
    st.markdown(f'<div class="section-title">{_esc(title)}</div><div class="section-sub">{_esc(sub)}</div>', unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def _thumb_b64(path, mtime, max_px):
    try:
        from PIL import Image
        img = Image.open(path).convert("RGB")
        img.thumbnail((max_px, max_px))
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=82)
        return base64.b64encode(buf.getvalue()).decode()
    except Exception:
        try:
            return base64.b64encode(Path(path).read_bytes()).decode()
        except Exception:
            return ""

def img_src(path, max_px=520):
    p = Path(path)
    if not path or not p.exists():
        return ""
    b64 = _thumb_b64(str(p), p.stat().st_mtime, max_px)
    return f"data:image/jpeg;base64,{b64}" if b64 else ""

def tile_html(colors, caption="", images=None, height=210):
    srcs = [s for s in (img_src(p) for p in (images or [])[:3]) if s]
    cap = f'<span class="tile-cap">{_esc(caption)}</span>' if caption else ""
    if len(srcs) == 1:
        inner = f'<img src="{srcs[0]}" alt="">'
    elif srcs:
        cols = 2 if len(srcs) > 1 else 1
        inner = f'<div class="collage" style="grid-template-columns:repeat({cols},1fr)">' + "".join(
            f'<img src="{s}" alt="">' for s in srcs) + "</div>"
    else:
        blocks = "".join(f'<span class="blk" style="background:{COLOR_HEX.get(c, "#c8ab87")}"></span>' for c in (colors or ["Beige"]))
        inner = blocks
    return f'<div class="tile" style="height:{height}px">{inner}{cap}</div>'


# ------------------- Web photos -------------------
def _secret(name):
    val = os.environ.get(name, "")
    if not val:
        try:
            val = st.secrets.get(name, "")
        except Exception:
            val = ""
    return val

def _online_query(outfit, gender=""):
    who = "women" if str(gender).lower().startswith("f") else "men"
    top = outfit.get("top", "").replace(" over a white shirt", "")
    bottom = outfit.get("bottom", "")
    return [f"{who} outfit {top} {bottom}".strip(), f"{top} {bottom} outfit".strip(), f"{who} {top} outfit".strip()]

def _search_photo_urls(query, n=3, errs=None):
    import requests
    errs = errs if errs is not None else []
    out = []
    gkey, cx = _secret("GOOGLE_API_KEY"), _secret("GOOGLE_CSE_ID")
    if gkey and cx:
        try:
            r = requests.get("https://www.googleapis.com/customsearch/v1", timeout=10,
                             params={"key": gkey, "cx": cx, "q": query, "searchType": "image",
                                     "num": min(10, n * 2), "safe": "active", "imgType": "photo"})
            js = r.json()
            if "error" in js:
                errs.append("Google: " + str(js["error"].get("message", "error"))[:80])
            for it in js.get("items", []):
                urls = [it.get("link"), (it.get("image") or {}).get("thumbnailLink")]
                out.append(([u for u in urls if u], f"Google Images · {it.get('displayLink') or 'web'}"))
        except Exception as e:
            errs.append(f"Google: {type(e).__name__}")
    if len(out) < n:
        try:
            try:
                from ddgs import DDGS
            except ImportError:
                from duckduckgo_search import DDGS
            for it in DDGS().images(query, max_results=n * 3) or []:
                urls = [u for u in (it.get("image"), it.get("thumbnail")) if u]
                if urls:
                    out.append((urls, f"Web image · {it.get('source') or 'search'}"))
        except Exception as e:
            errs.append(f"Web search: {type(e).__name__}")
    return out

def _download_image(urls, dest):
    import requests
    for url in urls:
        try:
            resp = requests.get(url, timeout=12, headers={"User-Agent": "Mozilla/5.0 AIStylistBuddy/1.0"})
            if resp.ok and len(resp.content) > 2000 and resp.content[:3] in (b"\xff\xd8\xff", b"\x89PN", b"RIF"):
                dest.write_bytes(resp.content)
                return True
        except Exception:
            continue
    return False

def _meta_path(query):
    first = query[0] if isinstance(query, (list, tuple)) else query
    return DEMO_CACHE_DIR / f"web_{hashlib.md5(first.encode()).hexdigest()[:12]}.json"

def web_images(query, n=3):
    queries = list(query) if isinstance(query, (list, tuple)) else [query]
    meta = _meta_path(queries)
    if meta.exists():
        try:
            data = json.loads(meta.read_text())
            paths = [p for p in data.get("paths", []) if Path(p).exists()]
            if paths:
                return paths, data.get("credits", [])
        except Exception:
            pass
    paths, credits, errs = [], [], []
    for q in queries:
        for urls, credit in _search_photo_urls(q, n, errs):
            if len(paths) >= n:
                break
            f = meta.with_name(f"{meta.stem}_{len(paths)}.jpg")
            if _download_image(urls, f):
                paths.append(str(f)); credits.append(credit)
        if paths:
            break
    meta.write_text(json.dumps({"paths": paths, "credits": credits, "ts": time.time(), "err": ""}))
    return paths, credits

def miss_reason(query):
    try:
        return json.loads(_meta_path(query).read_text()).get("err", "")
    except Exception:
        return ""

def online_images(outfit, gender="", n=3):
    return web_images(_online_query(outfit, gender), n)

def wardrobe_item_images(item, gender=""):
    who = "women" if str(gender).lower().startswith("f") else "men"
    name = item.get("name", "") or item.get("category", "")
    return web_images([f"{item.get('color', '')} {name} {who} clothing", f"{item.get('color', '')} {name}"], 1)

def prefetch_online_images(looks, gender=""):
    outfits = [l["outfit"] for l in looks if not l.get("outfit", {}).get("from_wardrobe")]
    if outfits:
        with ThreadPoolExecutor(max_workers=6) as ex:
            list(ex.map(lambda o: online_images(o, gender), outfits))
    return looks

def _user_gender():
    p = globals().get("profile") or {}
    try:
        return p.get("gender", "") or ""
    except Exception:
        return ""

def look_visual(look, image_path="", height=210):
    outfit = look.get("outfit", {})
    caption = " · ".join(x for x in (look.get("occasion", ""), "Your wardrobe" if outfit.get("from_wardrobe") else "") if x)
    images = [image_path] if image_path and Path(image_path).exists() else outfit.get("images", [])
    if not images and not outfit.get("from_wardrobe"):
        images, _ = online_images(outfit, _user_gender())
    return tile_html(outfit.get("colors", []), caption, images, height)

def _popover(label):
    if hasattr(st, "popover"):
        return st.popover(label, use_container_width=True)
    return st.expander(label)


# ============================================================
# DATABASE & AUTHENTICATION (Updated with Email & Password Reset)
# ============================================================

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def _has_col(conn, table, col):
    return any(r[1] == col for r in conn.execute(f"PRAGMA table_info({table})").fetchall())

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        reset_token TEXT,
        reset_token_expires TEXT,
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS profiles (
        user_id INTEGER PRIMARY KEY,
        name TEXT,
        age INTEGER,
        gender TEXT,
        height REAL,
        chest REAL,
        waist REAL,
        hips REAL,
        preferred_colors TEXT,
        clothing_style TEXT,
        hair_length TEXT,
        hair_type TEXT,
        current_hairstyle TEXT,
        hair_preferences TEXT,
        fashion_interests TEXT,
        profile_photo TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS wardrobe (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        category TEXT,
        color TEXT,
        style TEXT,
        occasion TEXT,
        image_path TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        look_json TEXT NOT NULL,
        action TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        look_json TEXT NOT NULL,
        occasion TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS saved_looks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        look_json TEXT NOT NULL,
        occasion TEXT,
        notes TEXT DEFAULT '',
        favorite INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS generated_images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        look_json TEXT NOT NULL,
        image_path TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS collections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS pending_generations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        look_json TEXT NOT NULL,
        extra_prompt TEXT DEFAULT '',
        error TEXT DEFAULT '',
        attempts INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );
    """)

    # Migrations for existing databases
    if not _has_col(conn, "users", "email"):
        cur.execute("ALTER TABLE users ADD COLUMN email TEXT")
    if not _has_col(conn, "users", "reset_token"):
        cur.execute("ALTER TABLE users ADD COLUMN reset_token TEXT")
    if not _has_col(conn, "users", "reset_token_expires"):
        cur.execute("ALTER TABLE users ADD COLUMN reset_token_expires TEXT")
    if not _has_col(conn, "feedback", "reason"):
        cur.execute("ALTER TABLE feedback ADD COLUMN reason TEXT DEFAULT ''")
    if not _has_col(conn, "saved_looks", "collection_id"):
        cur.execute("ALTER TABLE saved_looks ADD COLUMN collection_id INTEGER")
    if not _has_col(conn, "saved_looks", "image_path"):
        cur.execute("ALTER TABLE saved_looks ADD COLUMN image_path TEXT DEFAULT ''")
        
    conn.commit()
    conn.close()

init_db()

PBKDF2_ITERATIONS = 200_000

def hash_password(password):
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), PBKDF2_ITERATIONS).hex()
    return f"pbkdf2${PBKDF2_ITERATIONS}${salt}${digest}"

def verify_password(password, stored):
    if not stored: return False
    if stored.startswith("pbkdf2$"):
        try:
            _, iters, salt, digest = stored.split("$")
            calc = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), int(iters)).hex()
        except (ValueError, TypeError):
            return False
        return hmac.compare_digest(calc, digest)
    legacy = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return hmac.compare_digest(legacy, stored)

def is_valid_email(email):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return bool(re.match(pattern, email))

def register(username, email, password):
    username = username.strip().lower()
    email = email.strip().lower()
    if not username or not email or not password: 
        return False, "Username, email, and password are required."
    if not is_valid_email(email):
        return False, "Please enter a valid email address."
    if len(password) < 6: 
        return False, "Password must be at least 6 characters."
    try:
        conn = get_conn()
        conn.execute("INSERT INTO users(username,email,password_hash,created_at) VALUES(?,?,?,?)", 
                     (username, email, hash_password(password), datetime.now().isoformat()))
        conn.commit()
        conn.close()
        return True, "Account created successfully. You can log in now."
    except sqlite3.IntegrityError:
        return False, "Username or email already exists."

def login(username_or_email, password):
    val = username_or_email.strip().lower()
    conn = get_conn()
    row = conn.execute("SELECT id, username, password_hash FROM users WHERE username=? OR email=?", (val, val)).fetchone()
    if not row or not verify_password(password, row["password_hash"]):
        conn.close()
        return None
    conn.close()
    return row

def create_password_reset_token(identifier):
    val = identifier.strip().lower()
    conn = get_conn()
    user = conn.execute("SELECT id FROM users WHERE username=? OR email=?", (val, val)).fetchone()
    if not user:
        conn.close()
        return None, "User not found with that username or email."
    
    token = secrets.token_urlsafe(32)
    expires = (datetime.now() + timedelta(minutes=15)).isoformat()
    
    conn.execute("UPDATE users SET reset_token=?, reset_token_expires=? WHERE id=?", 
                 (token, expires, user["id"]))
    conn.commit()
    conn.close()
    return token, "Success"

def get_profile(user_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM profiles WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else {}

def save_profile(user_id, data):
    conn = get_conn()
    exists = conn.execute("SELECT user_id FROM profiles WHERE user_id=?", (user_id,)).fetchone()
    values = (
        data["name"], data["age"], data["gender"], data["height"],
        data["chest"], data["waist"], data["hips"],
        json.dumps(data["preferred_colors"]), json.dumps(data["clothing_style"]),
        data["hair_length"], data["hair_type"], data["current_hairstyle"],
        data["hair_preferences"], data["fashion_interests"], data.get("profile_photo", "")
    )
    if exists:
        conn.execute("""
            UPDATE profiles SET name=?, age=?, gender=?, height=?, chest=?, waist=?, hips=?,
            preferred_colors=?, clothing_style=?, hair_length=?, hair_type=?, current_hairstyle=?,
            hair_preferences=?, fashion_interests=?, profile_photo=? WHERE user_id=?
        """, values + (user_id,))
    else:
        conn.execute("""
            INSERT INTO profiles(name,age,gender,height,chest,waist,hips,preferred_colors,
            clothing_style,hair_length,hair_type,current_hairstyle,hair_preferences,
            fashion_interests,profile_photo,user_id) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, values + (user_id,))
    conn.commit()
    conn.close()

def parse_profile(profile):
    p = dict(profile)
    for key in ("preferred_colors", "clothing_style"):
        try: p[key] = json.loads(p.get(key) or "[]")
        except Exception: p[key] = []
    return p


# ============================================================
# CATALOG & ENGINE DATA (OUTFITS, HAIRSTYLES, ETC.)
# ============================================================
OCCASIONS = ["Interview", "College", "Office", "Wedding", "Party", "Date", "Casual outing", "Festival"]
STYLES = ["Casual", "Formal", "Smart Casual", "Streetwear", "Minimal", "Traditional", "Trendy"]
COLORS = ["Black", "White", "Blue", "Navy", "Grey", "Beige", "Brown", "Green", "Maroon", "Pink"]
HAIR_LENGTHS = ["Short", "Medium", "Long"]
HAIR_TYPES = ["Straight", "Wavy", "Curly", "Coily"]
SEASONS = ["Spring", "Summer", "Autumn", "Winter"]
ALL_SEASONS = list(SEASONS)

OUTFITS = [
    {"name":"Classic Interview Look","top":"White formal shirt","bottom":"Navy tailored trousers","shoes":"Black formal shoes","accessories":["Minimal watch"],"colors":["White","Navy"],"styles":["Formal","Minimal"],"occasions":["Interview","Office"],"seasons":ALL_SEASONS,"formality":5,"trend":3,"fabric":"Crisp cotton poplin with a wool-blend trouser","fit":"Tailored through the shoulder, trouser breaks just above the shoe"},
    {"name":"Smart College Look","top":"Light blue Oxford shirt","bottom":"Dark straight-fit jeans","shoes":"Clean white sneakers","accessories":["Watch"],"colors":["Blue","White"],"styles":["Smart Casual","Casual"],"occasions":["College","Casual outing"],"seasons":["Spring","Summer","Autumn"],"formality":3,"trend":4,"fabric":"Washed cotton Oxford with mid-weight denim","fit":"Shirt worn untucked or half-tucked, jeans straight not skinny"},
    {"name":"Minimal Office Look","top":"Beige knit polo","bottom":"Charcoal trousers","shoes":"Brown loafers","accessories":["Leather belt"],"colors":["Beige","Grey","Brown"],"styles":["Smart Casual","Minimal"],"occasions":["Office","Date"],"seasons":["Autumn","Winter","Spring"],"formality":3.5,"trend":4,"fabric":"Fine-gauge merino knit with a matte wool trouser","fit":"Polo skims the waistband, no bunching at the hem"},
    {"name":"Modern Party Look","top":"Black fitted shirt","bottom":"Black tailored trousers","shoes":"Black loafers","accessories":["Metal watch"],"colors":["Black"],"styles":["Trendy","Formal"],"occasions":["Party","Date"],"seasons":ALL_SEASONS,"formality":4,"trend":3,"fabric":"Soft satin-finish cotton with a drapey trouser","fit":"Slim through the torso, top button open"},
    {"name":"Wedding Fusion Look","top":"Ivory kurta","bottom":"Beige trousers","shoes":"Brown ethnic loafers","accessories":["Watch"],"colors":["White","Beige","Brown"],"styles":["Traditional"],"occasions":["Wedding","Festival"],"seasons":["Autumn","Winter","Spring"],"formality":4,"trend":5,"fabric":"Cotton-silk kurta with a light cotton trouser","fit":"Kurta ends mid-thigh, trousers slim and tapered"},
    {"name":"Casual Weekend Look","top":"Plain black T-shirt","bottom":"Blue jeans","shoes":"White sneakers","accessories":["Cap"],"colors":["Black","Blue","White"],"styles":["Casual","Streetwear"],"occasions":["Casual outing","College"],"seasons":["Spring","Summer"],"formality":1.5,"trend":2,"fabric":"Heavy cotton jersey with rigid denim","fit":"Relaxed, with a clean sleeve length at mid-bicep"},
    {"name":"Linen Summer Date Look","top":"Light blue linen shirt","bottom":"Beige chinos","shoes":"Tan leather loafers","accessories":["Sunglasses"],"colors":["Blue","Beige","Brown"],"styles":["Smart Casual","Minimal"],"occasions":["Date","Casual outing","Wedding"],"seasons":["Summer","Spring"],"formality":3,"trend":4,"fabric":"Breathable linen with cotton twill chinos","fit":"Sleeves rolled twice, shirt loosely tucked"},
    {"name":"Layered Winter Smart Look","top":"Grey crew-neck sweater over a white shirt","bottom":"Navy wool trousers","shoes":"Brown leather boots","accessories":["Wool scarf"],"colors":["Grey","White","Navy","Brown"],"styles":["Smart Casual","Minimal"],"occasions":["Office","College","Date"],"seasons":["Winter","Autumn"],"formality":3.5,"trend":3,"fabric":"Lambswool knit over cotton, brushed wool trouser","fit":"Shirt collar visible above the knit, trousers full length"},
    {"name":"Festive Maroon Kurta Look","top":"Maroon kurta","bottom":"Cream churidar","shoes":"Tan mojari","accessories":["Pocket square"],"colors":["Maroon","White","Beige"],"styles":["Traditional","Trendy"],"occasions":["Festival","Wedding","Party"],"seasons":["Winter","Autumn"],"formality":4,"trend":4,"fabric":"Textured jacquard cotton with a soft churidar","fit":"Kurta cut straight, churidar gathers slightly at the ankle"},
    {"name":"Street Layer Look","top":"Oversized grey hoodie","bottom":"Black cargo pants","shoes":"Chunky white sneakers","accessories":["Crossbody bag"],"colors":["Grey","Black","White"],"styles":["Streetwear","Casual"],"occasions":["Casual outing","College","Party"],"seasons":["Autumn","Winter","Spring"],"formality":1,"trend":5,"fabric":"Brushed fleece with ripstop cotton","fit":"Boxy on top, tapered at the ankle to balance volume"},
]

HAIRSTYLES = [
    {"name":"Textured crop","lengths":["Short","Medium"],"types":["Straight","Wavy","Curly"],"occasions":["Interview","College","Office","Casual outing","Party"],"tip":"Low-maintenance and clean."},
    {"name":"Classic side part","lengths":["Short","Medium"],"types":["Straight","Wavy"],"occasions":["Interview","Office","Wedding"],"tip":"Professional and polished."},
    {"name":"Low fade","lengths":["Short","Medium"],"types":["Straight","Wavy","Curly"],"occasions":["College","Party","Casual outing"],"tip":"Sharp modern finish."},
    {"name":"Messy quiff","lengths":["Short","Medium"],"types":["Straight","Wavy"],"occasions":["Date","Party","College"],"tip":"Adds natural texture and volume."},
    {"name":"Slick back","lengths":["Short","Medium","Long"],"types":["Straight","Wavy"],"occasions":["Wedding","Party","Office"],"tip":"Refined formal presentation."},
]

FORMALITY = {"Formal": 5, "Traditional": 4, "Smart Casual": 3.5, "Minimal": 3, "Trendy": 2.5, "Casual": 2, "Streetwear": 1.5}
NEUTRALS = {"Black", "White", "Grey", "Beige", "Navy", "Brown"}
GOOD_PAIRS = [frozenset(p) for p in (("Navy", "White"), ("Beige", "Brown"), ("Grey", "Navy"), ("Black", "White"),
              ("Blue", "Beige"), ("Blue", "White"), ("Grey", "White"), ("Maroon", "Beige"), ("Brown", "White"),
              ("Navy", "Beige"), ("Green", "Beige"), ("Pink", "Grey"))]
CLASH_PAIRS = [frozenset(p) for p in (("Pink", "Maroon"), ("Green", "Blue"), ("Black", "Brown"), ("Navy", "Black"),
               ("Pink", "Green"), ("Maroon", "Green"), ("Maroon", "Blue"))]
DISLIKE_REASONS = ["Not my colours", "Not my style", "Wrong for the occasion", "Hairstyle isn't me", "Just not for me"]
REASON_SCOPE = {
    "Not my colours": ("color",), "Not my style": ("style",), "Wrong for the occasion": ("occasion",),
    "Hairstyle isn't me": ("hair",), "Just not for me": ("color", "style", "hair", "source", "outfit"),
}

def formality_label(f):
    if f >= 4.5: return "Sharp and formal"
    if f >= 3.5: return "Polished"
    if f >= 2.5: return "Relaxed smart"
    if f >= 1.5: return "Easy casual"
    return "Street"

def current_season():
    m = datetime.now().month
    return "Spring" if m in (3, 4, 5) else "Summer" if m in (6, 7, 8) else "Autumn" if m in (9, 10, 11) else "Winter"


# ============================================================
# STORAGE & RECOMMENDATION HELPERS
# ============================================================
def save_history(user_id, look):
    conn = get_conn()
    conn.execute("INSERT INTO history(user_id,look_json,occasion,created_at) VALUES(?,?,?,?)",
                 (user_id, json.dumps(look), look.get("occasion",""), datetime.now().isoformat()))
    conn.commit()
    conn.close()

def recent_occasion(user_id, default="Casual outing"):
    conn = get_conn()
    rows = conn.execute("SELECT occasion FROM history WHERE user_id=? ORDER BY id DESC LIMIT 20", (user_id,)).fetchall()
    conn.close()
    counts = {}
    for r in rows:
        if r["occasion"] in OCCASIONS:
            counts[r["occasion"]] = counts.get(r["occasion"], 0) + 1
    return max(counts, key=counts.get) if counts else default

def save_feedback(user_id, look, action, reason=""):
    conn = get_conn()
    conn.execute("INSERT INTO feedback(user_id,look_json,action,created_at,reason) VALUES(?,?,?,?,?)",
                 (user_id, json.dumps(look), action, datetime.now().isoformat(), reason or ""))
    conn.commit()
    conn.close()

def reset_feedback(user_id):
    conn = get_conn()
    conn.execute("DELETE FROM feedback WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

DEFAULT_COLLECTION = "Favorites"

def ensure_default_collection(user_id):
    conn = get_conn()
    row = conn.execute("SELECT id FROM collections WHERE user_id=? AND name=?", (user_id, DEFAULT_COLLECTION)).fetchone()
    if row:
        cid = row["id"]
    else:
        cur = conn.execute("INSERT INTO collections(user_id,name,created_at) VALUES(?,?,?)",
                           (user_id, DEFAULT_COLLECTION, datetime.now().isoformat()))
        cid = cur.lastrowid
    conn.execute("UPDATE saved_looks SET collection_id=? WHERE user_id=? AND collection_id IS NULL", (cid, user_id))
    conn.commit()
    conn.close()
    return cid

def get_collections(user_id):
    conn = get_conn()
    rows = conn.execute(
        "SELECT c.id, c.name, c.created_at, (SELECT COUNT(*) FROM saved_looks s WHERE s.collection_id=c.id) AS n "
        "FROM collections c WHERE c.user_id=? ORDER BY (c.name=?) DESC, c.id", (user_id, DEFAULT_COLLECTION)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def create_collection(user_id, name):
    name = (name or "").strip()[:40]
    if not name: return None
    conn = get_conn()
    row = conn.execute("SELECT id FROM collections WHERE user_id=? AND lower(name)=lower(?)", (user_id, name)).fetchone()
    if row:
        conn.close()
        return row["id"]
    cur = conn.execute("INSERT INTO collections(user_id,name,created_at) VALUES(?,?,?)",
                       (user_id, name, datetime.now().isoformat()))
    conn.commit()
    cid = cur.lastrowid
    conn.close()
    return cid

def delete_collection(user_id, collection_id):
    default_id = ensure_default_collection(user_id)
    if collection_id == default_id: return
    conn = get_conn()
    conn.execute("UPDATE saved_looks SET collection_id=? WHERE user_id=? AND collection_id=?", (default_id, user_id, collection_id))
    conn.execute("DELETE FROM collections WHERE id=? AND user_id=?", (collection_id, user_id))
    conn.commit()
    conn.close()

def save_look(user_id, look, collection_id=None, image_path=""):
    if collection_id is None:
        collection_id = ensure_default_collection(user_id)
    conn = get_conn()
    conn.execute(
        "INSERT INTO saved_looks(user_id,name,look_json,occasion,created_at,collection_id,image_path) VALUES(?,?,?,?,?,?,?)",
        (user_id, look["outfit"]["name"], json.dumps(look), look.get("occasion",""), datetime.now().isoformat(),
         collection_id, image_path or ""))
    conn.commit()
    conn.close()
    return True

def get_saved_looks(user_id, collection_id=None, limit=None):
    conn = get_conn()
    sql = ("SELECT s.*, c.name AS collection_name FROM saved_looks s "
           "LEFT JOIN collections c ON c.id=s.collection_id WHERE s.user_id=?")
    args = [user_id]
    if collection_id is not None:
        sql += " AND s.collection_id=?"
        args.append(collection_id)
    sql += " ORDER BY s.id DESC"
    if limit:
        sql += f" LIMIT {int(limit)}"
    rows = conn.execute(sql, args).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def move_saved_look(user_id, look_id, collection_id):
    conn = get_conn()
    conn.execute("UPDATE saved_looks SET collection_id=? WHERE id=? AND user_id=?", (collection_id, look_id, user_id))
    conn.commit()
    conn.close()

def delete_saved_look(user_id, look_id):
    conn = get_conn()
    conn.execute("DELETE FROM saved_looks WHERE id=? AND user_id=?", (look_id, user_id))
    conn.commit()
    conn.close()

def save_generated_image(user_id, look, image_path):
    conn = get_conn()
    conn.execute(
        "INSERT INTO generated_images(user_id,look_json,image_path,created_at) VALUES(?,?,?,?)",
        (user_id, json.dumps(look), image_path, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()

def get_generated_images(user_id, occasion="All", limit=20):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM generated_images WHERE user_id=? ORDER BY id DESC", (user_id,)).fetchall()
    conn.close()
    out = []
    for r in rows:
        d = dict(r)
        try: d["look"] = json.loads(d["look_json"])
        except Exception: d["look"] = {}
        if occasion != "All" and d["look"].get("occasion") != occasion: continue
        out.append(d)
        if len(out) >= limit: break
    return out

def add_pending(user_id, look, extra_prompt, error):
    conn = get_conn()
    cur = conn.execute(
        "INSERT INTO pending_generations(user_id,look_json,extra_prompt,error,created_at) VALUES(?,?,?,?,?)",
        (user_id, json.dumps(look), extra_prompt or "", str(error)[:500], datetime.now().isoformat()))
    conn.commit()
    pid = cur.lastrowid
    conn.close()
    return pid

def bump_pending(pending_id, user_id, error):
    conn = get_conn()
    conn.execute("UPDATE pending_generations SET attempts=attempts+1, error=? WHERE id=? AND user_id=?",
                 (str(error)[:500], pending_id, user_id))
    conn.commit()
    conn.close()

def get_pending(user_id):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM pending_generations WHERE user_id=? ORDER BY id DESC", (user_id,)).fetchall()
    conn.close()
    out = []
    for r in rows:
        d = dict(r)
        try: d["look"] = json.loads(d["look_json"])
        except Exception: continue
        out.append(d)
    return out

def delete_pending(pending_id, user_id):
    conn = get_conn()
    conn.execute("DELETE FROM pending_generations WHERE id=? AND user_id=?", (pending_id, user_id))
    conn.commit()
    conn.close()

def add_wardrobe(user_id, name, category, color, style, occasion, image_path=""):
    conn = get_conn()
    conn.execute("INSERT INTO wardrobe(user_id,name,category,color,style,occasion,image_path,created_at) VALUES(?,?,?,?,?,?,?,?)",
                 (user_id, name, category, color, style, occasion, image_path, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_wardrobe(user_id):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM wardrobe WHERE user_id=? ORDER BY id DESC", (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def delete_wardrobe_item(user_id, item_id):
    conn = get_conn()
    conn.execute("DELETE FROM wardrobe WHERE id=? AND user_id=?", (item_id, user_id))
    conn.commit()
    conn.close()

def save_upload(uploaded, prefix):
    ext = Path(uploaded.name).suffix.lower()
    path = UPLOAD_DIR / f"{prefix}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}{ext}"
    path.write_bytes(uploaded.getbuffer())
    return str(path)

ACTION_WEIGHT = {"like": 1.0, "save": 1.5, "generate": 2.0, "dislike": -1.2}

def empty_prefs():
    return {"color": {}, "style": {}, "hair": {}, "source": {}, "occasion": {}, "outfit": {}, "n": 0, "likes": 0, "passes": 0}

def learn_preferences(user_id):
    prefs = empty_prefs()
    if not user_id: return prefs
    conn = get_conn()
    rows = conn.execute("SELECT look_json, action, reason FROM feedback WHERE user_id=? ORDER BY id DESC LIMIT 200", (user_id,)).fetchall()
    conn.close()
    for rank, row in enumerate(rows):
        weight = ACTION_WEIGHT.get(row["action"])
        if weight is None: continue
        try: look = json.loads(row["look_json"])
        except Exception: continue
        w = weight * (0.97 ** rank)
        scope = REASON_SCOPE.get(row["reason"] or "", ("color", "style", "hair", "source", "outfit")) if weight < 0 \
            else ("color", "style", "hair", "source", "outfit")
        outfit = look.get("outfit", {})
        def bump(dim, key):
            if key and dim in scope:
                prefs[dim][key] = prefs[dim].get(key, 0) + w
        for c in outfit.get("colors", []): bump("color", c)
        for s in outfit.get("styles", []): bump("style", s)
        bump("hair", look.get("hairstyle", {}).get("name"))
        bump("source", look.get("source"))
        bump("outfit", outfit.get("name"))
        if weight < 0 and "occasion" in scope: bump("occasion", look.get("occasion"))
        prefs["n"] += 1
        if weight > 0: prefs["likes"] += 1
        else: prefs["passes"] += 1
    return prefs

def trending_counts():
    conn = get_conn()
    rows = conn.execute("SELECT look_json, action FROM feedback WHERE action IN ('like','save','generate') ORDER BY id DESC LIMIT 600").fetchall()
    conn.close()
    counts = {}
    for r in rows:
        try: name = json.loads(r["look_json"]).get("outfit", {}).get("name")
        except Exception: continue
        if name: counts[name] = counts.get(name, 0) + 1
    return counts

def _combo_score(items, occasion):
    score, notes = 0.0, []
    colors = [i.get("color") for i in items if i.get("color")]
    uniq = list(dict.fromkeys(colors))
    pairs = list(itertools.combinations(uniq, 2))
    good = [p for p in pairs if frozenset(p) in GOOD_PAIRS]
    bad = [p for p in pairs if frozenset(p) in CLASH_PAIRS]
    if good:
        score += 6 * len(good)
        notes.append(f"{good[0][0]} and {good[0][1]} are a classic pairing")
    if bad: score -= 7 * len(bad)
    accents = [c for c in uniq if c not in NEUTRALS]
    if len(accents) > 1: score -= 8
    elif len(accents) == 1 and len(uniq) > 1:
        score += 4
        notes.append(f"{accents[0]} is the only accent colour")
    if len(uniq) == 1 and uniq[0] in NEUTRALS:
        score += 3
        notes.append("A clean one-colour outfit")
    forms = [FORMALITY.get(i.get("style"), 3) for i in items if i.get("style")]
    if forms:
        spread = max(forms) - min(forms)
        if spread <= 1.5:
            score += 6
            notes.append("Every piece sits at the same level of dressiness")
        elif spread > 2.5: score -= 8
    for i in items:
        occ = i.get("occasion") or "Any"
        if occ == occasion: score += 4
        elif occ not in ("Any", ""): score -= 5
    return score, notes

def build_wardrobe_outfits(wardrobe, occasion=None, keep=12):
    tops = [i for i in wardrobe if i.get("category") == "Top"][:8]
    bottoms = [i for i in wardrobe if i.get("category") == "Bottom"][:8]
    shoes = [i for i in wardrobe if i.get("category") == "Shoes"][:8]
    accessories = [i for i in wardrobe if i.get("category") == "Accessory"]
    built = []
    for t, b, sh in itertools.product(tops, bottoms, shoes):
        items = [t, b, sh]
        wscore, notes = _combo_score(items, occasion)
        colors = list(dict.fromkeys(i["color"] for i in items if i.get("color")))
        styles = list(dict.fromkeys(i["style"] for i in items if i.get("style")))
        outfit_colors = set(colors)
        acc = next((a for a in accessories if a.get("color") in NEUTRALS or a.get("color") in outfit_colors), None)
        specific = sorted({i["occasion"] for i in items if i.get("occasion") and i["occasion"] != "Any"})
        forms = [FORMALITY.get(s, 3) for s in styles] or [3]
        built.append({
            "name": f"{t['name']} + {b['name']}",
            "top": t["name"], "bottom": b["name"], "shoes": sh["name"],
            "accessories": [acc["name"]] if acc else [], "colors": colors, "styles": styles,
            "occasions": specific or list(OCCASIONS), "seasons": ALL_SEASONS,
            "formality": round(sum(forms) / len(forms), 1),
            "images": [i["image_path"] for i in (items + ([acc] if acc else [])) if i.get("image_path")][:3],
            "from_wardrobe": True, "wardrobe_score": wscore, "match_notes": notes,
        })
    built.sort(key=lambda o: -o["wardrobe_score"])
    return built[:keep]

def _clamp(x, lo, hi):
    return max(lo, min(hi, x))

def pick_hair(profile, occasion, seed, prefs):
    length, htype = profile.get("hair_length"), profile.get("hair_type")
    def fit(h):
        s = (3 if length in h["lengths"] else 0) + (3 if htype in h["types"] else 0) + (2 if occasion in h["occasions"] else 0)
        return s + _clamp(prefs["hair"].get(h["name"], 0), -2, 2)
    ranked = sorted(HAIRSTYLES, key=lambda h: (-fit(h), zlib.crc32((seed + h["name"]).encode())))
    best = ranked[0]
    why = None
    if length in best["lengths"] and htype in best["types"]:
        why = f"{best['name']} works with your {str(length).lower()}, {str(htype).lower()} hair"
    return best, why

def build_look(outfit, profile, occasion, situation="", prefs=None, season=None, lead_reason=None):
    prefs = prefs or empty_prefs()
    score, reasons = 0.0, []
    if lead_reason:
        reasons.append(lead_reason)

    if occasion in outfit["occasions"]:
        score += 40
        reasons.append(f"Built for {occasion.lower()} dressing")
    else:
        score += 8

    matched_colors = [c for c in outfit.get("colors", []) if c in profile.get("preferred_colors", [])]
    if matched_colors:
        score += min(8 * len(matched_colors), 16)
        reasons.append("Uses colours you like: " + ", ".join(matched_colors))
    matched_styles = [s for s in outfit.get("styles", []) if s in profile.get("clothing_style", [])]
    if matched_styles:
        score += min(8 * len(matched_styles), 16)
        reasons.append("Matches your style: " + ", ".join(matched_styles))

    if season and season in outfit.get("seasons", []) and len(outfit.get("seasons", [])) < 4:
        score += 6
        reasons.append(f"Suited to {season.lower()}")

    tokens = set(re.findall(r"[a-z]+", (situation or "").lower()))
    styles = outfit.get("styles", [])
    if tokens & {"interview", "office", "meeting", "conference", "presentation"} and ("Formal" in styles or "Smart Casual" in styles):
        score += 8
        reasons.append("Reads professional for the setting you described")
    if tokens & {"wedding", "festival", "ceremony"} and "Traditional" in styles:
        score += 8
        reasons.append("Traditional pieces fit the ceremony you described")
    if tokens & {"casual", "college", "weekend", "outing"} and any(s in styles for s in ("Casual", "Streetwear", "Smart Casual")):
        score += 6
        reasons.append("Easy enough for the relaxed day you described")
    if tokens & {"hot", "summer", "humid", "warm"} and "Summer" in outfit.get("seasons", []):
        score += 5
        reasons.append("Light fabrics for warm weather")
    if tokens & {"cold", "winter", "chilly", "cool"} and "Winter" in outfit.get("seasons", []):
        score += 5
        reasons.append("Layered for cooler weather")

    # what this person has taught the app so far
    for c in outfit.get("colors", []):
        w = prefs["color"].get(c, 0)
        score += _clamp(w * 3, -12, 12)
        if w >= 1: reasons.append(f"You've liked {c.lower()} looks before")
        elif w <= -1: reasons.append(f"Heads up: you've passed on {c.lower()} before")
    for s in styles:
        w = prefs["style"].get(s, 0)
        score += _clamp(w * 3, -12, 12)
        if w >= 1: reasons.append(f"You tend to like {s.lower()} styling")
    score += _clamp(prefs["outfit"].get(outfit["name"], 0) * 4, -15, 15)
    score += _clamp(prefs["occasion"].get(occasion, 0) * 2, -6, 0)
    source = "My Wardrobe" if outfit.get("from_wardrobe") else "Online"
    score += _clamp(prefs["source"].get(source, 0) * 1.5, -5, 5)

    if outfit.get("from_wardrobe"):
        score += outfit.get("wardrobe_score", 0)
        reasons += outfit.get("match_notes", [])[:2]
        reasons.append("Made entirely from pieces you already own")

    hair, hair_why = pick_hair(profile, occasion, outfit["name"], prefs)
    if hair_why:
        reasons.append(hair_why)

    seen, uniq = set(), []
    for r in reasons:
        if r not in seen:
            seen.add(r); uniq.append(r)

    return {
        "outfit": outfit, "hairstyle": hair, "occasion": occasion, "situation": situation,
        "score": round(score, 1), "reasons": uniq[:6], "source": source,
        "products": product_matches(outfit, profile, occasion) if source == "Online" else [],
    }

def recommend(profile, occasion, situation, source="Online", wardrobe=None, prefs=None, user_id=None, limit=9, season=None):
    pool = []
    if source in ("Online", "Both"):
        pool += OUTFITS
    if source in ("My Wardrobe", "Both"):
        pool += build_wardrobe_outfits(wardrobe or [], occasion)
    prefs = prefs if prefs is not None else learn_preferences(user_id)
    looks = [build_look(o, profile, occasion, situation, prefs, season) for o in pool]
    looks.sort(key=lambda x: (-x["score"], x["outfit"]["name"]))
    return prefetch_online_images(looks[:limit], profile.get("gender", ""))

def trending_looks(profile, prefs, n=3):
    counts = trending_counts()
    ranked = sorted(OUTFITS, key=lambda o: (-(o.get("trend", 0) + 2 * counts.get(o["name"], 0)), o["name"]))[:n]
    out = []
    for o in ranked:
        c = counts.get(o["name"], 0)
        lead = f"{c} saves and likes from people using this app" if c >= 3 else "An editor's pick that keeps coming up this season"
        out.append(build_look(o, profile, o["occasions"][0], "", prefs, None, lead_reason=lead))
    return prefetch_online_images(out, profile.get("gender", ""))

def seasonal_looks(profile, prefs, season, n=3):
    pool = [o for o in OUTFITS if season in o.get("seasons", []) and len(o["seasons"]) < 4] or OUTFITS
    looks = [build_look(o, profile, o["occasions"][0], "", prefs, season,
                        lead_reason=f"Fabric for {season.lower()}: {o.get('fabric', '').lower()}") for o in pool]
    looks.sort(key=lambda x: (-x["score"], x["outfit"]["name"]))
    return prefetch_online_images(looks[:n], profile.get("gender", ""))


# ============================================================
# ONLINE PRODUCT MATCHING (curated search links, no live scraping)
# ============================================================

def product_matches(outfit, profile, occasion):
    prefs_c = set(profile.get("preferred_colors", []))
    out = []
    for slot, label in (("top", "Top"), ("bottom", "Bottom"), ("shoes", "Shoes")):
        desc = outfit.get(slot, "")
        if not desc:
            continue
        query = desc.replace(" over a white shirt", "")
        reasons = [f"Keeps the palette to {', '.join(outfit.get('colors', [])[:3]).lower()}"]
        hit = [c for c in outfit.get("colors", []) if c in prefs_c and c.lower() in desc.lower()]
        if hit:
            reasons.append(f"{hit[0].lower()} is one of your favourite colours")
        reasons.append(f"suits {occasion.lower()} and {', '.join(outfit.get('styles', [])[:1]).lower()} styling")
        slug = re.sub(r"[^a-z0-9]+", "-", query.lower()).strip("-")
        out.append({
            "slot": label, "item": desc, "why": "; ".join(reasons).capitalize() + ".",
            "links": [
                ("Amazon.in", f"https://www.amazon.in/s?k={quote_plus(query)}"),
                ("Myntra", f"https://www.myntra.com/{slug}"),
                ("Google Shopping", f"https://www.google.com/search?tbm=shop&q={quote_plus(query)}"),
            ],
        })
    return out


# ============================================================
# FLUX.1 KONTEXT - FREE HUGGING FACE ZEROGPU SPACE
# ============================================================

# FLUX.1 Kontext is an image-editing model: it accepts the user's
# profile photo plus a natural-language styling instruction.
# The public Hugging Face Space exposes an /infer endpoint.
FLUX_SPACE_ID = "black-forest-labs/FLUX.1-Kontext-Dev"


def generate_ai_look(profile, look, user_id=None, extra_prompt=""):
    """
    Generate an AI-styled preview from the user's profile photo.

    This is image editing / styling, not a specialized garment VTON
    model. The prompt asks FLUX Kontext to preserve the person while
    changing the outfit and hairstyle.
    """

    profile_photo = profile.get("profile_photo")
    if not profile_photo or not Path(profile_photo).exists():
        raise RuntimeError(
            "Please upload a valid full-body profile photo in the Profile section first."
        )

    try:
        from gradio_client import Client, handle_file
    except ImportError:
        raise RuntimeError(
            "gradio_client is not installed. Run: pip install -U gradio_client"
        )

    outfit = look.get("outfit", {})
    hair = look.get("hairstyle", {})

    prompt = f"""
Edit the uploaded photo of the same person into this complete fashion look.

PERSON PRESERVATION:
- Keep the same person and preserve identity and facial features.
- Preserve skin tone, body proportions, pose, hairstyle characteristics,
  hands, and overall appearance as much as possible.
- Keep exactly one person.
- Keep the original full-body composition whenever possible.
- Do not replace the person with a different model.

OUTFIT:
Top: {outfit.get("top", "")}
Bottom: {outfit.get("bottom", "")}
Shoes: {outfit.get("shoes", "")}
Accessories: {", ".join(outfit.get("accessories", []))}
Colors: {", ".join(outfit.get("colors", []))}
Style: {", ".join(outfit.get("styles", []))}

HAIRSTYLE:
{hair.get("name", "")}

OCCASION:
{look.get("occasion", "")}

SITUATION:
{look.get("situation", "")}

Make the selected clothing clearly visible and realistic.
Use realistic fabric, natural folds, believable fit, realistic anatomy,
natural lighting and a polished fashion-editorial appearance.

Do not add another person, text, logos, watermarks, or unrelated objects.
"""

    # Optional note typed by the user on the AI Stylist page.
    extra_prompt = (extra_prompt or "").strip()[:300]
    if extra_prompt:
        prompt += f"\nADDITIONAL STYLING NOTES FROM THE USER:\n{extra_prompt}\n"

    try:
        client = Client(
            FLUX_SPACE_ID,
            httpx_kwargs={"timeout": 600},
            verbose=False,
        )

        # The official Space uses:
        # infer(input_image, prompt, seed, randomize_seed,
        #       guidance_scale, steps)
        result = client.predict(
            handle_file(profile_photo),
            prompt,
            42,
            True,
            2.5,
            20,
            api_name="/infer",
        )

        # The Space returns: result image, seed, reuse-button state.
        result_image = result[0] if isinstance(result, (list, tuple)) else result

        if not result_image:
            raise RuntimeError(
                "FLUX returned no generated image. The public ZeroGPU Space "
                "may currently be busy or rate-limited."
            )

        # Gradio normally returns a local filepath for an Image output.
        if isinstance(result_image, dict):
            result_path = (
                result_image.get("path")
                or result_image.get("url")
                or result_image.get("name")
            )
        else:
            result_path = str(result_image)

        if result_path and Path(result_path).exists():
            suffix = Path(result_path).suffix or ".png"
            out_path = UPLOAD_DIR / (
                f"ai_outfit_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}{suffix}"
            )
            shutil.copy(result_path, out_path)

        elif result_path and result_path.startswith(("http://", "https://")):
            import requests

            response = requests.get(result_path, timeout=120)
            response.raise_for_status()

            out_path = UPLOAD_DIR / (
                f"ai_outfit_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.png"
            )
            out_path.write_bytes(response.content)

        else:
            # Some Gradio versions may return a PIL image.
            try:
                from PIL import Image
                if isinstance(result_image, Image.Image):
                    out_path = UPLOAD_DIR / (
                        f"ai_outfit_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.png"
                    )
                    result_image.save(out_path)
                else:
                    raise RuntimeError(
                        f"FLUX returned an unexpected image result: {type(result_image).__name__}"
                    )
            except ImportError:
                raise RuntimeError(
                    f"FLUX returned an unexpected image result: {result_image}"
                )

        if user_id is not None:
            save_generated_image(user_id, look, str(out_path))

        return str(out_path)

    except Exception as e:
        message = str(e)

        if "upstream Gradio app has raised an exception" in message:
            raise RuntimeError(
                "The FLUX public ZeroGPU server rejected the request or is busy. "
                "Please try again after a short wait."
            ) from e

        raise RuntimeError(
            f"FLUX.1 Kontext generation failed: {message}"
        ) from e



# ============================================================
# VIRTUAL TRY-ON - GPU BACKEND ON GOOGLE COLAB (IDM-VTON)
# ============================================================
# Run the companion notebook (AIStylist_TryOn_Colab.ipynb) in Google Colab. It prints a
# public URL (https://xxxx.gradio.live). Put it in .streamlit/secrets.toml as
#     TRYON_URL = "https://xxxx.gradio.live"
# or set the TRYON_URL environment variable. If TRYON_URL is empty, the public
# IDM-VTON Hugging Face Space is used instead (same API, but shared and often busy).
TRYON_SPACE_ID = "yisol/IDM-VTON"


def tryon_endpoint():
    return (_secret("TRYON_URL") or "").strip().rstrip("/") or TRYON_SPACE_ID


def generate_tryon(person_path, garment_path, garment_desc="", user_id=None, name="Virtual try-on"):
    """Dress the person in the chosen garment photo using IDM-VTON. Returns the saved image path."""
    if not person_path or not Path(person_path).exists():
        raise RuntimeError("Please choose or take a full-body photo of yourself first.")
    if not garment_path or not Path(garment_path).exists():
        raise RuntimeError("Please choose a garment photo first.")
    try:
        from gradio_client import Client, handle_file
    except ImportError:
        raise RuntimeError("gradio_client is not installed. Run: pip install -U gradio_client")

    try:
        client = Client(tryon_endpoint(), httpx_kwargs={"timeout": 900}, verbose=False)
        # IDM-VTON: tryon(person_editor_dict, garment_image, garment_description,
        #                 auto_mask, auto_crop, denoise_steps, seed) -> (result, masked_person)
        result = client.predict(
            {"background": handle_file(person_path), "layers": [], "composite": None},
            handle_file(garment_path),
            (garment_desc or "a garment").strip()[:120],
            True,      # auto-generate the clothing mask
            False,     # no auto-crop, keep the original framing
            30,        # denoise steps
            42,        # seed
            api_name="/tryon",
        )
        result_image = result[0] if isinstance(result, (list, tuple)) else result
        if isinstance(result_image, dict):
            result_image = result_image.get("path") or result_image.get("url") or result_image.get("name")
        if not result_image or not Path(str(result_image)).exists():
            raise RuntimeError("The try-on server returned no image. Check that the Colab notebook is still running.")
        suffix = Path(str(result_image)).suffix or ".png"
        out_path = UPLOAD_DIR / f"tryon_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}{suffix}"
        shutil.copy(str(result_image), out_path)
        return str(out_path)
    except Exception as e:
        message = str(e)
        if "upstream Gradio app has raised an exception" in message:
            raise RuntimeError("The try-on server hit an error or is busy. Try again in a moment.") from e
        raise RuntimeError(f"Virtual try-on failed: {message}") from e


# ============================================================
# SESSION, CALLBACKS & SHARED COMPONENTS
# ============================================================

for _k, _v in {
    "user_id": None, "username": None, "looks": [], "looks_shown": 3, "selected_look": None,
    "last_result": None, "gen_error": None, "pending_save": None, "studio_prompt": "",
    "retry_pid": None, "nav_page": "Home", "home_tick": 0,
    "tryon_result": None, "tryon_error": None,
    "auth_fails": 0, "auth_lock_until": 0,
}.items():
    st.session_state.setdefault(_k, _v)

NAV = ["Home", "My Wardrobe", "AI Stylist", "Virtual Try-On", "AI Gallery", "Saved Looks", "Profile"]

def toast(msg):
    st.session_state["_toast"] = msg

def go(page_name):
    st.session_state.nav_page = page_name
    # This callback runs before the next script pass, so widget state is safe to update.
    st.session_state.nav_page_bottom = page_name

def _sync_nav_from_widget():
    st.session_state.nav_page = st.session_state.get("nav_page_bottom", "Home")

def cb_feedback(uid, look, action, reason_key=None, msg="Noted"):
    reason = st.session_state.get(reason_key, "") if reason_key else ""
    save_feedback(uid, look, action, reason)
    toast(msg)

def cb_quick_save(uid, look):
    cid = ensure_default_collection(uid)
    save_look(uid, look, cid)
    save_feedback(uid, look, "save")
    toast(f"Saved to {DEFAULT_COLLECTION}")

def cb_select(look):
    st.session_state.selected_look = look
    st.session_state.last_result = None
    st.session_state.gen_error = None
    st.session_state.studio_prompt = ""
    st.session_state.nav_page = "AI Stylist"

def cb_retry(pending):
    st.session_state.selected_look = pending["look"]
    st.session_state.studio_prompt = pending.get("extra_prompt", "")
    st.session_state.retry_pid = pending["id"]
    st.session_state.last_result = None
    st.session_state.gen_error = None
    st.session_state.nav_page = "AI Stylist"

def cb_request_save(look, image_path):
    st.session_state.pending_save = {"look": look, "image": image_path}


def look_card(look, key, compact=False, show_select=True):
    """One look: visual tile, smart details, 'Why this look?', shop links and actions."""
    outfit = look["outfit"]
    hair = look.get("hairstyle", {})
    match = int(_clamp(round(look.get("score", 0)), 35, 98))
    with st.container(border=True):
        st.markdown(look_visual(look, height=170 if compact else 230), unsafe_allow_html=True)
        if not outfit.get("from_wardrobe"):
            _, _credits = online_images(outfit, _user_gender())
            if not _credits:
                _why = miss_reason(_online_query(outfit, _user_gender()))
                st.caption(f"No photo loaded: {_why or 'searching...'}")
            _more = f"https://www.pinterest.com/search/pins/?q={quote_plus(_online_query(outfit, _user_gender())[0])}"
            st.markdown(f'<div class="small-muted">{_esc(_credits[0]) + " · " if _credits and not compact else ""}'
                        f'<a href="{_esc(_more)}" target="_blank" rel="noopener noreferrer">More photos</a></div>',
                        unsafe_allow_html=True)
        head_tags = [f"{match}% match", formality_label(outfit.get("formality", 3))]
        if not compact:
            head_tags += list(outfit.get("seasons", []))[:3] if len(outfit.get("seasons", [])) < 4 else ["All seasons"]
        st.markdown(
            f'<div class="look-name">{_esc(outfit["name"])}</div>'
            + swatches(outfit.get("colors", []))
            + f'<div>{tags_html(head_tags[:1], "dark")}{tags_html(head_tags[1:], "brown")}</div>',
            unsafe_allow_html=True,
        )

        if compact:
            if look.get("reasons"):
                st.markdown(f'<div class="detail-note">{_esc(look["reasons"][0])}</div>', unsafe_allow_html=True)
        else:
            rows = [("Top", outfit.get("top")), ("Bottom", outfit.get("bottom")),
                    ("Shoes", outfit.get("shoes")), ("Hair", hair.get("name"))]
            if outfit.get("accessories"):
                rows.append(("Extras", ", ".join(outfit["accessories"])))
            html = "".join(f'<div class="item-row"><small>{l}</small><div>{_esc(str(v))}</div></div>' for l, v in rows if v)
            notes = []
            if outfit.get("fabric"): notes.append(f"<b>Fabric</b> · {_esc(outfit['fabric'])}")
            if outfit.get("fit"): notes.append(f"<b>Fit</b> · {_esc(outfit['fit'])}")
            if hair.get("tip"): notes.append(f"<b>Hair</b> · {_esc(hair['tip'])}")
            html += "".join(f'<div class="detail-note">{n}</div>' for n in notes)
            st.markdown(html, unsafe_allow_html=True)

            with st.expander("Why this look?"):
                lis = "".join(f"<li>{_esc(r)}</li>" for r in look.get("reasons", []))
                st.markdown(f'<ul class="why">{lis}</ul>', unsafe_allow_html=True)

            if look.get("products"):
                with st.expander("Shop this look"):
                    shop = ""
                    for p in look["products"]:
                        links = "".join(f'<a href="{_esc(u)}" target="_blank" rel="noopener noreferrer">{_esc(n)}</a>' for n, u in p["links"])
                        shop += (f'<div class="shop-item"><b>{_esc(p["slot"])}</b> · {_esc(p["item"])}'
                                 f'<div class="why-text">{_esc(p["why"])}</div>{links}</div>')
                    st.markdown(shop, unsafe_allow_html=True)
                    st.caption("Each link opens a search on that store. Price and stock are shown by the store.")

        if compact:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown('<span class="act-marker"></span>', unsafe_allow_html=True)
                if show_select:
                    st.button("Style this", key=f"{key}_sel", type="primary", on_click=cb_select, args=(look,), use_container_width=True)
            with c2:
                st.button("Save", key=f"{key}_save", on_click=cb_quick_save, args=(user_id, look), use_container_width=True)
        else:
            a, b, c = st.columns(3)
            with a:
                st.markdown('<span class="act-marker"></span>', unsafe_allow_html=True)
                st.button("Like", key=f"{key}_like", on_click=cb_feedback,
                          args=(user_id, look, "like", None, "Liked. We'll show you more like this."), use_container_width=True)
            with b:
                with _popover("Pass"):
                    st.radio("What didn't work?", DISLIKE_REASONS, key=f"{key}_why")
                    st.button("Send feedback", key=f"{key}_pass", on_click=cb_feedback,
                              args=(user_id, look, "dislike", f"{key}_why", "Thanks. We'll steer away from that."))
            with c:
                st.button("Save", key=f"{key}_save", on_click=cb_quick_save, args=(user_id, look), use_container_width=True)
            if show_select:
                st.button("Style this look", key=f"{key}_sel", type="primary", on_click=cb_select, args=(look,), use_container_width=True)


def render_save_confirm(uid, scope):
    """Generated looks are only saved after the user confirms the collection."""
    ps = st.session_state.get("pending_save")
    if not ps:
        return
    cols = get_collections(uid)
    names = [c["name"] for c in cols]
    with st.container(border=True):
        st.markdown('<div class="step-title">Save this look?</div>'
                    '<div class="step-desc">Choose where it goes. Nothing is saved until you confirm.</div>', unsafe_allow_html=True)
        c1, c2 = st.columns([1, 2], gap="large")
        with c1:
            if ps.get("image") and Path(ps["image"]).exists():
                st.image(ps["image"], use_container_width=True)
        with c2:
            st.markdown(f'**{_esc(ps["look"].get("outfit", {}).get("name", "AI look"))}**')
            sel = st.selectbox("Collection", names, key=f"{scope}_ps_col")
            new = st.text_input("Or start a new collection", key=f"{scope}_ps_new", placeholder="For example: Wedding season")
            b1, b2 = st.columns(2)
            if b1.button("Confirm and save", type="primary", key=f"{scope}_ps_ok", use_container_width=True):
                cid = create_collection(uid, new) if new.strip() else next(c["id"] for c in cols if c["name"] == sel)
                save_look(uid, ps["look"], cid, ps.get("image", ""))
                save_feedback(uid, ps["look"], "save")
                st.session_state.pending_save = None
                toast("Saved to your collection")
                st.rerun()
            if b2.button("Cancel", key=f"{scope}_ps_no", use_container_width=True):
                st.session_state.pending_save = None
                st.rerun()


# ============================================================
# LOGIN
# ============================================================

if not st.session_state.user_id:
    AUTH_MAX_TRIES, AUTH_LOCK_SECONDS = 5, 30

    def _landing_wall():
        """Masonry of looks. Uses photos already cached on disk (no network on the sign-in page),
        mixed with colour-board tiles built from the built-in outfits."""
        heights = [250, 330, 220, 300, 260, 340, 230, 290, 320, 240, 280, 310]
        photos = sorted(DEMO_CACHE_DIR.glob("web_*_*.jpg"), key=lambda p: p.stat().st_mtime, reverse=True)[:8]
        tiles, i = [], 0
        boards = [tile_html(o["colors"], o["name"], None, heights[(k * 5 + 3) % len(heights)]) for k, o in enumerate(OUTFITS)]
        photo_tiles = [tile_html([], "", [str(p)], heights[(k * 7) % len(heights)]) for k, p in enumerate(photos)]
        while len(tiles) < 16 and (photo_tiles or boards):
            if photo_tiles and i % 2 == 0 or not boards:
                tiles.append(photo_tiles.pop(0))
            elif boards:
                tiles.append(boards.pop(0))
            i += 1
            if not photo_tiles and not boards:
                break
        return "".join(tiles)

    st.markdown(f"""
    <div class="landing">
        <div class="wall">{_landing_wall()}</div>
        <div class="landing-top">{brand_html(light=True)}</div>
        <div class="landing-copy">
            <h2>Dress for the day you're about to have.</h2>
            <p>Outfits, hairstyles and complete looks chosen around your body, your taste and your occasion.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    try:
        auth_box = st.container(key="auth_float")      # needs Streamlit 1.39+; older versions show a plain card
    except TypeError:
        auth_box = st.container(border=True)

    with auth_box:
        st.markdown(brand_html(sub=False), unsafe_allow_html=True)
        st.markdown('<div class="login-title">Welcome</div><div class="login-sub">Log in or create an account to start styling.</div>', unsafe_allow_html=True)
        login_tab, register_tab = st.tabs(["Log in", "Create account"])

        with login_tab:
            remaining = int(st.session_state.auth_lock_until - time.time())
            if remaining > 0:
                st.warning(f"Too many failed attempts. Please wait {remaining} seconds and try again.")
            with st.form("login_form"):
                u = st.text_input("Username", placeholder="your username")
                p = st.text_input("Password", type="password", placeholder="your password")
                if st.form_submit_button("Log in", type="primary", use_container_width=True):
                    if remaining > 0:
                        pass
                    elif not u.strip() or not p:
                        st.error("Enter your username and password.")
                    else:
                        user = login(u, p)
                        if user:
                            st.session_state.auth_fails = 0
                            st.session_state.user_id = user["id"]
                            st.session_state.username = user["username"]
                            st.rerun()
                        else:
                            st.session_state.auth_fails += 1
                            if st.session_state.auth_fails >= AUTH_MAX_TRIES:
                                st.session_state.auth_fails = 0
                                st.session_state.auth_lock_until = time.time() + AUTH_LOCK_SECONDS
                                st.error(f"Too many failed attempts. Please wait {AUTH_LOCK_SECONDS} seconds.")
                            else:
                                st.error("That username or password is not right.")

        with register_tab:
            ru = st.text_input("Choose a username", key="reg_user", placeholder="3 to 24 letters, numbers, _ or .")
            rp = st.text_input("Choose a password", type="password", key="reg_pw", placeholder="at least 6 characters")
            rc = st.text_input("Confirm password", type="password", key="reg_pw2", placeholder="type it again")

            user_ok = bool(re.fullmatch(r"[a-z0-9_.]{3,24}", ru.strip().lower()))
            len_ok = len(rp) >= 6
            match_ok = bool(rp) and rp == rc
            variety = sum([bool(re.search(r"[a-z]", rp)) and bool(re.search(r"[A-Z]", rp)),
                           bool(re.search(r"\d", rp)), bool(re.search(r"[^A-Za-z0-9]", rp)), len(rp) >= 10])
            strength = 0 if not len_ok else (1 if variety <= 1 else (2 if variety == 2 else 3))
            label, color, width = [("Too short", "#b04a3a", 12 if rp else 0), ("Weak", "#c8863a", 40),
                                   ("Good", "#8b5e3c", 70), ("Strong", "#3f6b3a", 100)][strength]
            if rp:
                st.markdown(f'<div class="pw-meter"><i style="width:{width}%;background:{color}"></i></div>'
                            f'<div class="small-muted">Password strength: {label}</div>', unsafe_allow_html=True)

            def _chk(ok, text):
                return f'<span class="{"ok" if ok else ""}">{"✓" if ok else "○"} {text}</span>'
            st.markdown('<div class="auth-checks">' + _chk(user_ok, "Username: 3 to 24 letters, numbers, _ or .")
                        + _chk(len_ok, "Password: at least 6 characters")
                        + _chk(match_ok, "Both passwords match") + '</div>', unsafe_allow_html=True)

            if st.button("Create account", type="primary", use_container_width=True, key="reg_go",
                         disabled=not (user_ok and len_ok and match_ok)):
                ok, msg = register(ru, re, rp)
                if ok:
                    user = login(ru, rp)          # sign them straight in, onboarding starts next
                    if user:
                        st.session_state.user_id = user["id"]
                        st.session_state.username = user["username"]
                        st.rerun()
                    st.success(msg)
                else:
                    st.error(msg)
    st.stop()


# ============================================================
# APP SHELL: top bar + navigation
# ============================================================

user_id = st.session_state.user_id
username = st.session_state.username
raw_profile = get_profile(user_id)
has_profile = bool(raw_profile)      # parse_profile() always returns a dict, so test the raw row
profile = parse_profile(raw_profile)
ensure_default_collection(user_id)
prefs = learn_preferences(user_id)

def do_logout():
    for k in ("user_id", "username", "selected_look", "last_result", "gen_error", "pending_save", "home_cache", "ob_draft", "ob_step", "tryon_result", "tryon_error"):
        st.session_state[k] = None
    st.session_state.looks = []
    st.session_state.nav_page = "Home"

tb_l, tb_r = st.columns([3, 2])
with tb_l:
    st.markdown(brand_html(), unsafe_allow_html=True)
with tb_r:
    tc1, tc2 = st.columns([3, 1.4])
    tc1.markdown(f'<div class="user-chip"><div class="uname">{_esc(username or "")}</div>'
                 f'<div class="avatar">{_esc((username or "?")[:1].upper())}</div></div>', unsafe_allow_html=True)
    tc2.button("Log out", key="logout_top_2", on_click=do_logout, use_container_width=True)

if not has_profile:
    st.session_state.nav_page = "Profile"   # new users start with guided onboarding
if st.session_state.nav_page not in NAV:
    st.session_state.nav_page = "Home"
# Page actions (such as onboarding completion) may request navigation after the
# previous widget was rendered. Reconcile before creating the widget on this run.
st.session_state.setdefault("nav_page_bottom", st.session_state.nav_page)
if st.session_state.nav_page_bottom != st.session_state.nav_page:
    st.session_state.nav_page_bottom = st.session_state.nav_page

page = st.radio(
    "Navigate", NAV, key="nav_page_bottom", horizontal=True,
    label_visibility="collapsed", on_change=_sync_nav_from_widget
)

_msg = st.session_state.pop("_toast", None)
if _msg:
    st.toast(_msg)


# ============================================================
# FLUX RUNNER (failure keeps the look so the user can retry later)
# ============================================================

def run_generation(look, extra_prompt="", pending_id=None):
    st.session_state.gen_error = None
    try:
        with st.spinner("Connecting to FLUX.1 Kontext. Creating your AI styled preview..."):
            out = generate_ai_look(profile, look, user_id, extra_prompt)
    except Exception as e:
        if pending_id:
            bump_pending(pending_id, user_id, e)
        else:
            pending_id = add_pending(user_id, look, extra_prompt, e)
        st.session_state.gen_error = {"msg": str(e), "pending_id": pending_id}
        return None
    for p in get_pending(user_id):               # a success clears any retry entry for this look
        if p["look"].get("outfit", {}).get("name") == look.get("outfit", {}).get("name"):
            delete_pending(p["id"], user_id)
    save_feedback(user_id, look, "generate")
    st.session_state.last_result = {"image": out, "look": look}
    return out


def chunked(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


# ============================================================
# PAGES
# ============================================================

def greeting():
    h = datetime.now().hour
    return "Good morning" if h < 12 else "Good afternoon" if h < 18 else "Good evening"


def page_home():
    name = profile.get("name") or username
    season = current_season()
    st.markdown(f"""
    <div class="hero">
        <h1>{greeting()}, {_esc(name)}.</h1>
        <p>Here is what we would put you in today. Three looks chosen for you, plus what's trending and what suits the season.</p>
    </div>
    """, unsafe_allow_html=True)
    st.button("Style me today", type="primary", key="home_cta", on_click=go, args=("AI Stylist",))

    pending = get_pending(user_id)
    if pending:
        st.info(f"You have {len(pending)} AI preview{'s' if len(pending) > 1 else ''} waiting to be retried. Your selected look is saved.")
        st.button("Open AI Stylist to retry", key="home_retry", on_click=go, args=("AI Stylist",))

    # ---- Personalized -------------------------------------------------
    section_title("Picked for you", "Based on your profile, your wardrobe and everything you've liked or passed on.")
    st.session_state.setdefault("home_occ", recent_occasion(user_id))
    c1, c2 = st.columns([2, 1])
    occ = c1.selectbox("Dressing for", OCCASIONS, key="home_occ")
    c2.markdown("<div style='height:1.8rem'></div>", unsafe_allow_html=True)
    if c2.button("Refresh picks", key="home_refresh", use_container_width=True):
        st.session_state.home_tick += 1

    wardrobe = get_wardrobe(user_id)
    sig = hashlib.md5(json.dumps([profile, len(wardrobe), occ, st.session_state.home_tick, datetime.now().date().isoformat()],
                                 sort_keys=True, default=str).encode()).hexdigest()
    cache = st.session_state.get("home_cache")
    if not cache or cache["sig"] != sig:
        cache = {"sig": sig, "looks": recommend(profile, occ, "", "Both", wardrobe, prefs, user_id, limit=3, season=season)}
        st.session_state.home_cache = cache
    cols = st.columns(3, gap="medium")
    for i, (look, col) in enumerate(zip(cache["looks"], cols)):
        with col:
            look_card(look, f"home_p{i}")

    # ---- Trending -----------------------------------------------------
    section_title("Trending now", "What people using Stylist Buddy are liking and saving.")
    cols = st.columns(3, gap="medium")
    for i, (look, col) in enumerate(zip(trending_looks(profile, prefs), cols)):
        with col:
            look_card(look, f"home_t{i}", compact=True)

    # ---- Seasonal -----------------------------------------------------
    section_title("The seasonal edit", "Fabrics and layers that suit the weather.")
    st.session_state.setdefault("home_season", season)
    sel_season = st.radio("Season", SEASONS, key="home_season", horizontal=True, label_visibility="collapsed")
    cols = st.columns(3, gap="medium")
    for i, (look, col) in enumerate(zip(seasonal_looks(profile, prefs, sel_season), cols)):
        with col:
            look_card(look, f"home_s{i}", compact=True)

    # ---- Recent saved looks -------------------------------------------
    section_title("Recently saved", "Your latest saved looks.")
    saved = get_saved_looks(user_id, limit=4)
    if not saved:
        st.info("Nothing saved yet. Save a look you love and it will appear here.")
    else:
        cols = st.columns(4, gap="medium")
        for row, col in zip(saved, cols):
            lk = json.loads(row["look_json"])
            with col:
                st.markdown('<span class="grid-marker"></span>', unsafe_allow_html=True)
                st.markdown(look_visual(lk, row.get("image_path") or "", height=190)
                            + f'<div class="look-name" style="font-size:1.05rem">{_esc(row["name"])}</div>'
                            + f'<div class="look-meta">{_esc(row.get("collection_name") or DEFAULT_COLLECTION)}</div>',
                            unsafe_allow_html=True)
        st.button("See all saved looks", key="home_saved_all", on_click=go, args=("Saved Looks",))


def page_wardrobe():
    page_header("My Wardrobe", "Everything you own, matched into outfits on your device. No AI needed.")
    with st.expander("Add an item"):
        with st.form("ward_form", clear_on_submit=True):
            a, b, c = st.columns(3)
            w_name = a.text_input("Item name")
            w_cat = b.selectbox("Category", ["Top", "Bottom", "Shoes", "Accessory"])
            w_col = c.selectbox("Colour", COLORS)
            d1, d2 = st.columns(2)
            w_sty = d1.selectbox("Style", STYLES)
            w_occ = d2.selectbox("Best for", ["Any"] + OCCASIONS)
            w_img = st.file_uploader("Photo of the item", type=["jpg", "jpeg", "png"])
            if st.form_submit_button("Add item", type="primary"):
                if not w_name.strip():
                    st.error("Give the item a name.")
                else:
                    ipath = save_upload(w_img, f"ward_{user_id}") if w_img else ""
                    add_wardrobe(user_id, w_name.strip(), w_cat, w_col, w_sty, w_occ, ipath)
                    st.success("Item added.")
                    st.rerun()

    items = get_wardrobe(user_id)
    if not items:
        st.info("Your wardrobe is empty. Add a top, a bottom and a pair of shoes to unlock outfit matches.")
        return

    # ---- Smart matches (local) --------------------------------------
    counts = {c: sum(1 for i in items if i.get("category") == c) for c in ("Top", "Bottom", "Shoes")}
    section_title("Smart matches", "Outfits built from your own pieces, scored for colour, dressiness and occasion.")
    if all(counts.values()):
        occ = st.selectbox("Match for", OCCASIONS, key="ward_occ")
        looks = recommend(profile, occ, "", "My Wardrobe", items, prefs, user_id, limit=3)
        cols = st.columns(3, gap="medium")
        for i, (look, col) in enumerate(zip(looks, cols)):
            with col:
                look_card(look, f"ward_m{i}")
    else:
        missing = [c.lower() for c, n in counts.items() if n == 0]
        st.info("Add at least one " + " and one ".join(missing) + " to see matches.")

    # ---- Grid with filter chips -------------------------------------
    section_title("All pieces")
    cats = ["All"] + sorted({i["category"] for i in items if i.get("category")})
    cat_filter = st.radio("Category", cats, horizontal=True, key="ward_cat", label_visibility="collapsed")
    f1, f2 = st.columns(2)
    color_filter = f1.selectbox("Colour", ["All"] + sorted({i["color"] for i in items if i.get("color")}))
    search = f2.text_input("Search")
    filtered = [
        i for i in items
        if (cat_filter == "All" or i["category"] == cat_filter)
        and (color_filter == "All" or i["color"] == color_filter)
        and (not search or search.lower() in i["name"].lower())
    ]
    if not filtered:
        st.caption("No pieces match those filters.")
    for row in chunked(filtered, 4):
        cols = st.columns(4, gap="medium")
        for it, col in zip(row, cols):
            with col:
                st.markdown('<span class="grid-marker"></span>', unsafe_allow_html=True)
                path = it.get("image_path", "")
                if path and Path(path).exists():
                    st.image(path, use_container_width=True)
                else:
                    _imgs, _ = wardrobe_item_images(it, _user_gender())
                    st.markdown(tile_html([it.get("color")], it.get("category", ""), _imgs, 200), unsafe_allow_html=True)
                st.markdown(f'<div class="look-name" style="font-size:1.05rem">{_esc(it["name"])}</div>'
                            f'<div class="look-meta">{_esc(str(it.get("color", "")))} · {_esc(str(it.get("style", "")))}</div>',
                            unsafe_allow_html=True)
                if st.button("Remove", key=f"del_ward_{it['id']}", use_container_width=True):
                    delete_wardrobe_item(user_id, it["id"])
                    st.rerun()


def page_stylist():
    page_header("AI Stylist", "Tell us the occasion. Pick a look. Preview it on yourself.")

    # ---- 1. Brief -----------------------------------------------------
    with st.container(border=True):
        st.markdown('<div class="step-title">Your brief</div><div class="step-desc">Looks are curated on your device. AI is only used for the final preview.</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        occasion = c1.selectbox("Occasion", OCCASIONS, key="brief_occasion")
        source = c2.radio("Where should the pieces come from?", ["Online", "My Wardrobe", "Both"], horizontal=True, key="brief_source")
        situation = st.text_area("Anything else about the day? (optional)", key="brief_situation",
                                 placeholder="For example: outdoor conference presentation, warm weather")
        if st.button("Curate my looks", type="primary", use_container_width=True):
            wardrobe = get_wardrobe(user_id)
            need_ward = source in ("My Wardrobe", "Both")
            has_all = all(any(i.get("category") == c for i in wardrobe) for c in ("Top", "Bottom", "Shoes"))
            if source == "My Wardrobe" and not has_all:
                st.warning("Add at least one top, one bottom and one pair of shoes to My Wardrobe first.")
            else:
                if need_ward and not has_all:
                    st.caption("Your wardrobe doesn't have a full outfit yet, so these come from online picks.")
                looks = recommend(profile, occasion, situation, source, wardrobe, prefs, user_id, limit=9, season=current_season())
                st.session_state.looks = looks
                st.session_state.looks_shown = 3
                for lk in looks[:3]:
                    save_history(user_id, lk)

    # ---- 2. Looks (3 first, more on request) --------------------------
    looks = st.session_state.looks
    if looks:
        section_title("Your looks", "Pick the one you want to see on yourself.")
        shown = looks[:st.session_state.looks_shown]
        for r, row in enumerate(chunked(shown, 3)):
            cols = st.columns(3, gap="medium")
            for j, (look, col) in enumerate(zip(row, cols)):
                with col:
                    look_card(look, f"st{r * 3 + j}")
        if len(looks) > st.session_state.looks_shown:
            if st.button("Show more looks", key="more_looks"):
                st.session_state.looks_shown += 3
                st.rerun()

    # ---- 3. Studio: selected look -> optional prompt -> FLUX ----------
    sel = st.session_state.selected_look
    if sel:
        section_title("Preview on you", "FLUX edits your profile photo into this look.")
        has_photo = bool(profile.get("profile_photo")) and Path(profile["profile_photo"]).exists()
        with st.container(border=True):
            l, r = st.columns([1, 2], gap="large")
            with l:
                st.markdown(look_visual(sel, height=200)
                            + f'<div class="look-name">{_esc(sel["outfit"]["name"])}</div>'
                            + f'<div class="look-meta">{_esc(sel.get("occasion", ""))}</div>', unsafe_allow_html=True)
            with r:
                st.text_area("Add a note for the stylist (optional)", key="studio_prompt", height=110,
                             placeholder="For example: sleeves rolled up, slightly darker shirt", max_chars=300)
                if not has_photo:
                    st.warning("Upload a full-body photo in your profile to generate a preview.")
                    st.button("Add a photo in Profile", key="studio_photo", on_click=go, args=("Profile",))
                b1, b2 = st.columns([3, 1])
                gen_btn = b1.button("Generate AI styled preview", type="primary", key="gen_btn",
                                    use_container_width=True, disabled=not has_photo)
                b2.button("Clear", key="studio_clear", use_container_width=True,
                          on_click=lambda: st.session_state.update(selected_look=None, last_result=None, gen_error=None))

        retry_pid = st.session_state.get("retry_pid")
        if has_photo and (gen_btn or retry_pid):
            st.session_state.retry_pid = None
            run_generation(sel, st.session_state.get("studio_prompt", ""), retry_pid)

        sc1, sc2 = st.columns(2, gap="large")
        with sc1:
            st.markdown('<div class="ba-label">Before: your photo</div>', unsafe_allow_html=True)
            if has_photo:
                st.image(profile["profile_photo"], use_container_width=True)
            else:
                st.markdown('<div class="ba-placeholder">Your profile photo will appear here.</div>', unsafe_allow_html=True)
        with sc2:
            st.markdown('<div class="ba-label">After: AI styled preview</div>', unsafe_allow_html=True)
            res, err = st.session_state.last_result, st.session_state.gen_error
            if res and Path(res["image"]).exists():
                st.image(res["image"], use_container_width=True)
                st.button("Save to a collection", key="res_save", on_click=cb_request_save, args=(res["look"], res["image"]))
            elif err:
                st.error(f"The preview didn't finish. {err['msg']}")
                st.caption("Your look is saved. Retry now, or come back later and retry from the list below.")
                st.button("Retry now", key="retry_now", on_click=cb_retry, args=(
                    next((p for p in get_pending(user_id) if p["id"] == err["pending_id"]),
                         {"id": err["pending_id"], "look": sel, "extra_prompt": st.session_state.get("studio_prompt", "")}),))
            else:
                st.markdown('<div class="ba-placeholder">Generate a preview to see yourself in this look.</div>', unsafe_allow_html=True)
        render_save_confirm(user_id, "stylist")

    # ---- 4. Saved for retry -------------------------------------------
    pending = get_pending(user_id)
    if pending:
        section_title("Saved for retry", "Previews that didn't finish. The public FLUX server can be busy, so try again in a few minutes.")
        for p in pending:
            with st.container(border=True):
                c1, c2, c3 = st.columns([4, 1, 1])
                c1.markdown(f'**{_esc(p["look"].get("outfit", {}).get("name", "Look"))}** · {_esc(p["look"].get("occasion", ""))}')
                c1.caption(f"Attempts: {p['attempts']} · Last try {p['created_at'][:16].replace('T', ' ')}"
                           + (f" · Note: {p['extra_prompt']}" if p.get("extra_prompt") else ""))
                c2.button("Retry", key=f"pend_retry_{p['id']}", on_click=cb_retry, args=(p,), use_container_width=True)
                if c3.button("Discard", key=f"pend_del_{p['id']}", use_container_width=True):
                    delete_pending(p["id"], user_id)
                    st.rerun()


def page_tryon():
    page_header("Virtual Try-On", "Take a photo, pick a garment, see it on you.")
    ep = tryon_endpoint()
    using_colab = ep.startswith("http")
    st.caption(("Connected to your Colab GPU." if using_colab else
                "No Colab URL set, so the shared public try-on server is used. It can be slow or busy.")
               + " Each try-on takes about 20 to 60 seconds.")

    person_path = None
    garment_path = None
    garment_desc = ""
    garment_name = "Virtual try-on"

    c1, c2 = st.columns(2, gap="large")

    # ---- You ----------------------------------------------------------
    with c1:
        with st.container(border=True):
            st.markdown('<div class="step-title">1. You</div><div class="step-desc">Stand straight, good light, plain background, upper body clearly visible.</div>', unsafe_allow_html=True)
            has_profile_photo = bool(profile.get("profile_photo")) and Path(profile["profile_photo"]).exists()
            options = (["My profile photo"] if has_profile_photo else []) + ["Take a photo", "Upload a photo"]
            src_choice = st.radio("Photo of you", options, horizontal=True, key="tryon_person_src", label_visibility="collapsed")
            if src_choice == "My profile photo":
                person_path = profile["profile_photo"]
                st.image(person_path, use_container_width=True)
            elif src_choice == "Take a photo":
                shot = st.camera_input("Camera", key="tryon_cam", label_visibility="collapsed")
                if shot:
                    person_path = str(UPLOAD_DIR / f"tryon_person_{user_id}.jpg")
                    Path(person_path).write_bytes(shot.getbuffer())
            else:
                up = st.file_uploader("Upload your photo", type=["jpg", "jpeg", "png", "webp"], key="tryon_person_up")
                if up:
                    person_path = save_upload(up, f"tryon_person_{user_id}")
                    st.image(person_path, use_container_width=True)

    # ---- Garment ------------------------------------------------------
    with c2:
        with st.container(border=True):
            st.markdown('<div class="step-title">2. The garment</div><div class="step-desc">Works best with tops, shirts, jackets and dresses on a plain background.</div>', unsafe_allow_html=True)
            wardrobe_items = [w for w in get_wardrobe(user_id)
                              if w.get("image_path") and Path(w["image_path"]).exists()]
            g_opts = (["From My Wardrobe"] if wardrobe_items else []) + ["Upload a garment photo"]
            g_choice = st.radio("Garment source", g_opts, horizontal=True, key="tryon_garm_src", label_visibility="collapsed")
            if g_choice == "From My Wardrobe":
                labels = {w["id"]: f"{w['name']} ({w['category']})" for w in wardrobe_items}
                wid = st.selectbox("Wardrobe item", list(labels), format_func=lambda i: labels[i], key="tryon_ward_pick")
                item = next(w for w in wardrobe_items if w["id"] == wid)
                garment_path = item["image_path"]
                garment_name = item["name"]
                garment_desc = f"{item.get('color', '')} {item['name']}".strip()
                st.image(garment_path, use_container_width=True)
            else:
                gup = st.file_uploader("Upload a garment photo", type=["jpg", "jpeg", "png", "webp"], key="tryon_garm_up")
                garment_desc = st.text_input("Short description (optional)", key="tryon_garm_desc",
                                             placeholder="For example: navy blue linen shirt", max_chars=100)
                if gup:
                    garment_path = save_upload(gup, f"tryon_garment_{user_id}")
                    garment_name = garment_desc or "Uploaded garment"
                    st.image(garment_path, use_container_width=True)

    ready = bool(person_path and garment_path)
    if st.button("Try it on", type="primary", use_container_width=True, key="tryon_go", disabled=not ready):
        st.session_state.tryon_error = None
        try:
            with st.spinner("Dressing you up. This takes about a minute..."):
                out = generate_tryon(person_path, garment_path, garment_desc, user_id, garment_name)
            look = {"outfit": {"name": garment_name, "top": garment_desc, "colors": [], "styles": [], "accessories": []},
                    "hairstyle": {"name": ""}, "occasion": "Virtual try-on", "source": "Try-On"}
            save_generated_image(user_id, look, out)
            st.session_state.tryon_result = {"image": out, "look": look, "before": person_path}
        except Exception as e:
            st.session_state.tryon_result = None
            st.session_state.tryon_error = str(e)

    res, err = st.session_state.tryon_result, st.session_state.tryon_error
    if err:
        st.error(err)
        st.caption("If you use Colab, make sure the notebook is still running and TRYON_URL matches the latest link it printed.")
    if res and Path(res["image"]).exists():
        section_title("Your try-on", "Also added to your AI Gallery.")
        b, a = st.columns(2, gap="large")
        with b:
            st.markdown('<div class="ba-label">Before</div>', unsafe_allow_html=True)
            if res.get("before") and Path(res["before"]).exists():
                st.image(res["before"], use_container_width=True)
        with a:
            st.markdown('<div class="ba-label">After</div>', unsafe_allow_html=True)
            st.image(res["image"], use_container_width=True)
            st.button("Save to a collection", key="tryon_save", on_click=cb_request_save, args=(res["look"], res["image"]))
    render_save_confirm(user_id, "tryon")


def page_gallery():
    page_header("AI Gallery", "Your latest 20 AI styled previews.")
    render_save_confirm(user_id, "gallery")
    occ = st.radio("Occasion", ["All"] + OCCASIONS, horizontal=True, key="gal_occ", label_visibility="collapsed")
    rows = get_generated_images(user_id, occ, 20)
    if not rows:
        st.info("No previews here yet. Pick a look in AI Stylist and generate one." if occ == "All"
                else f"No {occ.lower()} previews yet.")
        return
    st.caption(f"Showing {len(rows)} most recent" + ("" if occ == "All" else f" for {occ.lower()}"))
    for row_chunk in chunked(rows, 3):
        cols = st.columns(3, gap="medium")
        for row, col in zip(row_chunk, cols):
            with col:
                st.markdown('<span class="grid-marker"></span>', unsafe_allow_html=True)
                if Path(row["image_path"]).exists():
                    st.image(row["image_path"], use_container_width=True)
                    st.markdown(f'<div class="look-name" style="font-size:1.05rem">{_esc(row["look"].get("outfit", {}).get("name", "AI look"))}</div>'
                                f'<div class="look-meta">{_esc(row["look"].get("occasion", ""))} · {row["created_at"][:10]}</div>', unsafe_allow_html=True)
                    a, b = st.columns(2)
                    with a:
                        st.markdown('<span class="act-marker"></span>', unsafe_allow_html=True)
                        with open(row["image_path"], "rb") as f:
                            st.download_button("Download", f, file_name=Path(row["image_path"]).name, mime="image/png",
                                               key=f"gallery_download_{row['id']}", use_container_width=True)
                    with b:
                        st.button("Save", key=f"gal_save_{row['id']}", on_click=cb_request_save,
                                  args=(row["look"], row["image_path"]), use_container_width=True)
                else:
                    st.caption("Image file is missing from disk.")


def page_saved():
    page_header("Saved Looks", "Keep looks in collections for weddings, work weeks, trips.")
    collections = get_collections(user_id)
    by_name = {c["name"]: c for c in collections}
    with st.expander("New collection"):
        n1, n2 = st.columns([3, 1])
        new_name = n1.text_input("Collection name", key="new_coll_name", label_visibility="collapsed", placeholder="For example: Wedding season")
        if n2.button("Create", key="new_coll_btn", use_container_width=True):
            if new_name.strip():
                create_collection(user_id, new_name)
                st.rerun()
            else:
                st.warning("Give the collection a name.")

    labels = ["All"] + [c["name"] for c in collections]
    choice = st.radio("Collection", labels, horizontal=True, key="saved_coll", label_visibility="collapsed")
    current = None if choice == "All" else by_name.get(choice)
    if current:
        st.caption(f"{current['n']} look{'s' if current['n'] != 1 else ''} in {current['name']}")
    if current and current["name"] != DEFAULT_COLLECTION:
        with _popover("Collection options"):
            st.caption("Deleting a collection moves its looks to Favorites. Looks are never deleted this way.")
            if st.button(f"Delete {current['name']}", key="del_coll"):
                delete_collection(user_id, current["id"])
                st.session_state.saved_coll = "All"
                st.rerun()

    saved = get_saved_looks(user_id, current["id"] if current else None)
    if not saved:
        st.info("Nothing here yet. Save a look from Home or AI Stylist and it will land in a collection.")
        return
    move_options = [c["name"] for c in collections]
    for row_chunk in chunked(saved, 3):
        cols = st.columns(3, gap="medium")
        for row, col in zip(row_chunk, cols):
            lk = json.loads(row["look_json"])
            with col:
                st.markdown('<span class="grid-marker"></span>', unsafe_allow_html=True)
                with st.container(border=True):
                    st.markdown(look_visual(lk, row.get("image_path") or "", height=230)
                                + f'<div class="look-name">{_esc(row["name"])}</div>'
                                + f'<div>{tags_html([row.get("collection_name") or DEFAULT_COLLECTION], "brown")}{tags_html([row.get("occasion"), row["created_at"][:10]])}</div>',
                                unsafe_allow_html=True)
                    o = lk.get("outfit", {})
                    st.markdown(f'<div class="detail-note">{_esc(o.get("top", ""))} · {_esc(o.get("bottom", ""))} · {_esc(o.get("shoes", ""))}</div>',
                                unsafe_allow_html=True)
                    st.button("Style this look", key=f"sv_style_{row['id']}", type="primary", on_click=cb_select, args=(lk,), use_container_width=True)
                    a, b = st.columns(2)
                    with a:
                        st.markdown('<span class="act-marker"></span>', unsafe_allow_html=True)
                        with _popover("Move"):
                            dest = st.selectbox("Move to", move_options, key=f"sv_dest_{row['id']}",
                                                index=move_options.index(row["collection_name"]) if row.get("collection_name") in move_options else 0)
                            if st.button("Move look", key=f"sv_move_{row['id']}"):
                                move_saved_look(user_id, row["id"], by_name[dest]["id"])
                                st.rerun()
                    with b:
                        if st.button("Delete", key=f"delete_saved_{row['id']}", use_container_width=True):
                            delete_saved_look(user_id, row["id"])
                            st.rerun()


# ---------------------------- Profile ------------------------------

GENDERS = ["Male", "Female", "Other"]

def profile_defaults(p):
    return {
        "name": p.get("name", "") or "", "age": p.get("age") or 22, "gender": p.get("gender") or "Male",
        "height": p.get("height") or 170.0, "chest": p.get("chest") or 95.0, "waist": p.get("waist") or 80.0,
        "hips": p.get("hips") or 98.0, "preferred_colors": p.get("preferred_colors", []),
        "clothing_style": p.get("clothing_style", []), "hair_length": p.get("hair_length") or "Short",
        "hair_type": p.get("hair_type") or "Straight", "current_hairstyle": p.get("current_hairstyle", "") or "",
        "hair_preferences": p.get("hair_preferences", "") or "", "fashion_interests": p.get("fashion_interests", "") or "",
        "profile_photo": p.get("profile_photo", "") or "",
    }

def step_details(d, kp):
    a, b, c, e = st.columns(4)
    d["name"] = a.text_input("Name", d["name"], key=f"{kp}name")
    d["age"] = b.number_input("Age", 13, 100, int(d["age"]), key=f"{kp}age")
    d["gender"] = c.selectbox("Gender", GENDERS, index=GENDERS.index(d["gender"]) if d["gender"] in GENDERS else 0, key=f"{kp}gender")
    d["height"] = e.number_input("Height (cm)", 100.0, 230.0, float(d["height"]), key=f"{kp}height")
    f, g, h = st.columns(3)
    d["chest"] = f.number_input("Chest (cm)", 0.0, 200.0, float(d["chest"]), key=f"{kp}chest")
    d["waist"] = g.number_input("Waist (cm)", 0.0, 200.0, float(d["waist"]), key=f"{kp}waist")
    d["hips"] = h.number_input("Hips (cm)", 0.0, 200.0, float(d["hips"]), key=f"{kp}hips")

def step_photo(d, kp):
    up = st.file_uploader("Upload a full-body photo", type=["jpg", "jpeg", "png"], key=f"{kp}photo")
    if up:
        st.image(up, width=200)
    elif d.get("profile_photo") and Path(d["profile_photo"]).exists():
        st.image(d["profile_photo"], width=200)
    st.caption("Stand straight, good light, plain background. This is the photo FLUX restyles, so your face and body should be clearly visible.")
    return up

def step_prefs(d, kp):
    d["preferred_colors"] = st.multiselect("Colours you love", COLORS, default=d["preferred_colors"], key=f"{kp}colors")
    d["clothing_style"] = st.multiselect("Your style", STYLES, default=d["clothing_style"], key=f"{kp}styles")
    d["fashion_interests"] = st.text_area("Fashion interests (optional)", d["fashion_interests"], key=f"{kp}interests")

def step_hair(d, kp):
    h1, h2 = st.columns(2)
    d["hair_length"] = h1.selectbox("Hair length", HAIR_LENGTHS, index=HAIR_LENGTHS.index(d["hair_length"]) if d["hair_length"] in HAIR_LENGTHS else 0, key=f"{kp}hlen")
    d["hair_type"] = h2.selectbox("Hair type", HAIR_TYPES, index=HAIR_TYPES.index(d["hair_type"]) if d["hair_type"] in HAIR_TYPES else 0, key=f"{kp}htype")
    d["current_hairstyle"] = st.text_input("Current hairstyle", d["current_hairstyle"], key=f"{kp}hstyle")
    d["hair_preferences"] = st.text_area("Hair preferences (optional)", d["hair_preferences"], key=f"{kp}hprefs")


def onboarding():
    steps = [
        ("Profile", "About you", "Used for sizing and for how we address you."),
        ("Photo", "Your photo", "The reference photo for your AI styled preview. You can skip this and add it later."),
        ("Preferences", "Your taste", "The colours and styles we should lean towards."),
        ("Hair", "Your hair", "So hairstyle suggestions actually suit your hair."),
    ]
    if not st.session_state.get("ob_draft"):
        st.session_state.ob_draft = profile_defaults(profile)
        st.session_state.ob_draft["name"] = username or ""
    d = st.session_state.ob_draft
    step = st.session_state.get("ob_step") or 0
    page_header("Let's set up your style profile", "Four short steps, about two minutes.")
    st.markdown('<div class="stepper">' + "".join(
        f'<span class="s {"on" if i == step else "done" if i < step else ""}">{n[0]}</span>' for i, n in enumerate(steps)) + '</div>',
        unsafe_allow_html=True)
    st.progress((step + 1) / len(steps))

    with st.container(border=True):
        st.markdown(f'<div class="step-title">{steps[step][1]}</div><div class="step-desc">{steps[step][2]}</div>', unsafe_allow_html=True)
        up = None
        if step == 0: step_details(d, "ob_")
        elif step == 1: up = step_photo(d, "ob_")
        elif step == 2: step_prefs(d, "ob_")
        else: step_hair(d, "ob_")

        b1, b2, _ = st.columns([1, 1.4, 3])
        if step > 0 and b1.button("Back", key="ob_back", use_container_width=True):
            st.session_state.ob_step = step - 1
            st.rerun()
        last = step == len(steps) - 1
        if b2.button("Finish setup" if last else "Continue", type="primary", key="ob_next", use_container_width=True):
            if step == 0 and not d["name"].strip():
                st.error("Please enter your name.")
            else:
                if step == 1 and up:
                    d["profile_photo"] = save_upload(up, f"user_photo_{user_id}")
                if last:
                    save_profile(user_id, d)
                    st.session_state.ob_draft = None
                    st.session_state.ob_step = 0
                    st.session_state.nav_page = "Home"
                    toast("Profile saved. Here are your first looks.")
                else:
                    st.session_state.ob_step = step + 1
                st.rerun()


def taste_panel():
    st.markdown('<div class="step-title">What we have learned about your taste</div>'
                '<div class="step-desc">Built on this device from your likes, passes, saves and previews. Recent actions count more.</div>', unsafe_allow_html=True)
    if not prefs["n"]:
        st.info("Nothing yet. Like or pass on a few looks and this fills in.")
        return
    st.caption(f"Based on {prefs['n']} actions: {prefs['likes']} positive, {prefs['passes']} passes.")
    for title, dim in (("Colours", "color"), ("Styles", "style"), ("Hairstyles", "hair")):
        items = sorted(prefs[dim].items(), key=lambda kv: -kv[1])
        items = [kv for kv in items if abs(kv[1]) >= 0.5][:5]
        if not items:
            continue
        top = max(abs(v) for _, v in items) or 1
        st.markdown(f"**{title}**")
        html = "".join(
            f'<div class="bar-row"><span class="lbl">{_esc(k)}</span><span class="bar"><i style="width:{int(abs(v) / top * 100)}%;'
            f'{"" if v >= 0 else "background:#b8a089;"}"></i></span><span class="small-muted">{"likes" if v >= 0 else "avoids"}</span></div>'
            for k, v in items)
        st.markdown(html, unsafe_allow_html=True)
    with st.expander("Reset what the stylist has learned"):
        st.caption("Clears your likes, passes and save history used for recommendations. Your saved looks stay.")
        if st.checkbox("I understand", key="reset_ok") and st.button("Reset my taste profile", key="reset_btn"):
            reset_feedback(user_id)
            toast("Taste profile reset")
            st.rerun()


def account_panel():
    st.markdown('<div class="step-title">Password</div>', unsafe_allow_html=True)
    with st.form("pwd_form"):
        old_p = st.text_input("Current password", type="password")
        new_p = st.text_input("New password", type="password")
        confirm_p = st.text_input("Confirm new password", type="password")
        if st.form_submit_button("Update password", type="primary"):
            if new_p != confirm_p:
                st.error("New passwords do not match.")
            elif len(new_p) < 6:
                st.error("New password must be at least 6 characters.")
            else:
                conn = get_conn()
                row = conn.execute("SELECT password_hash FROM users WHERE id=?", (user_id,)).fetchone()
                if row and verify_password(old_p, row["password_hash"]):
                    conn.execute("UPDATE users SET password_hash=? WHERE id=?", (hash_password(new_p), user_id))
                    conn.commit()
                    st.success("Password updated.")
                else:
                    st.error("Current password is incorrect.")
                conn.close()


def page_profile():
    if not has_profile:
        onboarding()
        return
    page_header("Profile", "Your details, photo and preferences. Changes apply to your next recommendations.")
    d = profile_defaults(profile)
    tabs = st.tabs(["Details", "Photo", "Preferences", "Hair", "Taste profile", "Account"])
    clicked, up = False, None
    with tabs[0]:
        step_details(d, "ed_")
        clicked |= st.button("Save changes", type="primary", key="ed_save_0")
    with tabs[1]:
        up = step_photo(d, "ed_")
        clicked |= st.button("Save changes", type="primary", key="ed_save_1")
    with tabs[2]:
        step_prefs(d, "ed_")
        clicked |= st.button("Save changes", type="primary", key="ed_save_2")
    with tabs[3]:
        step_hair(d, "ed_")
        clicked |= st.button("Save changes", type="primary", key="ed_save_3")
    with tabs[4]:
        taste_panel()
    with tabs[5]:
        account_panel()
    if clicked:
        if not d["name"].strip():
            st.error("Name can't be empty.")
        else:
            if up:
                d["profile_photo"] = save_upload(up, f"user_photo_{user_id}")
            save_profile(user_id, d)
            toast("Profile saved")
            st.rerun()


# ============================================================
# ROUTER
# ============================================================

{
    "Home": page_home,
    "My Wardrobe": page_wardrobe,
    "AI Stylist": page_stylist,
    "Virtual Try-On": page_tryon,
    "AI Gallery": page_gallery,
    "Saved Looks": page_saved,
    "Profile": page_profile,
}[page]()

st.markdown('<div class="footer">Stylist Buddy · Looks are curated on your device. Your photos go to AI servers only when you ask for a preview or a try-on.</div>', unsafe_allow_html=True)