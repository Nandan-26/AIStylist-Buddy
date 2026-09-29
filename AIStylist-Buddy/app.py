import streamlit as st
import sqlite3
import hashlib
import json
import random
from pathlib import Path
from datetime import datetime

# ============================================================
# AIStylist Buddy - Standalone Streamlit Prototype
# ============================================================

APP_DIR = Path(__file__).parent
DB_PATH = APP_DIR / "aistylist.db"
UPLOAD_DIR = APP_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

st.set_page_config(
    page_title="AIStylist Buddy",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------- Theme -------------------------

st.markdown("""
<style>
.stApp { background: #0f1117; }
.block-container { max-width: 1250px; padding-top: 2rem; }
.hero {
    padding: 2.5rem;
    border-radius: 24px;
    background: linear-gradient(135deg,#191c27,#25202b);
    border: 1px solid #383344;
    margin-bottom: 1.5rem;
}
.hero h1 { margin: 0; font-size: 3rem; }
.hero p { color: #b9b5c5; font-size: 1.05rem; }
.card {
    padding: 1.2rem;
    border-radius: 18px;
    background: #181b24;
    border: 1px solid #303442;
    margin-bottom: 1rem;
}
.small-muted { color: #aaa7b3; font-size: .9rem; }
.badge {
    display:inline-block;
    padding:.3rem .65rem;
    border-radius:999px;
    background:#2a2635;
    color:#e8c7a8;
    margin:.15rem;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# DATABASE
# ============================================================

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
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
    """)

    # Small demo catalog. It is deliberately rule-based for the prototype.
    cur.execute("SELECT COUNT(*) FROM wardrobe")
    conn.commit()
    conn.close()


init_db()


# ============================================================
# AUTH
# ============================================================

def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def register(username, password):
    username = username.strip().lower()
    if not username or not password:
        return False, "Username and password are required."
    try:
        conn = get_conn()
        conn.execute(
            "INSERT INTO users(username,password_hash,created_at) VALUES(?,?,?)",
            (username, hash_password(password), datetime.now().isoformat()),
        )
        conn.commit()
        conn.close()
        return True, "Account created."
    except sqlite3.IntegrityError:
        return False, "Username already exists."


def login(username, password):
    conn = get_conn()
    row = conn.execute(
        "SELECT id, username FROM users WHERE username=? AND password_hash=?",
        (username.strip().lower(), hash_password(password)),
    ).fetchone()
    conn.close()
    return row


# ============================================================
# PROFILE
# ============================================================

def get_profile(user_id):
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM profiles WHERE user_id=?", (user_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else {}


def save_profile(user_id, data):
    conn = get_conn()
    exists = conn.execute(
        "SELECT user_id FROM profiles WHERE user_id=?", (user_id,)
    ).fetchone()

    values = (
        data["name"], data["age"], data["gender"], data["height"],
        data["chest"], data["waist"], data["hips"],
        json.dumps(data["preferred_colors"]),
        json.dumps(data["clothing_style"]),
        data["hair_length"], data["hair_type"],
        data["current_hairstyle"], data["hair_preferences"],
        data["fashion_interests"], data.get("profile_photo", "")
    )

    if exists:
        conn.execute("""
            UPDATE profiles SET
            name=?, age=?, gender=?, height=?, chest=?, waist=?, hips=?,
            preferred_colors=?, clothing_style=?, hair_length=?,
            hair_type=?, current_hairstyle=?, hair_preferences=?,
            fashion_interests=?, profile_photo=?
            WHERE user_id=?
        """, values + (user_id,))
    else:
        conn.execute("""
            INSERT INTO profiles(
                name,age,gender,height,chest,waist,hips,
                preferred_colors,clothing_style,hair_length,hair_type,
                current_hairstyle,hair_preferences,fashion_interests,
                profile_photo,user_id
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, values + (user_id,))

    conn.commit()
    conn.close()


def parse_profile(profile):
    p = dict(profile)
    for key in ("preferred_colors", "clothing_style"):
        try:
            p[key] = json.loads(p.get(key) or "[]")
        except Exception:
            p[key] = []
    return p


# ============================================================
# CATALOG
# ============================================================

OCCASIONS = [
    "Interview", "College", "Office", "Wedding",
    "Party", "Date", "Casual outing", "Festival"
]

STYLES = [
    "Casual", "Formal", "Smart Casual", "Streetwear",
    "Minimal", "Traditional", "Trendy"
]

COLORS = [
    "Black", "White", "Blue", "Navy", "Grey",
    "Beige", "Brown", "Green", "Maroon", "Pink"
]

HAIR_LENGTHS = ["Short", "Medium", "Long"]
HAIR_TYPES = ["Straight", "Wavy", "Curly", "Coily"]
HAIR_STYLES = [
    "Textured crop", "Classic side part", "Low fade",
    "Messy quiff", "Medium layered", "Curtain style",
    "Shoulder-length layers", "Slick back"
]

OUTFITS = [
    {"name":"Classic Interview Look","top":"White formal shirt","bottom":"Navy tailored trousers","shoes":"Black formal shoes","accessories":["Minimal watch"],"colors":["White","Navy"],"styles":["Formal","Minimal"],"occasions":["Interview","Office"]},
    {"name":"Smart College Look","top":"Light blue Oxford shirt","bottom":"Dark straight-fit jeans","shoes":"Clean white sneakers","accessories":["Watch"],"colors":["Blue","White"],"styles":["Smart Casual","Casual"],"occasions":["College","Casual outing"]},
    {"name":"Minimal Office Look","top":"Beige knit polo","bottom":"Charcoal trousers","shoes":"Brown loafers","accessories":["Leather belt","Watch"],"colors":["Beige","Grey","Brown"],"styles":["Smart Casual","Minimal"],"occasions":["Office","Date"]},
    {"name":"Modern Party Look","top":"Black fitted shirt","bottom":"Black tailored trousers","shoes":"Black loafers","accessories":["Metal watch"],"colors":["Black"],"styles":["Trendy","Formal","Minimal"],"occasions":["Party","Date"]},
    {"name":"Wedding Fusion Look","top":"Ivory kurta","bottom":"Beige trousers","shoes":"Brown ethnic loafers","accessories":["Watch"],"colors":["White","Beige","Brown"],"styles":["Traditional","Trendy"],"occasions":["Wedding","Festival"]},
    {"name":"Festival Traditional Look","top":"Maroon kurta","bottom":"Cream trousers","shoes":"Brown ethnic shoes","accessories":["Simple bracelet"],"colors":["Maroon","Beige","Brown"],"styles":["Traditional"],"occasions":["Festival","Wedding"]},
    {"name":"Casual Weekend Look","top":"Plain black T-shirt","bottom":"Blue jeans","shoes":"White sneakers","accessories":["Cap"],"colors":["Black","Blue","White"],"styles":["Casual","Streetwear"],"occasions":["Casual outing","College"]},
    {"name":"Date Night Look","top":"Dark green overshirt","bottom":"Black jeans","shoes":"White sneakers","accessories":["Watch"],"colors":["Green","Black","White"],"styles":["Smart Casual","Trendy"],"occasions":["Date","Party"]},
]


def hair_matches(profile, style):
    length = profile.get("hair_length", "Short")
    hair_type = profile.get("hair_type", "Straight")

    # Hard constraint: do not recommend a style requiring more length.
    requirements = {
        "Textured crop": ["Short", "Medium"],
        "Classic side part": ["Short", "Medium"],
        "Low fade": ["Short", "Medium"],
        "Messy quiff": ["Short", "Medium"],
        "Medium layered": ["Medium", "Long"],
        "Curtain style": ["Medium", "Long"],
        "Shoulder-length layers": ["Long"],
        "Slick back": ["Short", "Medium", "Long"],
    }

    return length in requirements.get(style["name"], [length])


HAIRSTYLES = [
    {"name":"Textured crop","lengths":["Short","Medium"],"types":["Straight","Wavy","Curly"],"occasions":["Interview","College","Office","Casual outing","Party"],"tip":"Low-maintenance and easy to style."},
    {"name":"Classic side part","lengths":["Short","Medium"],"types":["Straight","Wavy"],"occasions":["Interview","Office","Wedding"],"tip":"Clean and polished."},
    {"name":"Low fade","lengths":["Short","Medium"],"types":["Straight","Wavy","Curly"],"occasions":["College","Party","Casual outing"],"tip":"Sharp sides with a modern finish."},
    {"name":"Messy quiff","lengths":["Short","Medium"],"types":["Straight","Wavy"],"occasions":["Date","Party","College"],"tip":"Adds texture and volume."},
    {"name":"Medium layered","lengths":["Medium","Long"],"types":["Straight","Wavy","Curly"],"occasions":["Date","Casual outing","Festival"],"tip":"Natural movement with layered volume."},
    {"name":"Curtain style","lengths":["Medium","Long"],"types":["Straight","Wavy"],"occasions":["Date","Party","Casual outing"],"tip":"Soft and contemporary."},
    {"name":"Shoulder-length layers","lengths":["Long"],"types":["Straight","Wavy","Curly"],"occasions":["Festival","Casual outing","Date"],"tip":"Works with naturally longer hair."},
    {"name":"Slick back","lengths":["Short","Medium","Long"],"types":["Straight","Wavy"],"occasions":["Wedding","Party","Office"],"tip":"A refined formal finish."},
]


# ============================================================
# RECOMMENDATION ENGINE
# ============================================================

def situation_keywords(text):
    text = (text or "").lower()
    tags = set()
    mapping = {
        "professional": ["professional", "office", "meeting", "presentation", "interview"],
        "comfortable": ["comfortable", "comfort"],
        "traditional": ["traditional", "ethnic", "festival", "wedding"],
        "confident": ["confident", "confidence"],
        "casual": ["casual", "relaxed", "outing"],
        "party": ["party", "celebration", "club"],
    }
    for tag, words in mapping.items():
        if any(w in text for w in words):
            tags.add(tag)
    return tags


def score_outfit(outfit, profile, occasion, situation):
    score = 0
    reasons = []

    if occasion in outfit["occasions"]:
        score += 50
        reasons.append(f"Suitable for {occasion}.")

    profile_styles = profile.get("clothing_style", [])
    overlap = set(profile_styles) & set(outfit["styles"])
    if overlap:
        score += 20 * len(overlap)
        reasons.append(f"Matches your {', '.join(overlap)} style preference.")

    preferred_colors = profile.get("preferred_colors", [])
    color_overlap = set(preferred_colors) & set(outfit["colors"])
    if color_overlap:
        score += 10 * len(color_overlap)
        reasons.append(f"Uses preferred colour(s): {', '.join(color_overlap)}.")

    tags = situation_keywords(situation)
    if "professional" in tags and any(x in outfit["styles"] for x in ["Formal","Smart Casual","Minimal"]):
        score += 12
        reasons.append("Fits the professional part of your situation.")
    if "traditional" in tags and "Traditional" in outfit["styles"]:
        score += 15
        reasons.append("Matches your traditional requirement.")
    if "casual" in tags and "Casual" in outfit["styles"]:
        score += 12
        reasons.append("Keeps the look casual and practical.")

    # Basic measurement-aware fit hints.
    waist = profile.get("waist") or 0
    height = profile.get("height") or 0
    if waist:
        if waist >= 90 and "tailored" in outfit["bottom"].lower():
            reasons.append("Structured tailoring can create a cleaner silhouette.")
        elif waist < 80:
            reasons.append("A clean fitted silhouette can complement your proportions.")
    if height:
        if height < 165:
            reasons.append("The streamlined colour palette can create a longer visual line.")
        elif height > 185:
            reasons.append("The layered proportions work well with a taller frame.")

    return score, reasons[:4]


def recommend(profile, occasion, situation, source="Online", excluded_names=None):
    excluded_names = excluded_names or set()
    candidates = []

    for outfit in OUTFITS:
        if outfit["name"] in excluded_names:
            continue
        score, reasons = score_outfit(outfit, profile, occasion, situation)
        if score <= 0:
            continue

        matching_hairs = []
        for h in HAIRSTYLES:
            if occasion in h["occasions"] and profile.get("hair_length") in h["lengths"] and profile.get("hair_type") in h["types"]:
                matching_hairs.append(h)

        if not matching_hairs:
            # Never violate current hair length. Relax occasion only.
            for h in HAIRSTYLES:
                if profile.get("hair_length") in h["lengths"] and profile.get("hair_type") in h["types"]:
                    matching_hairs.append(h)

        if not matching_hairs:
            continue

        hair = random.choice(matching_hairs)
        candidates.append({
            "outfit": outfit,
            "hairstyle": hair,
            "occasion": occasion,
            "situation": situation,
            "score": score,
            "reasons": reasons,
            "source": source,
        })

    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates[:3]


# ============================================================
# FEEDBACK / HISTORY / WARDROBE
# ============================================================

def save_history(user_id, look):
    conn = get_conn()
    conn.execute(
        "INSERT INTO history(user_id,look_json,occasion,created_at) VALUES(?,?,?,?)",
        (user_id, json.dumps(look), look.get("occasion",""), datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def save_feedback(user_id, look, action):
    conn = get_conn()
    conn.execute(
        "INSERT INTO feedback(user_id,look_json,action,created_at) VALUES(?,?,?,?)",
        (user_id, json.dumps(look), action, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def add_wardrobe(user_id, name, category, color, style, occasion, image_path=""):
    conn = get_conn()
    conn.execute("""
        INSERT INTO wardrobe(user_id,name,category,color,style,occasion,image_path,created_at)
        VALUES(?,?,?,?,?,?,?,?)
    """, (user_id,name,category,color,style,occasion,image_path,datetime.now().isoformat()))
    conn.commit()
    conn.close()


def get_wardrobe(user_id):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM wardrobe WHERE user_id=? ORDER BY id DESC", (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_history(user_id):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM history WHERE user_id=? ORDER BY id DESC LIMIT 30", (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def feedback_counts(user_id):
    conn = get_conn()
    rows = conn.execute(
        "SELECT action, COUNT(*) AS n FROM feedback WHERE user_id=? GROUP BY action",
        (user_id,)
    ).fetchall()
    conn.close()
    return {r["action"]: r["n"] for r in rows}


# ============================================================
# SESSION / LOGIN UI
# ============================================================

if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "looks" not in st.session_state:
    st.session_state.looks = []
if "excluded" not in st.session_state:
    st.session_state.excluded = set()

if not st.session_state.user_id:
    st.markdown("""
    <div class="hero">
        <h1>✨ AIStylist Buddy</h1>
        <p>Your personal AI stylist for outfits, hairstyles and complete looks.</p>
    </div>
    """, unsafe_allow_html=True)

    login_tab, register_tab = st.tabs(["🔐 Login", "📝 Create account"])

    with login_tab:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", type="primary")
            if submit:
                user = login(username, password)
                if user:
                    st.session_state.user_id = user["id"]
                    st.session_state.username = user["username"]
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

    with register_tab:
        with st.form("register_form"):
            username = st.text_input("Choose a username")
            password = st.text_input("Choose a password", type="password")
            confirm = st.text_input("Confirm password", type="password")
            submit = st.form_submit_button("Create account", type="primary")
            if submit:
                if password != confirm:
                    st.error("Passwords do not match.")
                else:
                    ok, msg = register(username, password)
                    if ok:
                        st.success(msg + " You can now log in.")
                    else:
                        st.error(msg)

    st.stop()


# ============================================================
# MAIN APP
# ============================================================

user_id = st.session_state.user_id
username = st.session_state.username
profile = parse_profile(get_profile(user_id))

with st.sidebar:
    st.markdown("## ✨ AIStylist Buddy")
    st.caption(f"Signed in as **{username}**")
    st.divider()

    page = st.radio(
        "Navigate",
        ["🏠 Dashboard", "👤 Profile", "✨ Stylist", "👕 My Wardrobe", "📜 History"]
    )

    st.divider()
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.user_id = None
        st.session_state.username = None
        st.session_state.looks = []
        st.rerun()


# ============================================================
# DASHBOARD
# ============================================================

if page == "🏠 Dashboard":
    name = profile.get("name") or username

    st.markdown(f"""
    <div class="hero">
        <h1>Welcome, {name}! 👋</h1>
        <p>Build your profile, tell me where you're going, and I'll curate your next look.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Profile", "Complete" if profile else "Not started")
    with c2:
        st.metric("Saved looks", len(get_wardrobe(user_id)))
    with c3:
        counts = feedback_counts(user_id)
        st.metric("Feedback given", sum(counts.values()))

    st.subheader("🚀 Quick start")
    st.info("Go to **Profile** first. Your recommendations use your preferences, measurements, hair information, occasion and situation.")

    st.markdown("### Product flow")
    st.markdown("""
    1. 👤 Create your profile and upload your photo.
    2. 🎯 Choose an occasion and describe your situation.
    3. ✨ Generate personalized outfit + hairstyle combinations.
    4. ❤️ Like, 👎 dislike, ⭐ save, or 🔄 try another.
    5. 🪞 Select a look for the future AI visualization/try-on integration.
    """)


# ============================================================
# PROFILE
# ============================================================

elif page == "👤 Profile":
    st.title("👤 Your Style Profile")
    st.caption("These details are used to personalize your recommendations.")

    defaults = {
        "name": profile.get("name",""),
        "age": profile.get("age",22),
        "gender": profile.get("gender","Male"),
        "height": profile.get("height",170.0),
        "chest": profile.get("chest",0.0),
        "waist": profile.get("waist",0.0),
        "hips": profile.get("hips",0.0),
        "preferred_colors": profile.get("preferred_colors",[]),
        "clothing_style": profile.get("clothing_style",[]),
        "hair_length": profile.get("hair_length","Short"),
        "hair_type": profile.get("hair_type","Straight"),
        "current_hairstyle": profile.get("current_hairstyle",""),
        "hair_preferences": profile.get("hair_preferences",""),
        "fashion_interests": profile.get("fashion_interests",""),
        "profile_photo": profile.get("profile_photo",""),
    }

    with st.form("profile"):
        st.subheader("📸 Profile photo")
        uploaded = st.file_uploader("Upload your photo", type=["jpg","jpeg","png"])
        if defaults["profile_photo"] and Path(defaults["profile_photo"]).exists():
            st.image(defaults["profile_photo"], width=180)

        st.subheader("👤 Basic details")
        a,b,c,d = st.columns(4)
        name = a.text_input("Name", defaults["name"])
        age = b.number_input("Age", 13, 100, int(defaults["age"]))
        gender = c.selectbox("Gender", ["Male","Female","Other"], index=["Male","Female","Other"].index(defaults["gender"]) if defaults["gender"] in ["Male","Female","Other"] else 0)
        height = d.number_input("Height (cm)", 100.0, 230.0, float(defaults["height"]))

        st.subheader("📏 Body measurements")
        a,b,c = st.columns(3)
        chest = a.number_input("Chest (cm)", 0.0, 200.0, float(defaults["chest"]))
        waist = b.number_input("Waist (cm)", 0.0, 200.0, float(defaults["waist"]))
        hips = c.number_input("Hips (cm)", 0.0, 200.0, float(defaults["hips"]))
        st.caption("Weight is intentionally not collected.")

        st.subheader("🎨 Fashion preferences")
        colors = st.multiselect("Preferred colors", COLORS, default=defaults["preferred_colors"])
        styles = st.multiselect("Clothing style", STYLES, default=defaults["clothing_style"])
        interests = st.text_area("Fashion interests", defaults["fashion_interests"], placeholder="e.g. sneakers, minimal outfits, Indian fusion")

        st.subheader("💇 Hair")
        a,b = st.columns(2)
        hair_length = a.selectbox("Current hair length", HAIR_LENGTHS, index=HAIR_LENGTHS.index(defaults["hair_length"]) if defaults["hair_length"] in HAIR_LENGTHS else 0)
        hair_type = b.selectbox("Hair type / texture", HAIR_TYPES, index=HAIR_TYPES.index(defaults["hair_type"]) if defaults["hair_type"] in HAIR_TYPES else 0)
        current_hair = st.text_input("Current hairstyle", defaults["current_hairstyle"], placeholder="e.g. short fade")
        hair_prefs = st.text_area("Hair preferences", defaults["hair_preferences"], placeholder="e.g. low maintenance, modern, professional")

        save = st.form_submit_button("💾 Save profile", type="primary")

        if save:
            photo_path = defaults["profile_photo"]
            if uploaded:
                ext = Path(uploaded.name).suffix.lower()
                photo_path = str(UPLOAD_DIR / f"user_{user_id}{ext}")
                Path(photo_path).write_bytes(uploaded.getbuffer())

            save_profile(user_id, {
                "name": name, "age": age, "gender": gender, "height": height,
                "chest": chest, "waist": waist, "hips": hips,
                "preferred_colors": colors, "clothing_style": styles,
                "hair_length": hair_length, "hair_type": hair_type,
                "current_hairstyle": current_hair,
                "hair_preferences": hair_prefs,
                "fashion_interests": interests,
                "profile_photo": photo_path,
            })
            st.success("Profile saved successfully. ✨")
            st.rerun()


# ============================================================
# STYLIST
# ============================================================

elif page == "✨ Stylist":
    st.title("✨ Personal Stylist")
    if not profile:
        st.warning("Create your profile first.")
        st.stop()

    occasion = st.selectbox("🎯 Occasion", OCCASIONS)
    situation = st.text_area(
        "📝 Tell your stylist about the situation",
        placeholder="Example: I have a college presentation tomorrow and want to look professional but comfortable."
    )
    source = st.radio(
        "👕 Recommendation source",
        ["Online", "My Wardrobe", "Both"],
        horizontal=True,
        help="Choose whether recommendations should consider your wardrobe."
    )

    if st.button("✨ Generate My Looks", type="primary", use_container_width=True):
        st.session_state.excluded = set()
        st.session_state.looks = recommend(profile, occasion, situation, source)
        for look in st.session_state.looks:
            save_history(user_id, look)
        if not st.session_state.looks:
            st.warning("No matching looks found. Try another occasion or update your hair profile.")
        else:
            st.success("Your personalized looks are ready! ✨")

    if st.session_state.looks:
        st.divider()
        st.subheader("Your personalized looks")

        for i, look in enumerate(st.session_state.looks):
            outfit = look["outfit"]
            hair = look["hairstyle"]

            with st.container(border=True):
                st.markdown(f"### Look {i+1} — {outfit['name']}")
                a,b = st.columns([2,1])

                with a:
                    st.markdown(f"**👕 Top:** {outfit['top']}")
                    st.markdown(f"**👖 Bottom:** {outfit['bottom']}")
                    st.markdown(f"**👟 Shoes:** {outfit['shoes']}")
                    st.markdown(f"**💍 Accessories:** {', '.join(outfit['accessories'])}")
                    st.markdown(f"**💇 Hairstyle:** {hair['name']}")
                    st.caption(hair["tip"])

                    st.write("**🎨 Palette:** " + ", ".join(outfit["colors"]))

                with b:
                    st.markdown("**Why it matched:**")
                    for reason in look["reasons"]:
                        st.write("✓ " + reason)

                x,y,z = st.columns(3)
                if x.button("❤️ Like", key=f"like_{i}", use_container_width=True):
                    save_feedback(user_id, look, "like")
                    st.toast("Liked — future recommendations can use this preference.")
                if y.button("👎 Dislike", key=f"dislike_{i}", use_container_width=True):
                    save_feedback(user_id, look, "dislike")
                    st.session_state.excluded.add(outfit["name"])
                    st.toast("Disliked — this look will be avoided.")
                if z.button("⭐ Save", key=f"save_{i}", use_container_width=True):
                    save_feedback(user_id, look, "save")
                    add_wardrobe(
                        user_id, outfit["name"], "Complete Look",
                        ", ".join(outfit["colors"]),
                        ", ".join(outfit["styles"]),
                        look["occasion"]
                    )
                    st.toast("Saved to My Wardrobe!")

                st.button(
                    "🪞 Select for AI visualization",
                    key=f"try_{i}",
                    on_click=lambda lk=look: st.session_state.update(selected_look=lk),
                    use_container_width=True,
                )

        if st.button("🔄 Try Another Set", use_container_width=True):
            excluded = {x["outfit"]["name"] for x in st.session_state.looks}
            st.session_state.looks = recommend(profile, occasion, situation, source, excluded)
            if not st.session_state.looks:
                st.session_state.excluded = set()
                st.session_state.looks = recommend(profile, occasion, situation, source)
            st.rerun()

        if st.session_state.get("selected_look"):
            st.divider()
            st.subheader("🪞 Complete Look Visualization")
            st.info(
                "The selected look is ready for the AI visualization layer. "
                "Connect an image-generation or virtual try-on provider here next."
            )
            st.json({
                "outfit": st.session_state.selected_look["outfit"],
                "hairstyle": st.session_state.selected_look["hairstyle"],
                "profile_height_cm": profile.get("height"),
                "body_measurements": {
                    "chest": profile.get("chest"),
                    "waist": profile.get("waist"),
                    "hips": profile.get("hips"),
                }
            })


# ============================================================
# WARDROBE
# ============================================================

elif page == "👕 My Wardrobe":
    st.title("👕 My Wardrobe")

    st.subheader("Add an item")
    with st.form("wardrobe_add"):
        a,b,c = st.columns(3)
        name = a.text_input("Item name")
        category = b.selectbox("Category", ["Top","Bottom","Dress","Shoes","Accessory"])
        color = c.selectbox("Color", COLORS)
        a,b,c = st.columns(3)
        style = a.selectbox("Style", STYLES)
        occasion = b.selectbox("Occasion", ["Any"] + OCCASIONS)
        image = c.file_uploader("Item image", type=["jpg","jpeg","png"])
        add = st.form_submit_button("Add to wardrobe", type="primary")

        if add and name:
            image_path = ""
            if image:
                image_path = str(UPLOAD_DIR / f"wardrobe_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}{Path(image.name).suffix}")
                Path(image_path).write_bytes(image.getbuffer())
            add_wardrobe(user_id, name, category, color, style, occasion, image_path)
            st.success("Item added.")
            st.rerun()

    st.divider()
    items = get_wardrobe(user_id)
    if not items:
        st.info("Your wardrobe is empty.")
    else:
        cols = st.columns(3)
        for i,item in enumerate(items):
            with cols[i % 3].container(border=True):
                if item["image_path"] and Path(item["image_path"]).exists():
                    st.image(item["image_path"], use_container_width=True)
                st.subheader(item["name"])
                st.caption(f"{item['category']} • {item['color']} • {item['style']}")
                st.write(f"Occasion: {item['occasion']}")


# ============================================================
# HISTORY
# ============================================================

elif page == "📜 History":
    st.title("📜 Recommendation History")
    history = get_history(user_id)

    if not history:
        st.info("No recommendations yet.")
    else:
        for row in history:
            look = json.loads(row["look_json"])
            outfit = look["outfit"]
            hair = look["hairstyle"]

            with st.container(border=True):
                st.markdown(f"### {outfit['name']}")
                st.caption(f"{row['occasion']} • {row['created_at'][:19]}")
                st.write(f"👕 {outfit['top']}  |  👖 {outfit['bottom']}  |  👟 {outfit['shoes']}")
                st.write(f"💇 {hair['name']} — {hair['tip']}")


# ============================================================
# FOOTER
# ============================================================

st.divider()
st.caption("✨ AIStylist Buddy — prototype. Recommendation engine is rule-based; AI visualization is designed as a replaceable service layer.")
