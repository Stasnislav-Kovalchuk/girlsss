from __future__ import annotations

import streamlit as st
from streamlit_sortables import sort_items
from streamlit_folium import st_folium

from data import load_places, get_activities, get_food, places_by_id
from quiz import QUESTIONS
from itinerary import build_timeline, total_duration, day_warning
from map_utils import build_map

st.set_page_config(
    page_title="Наш Ідеальний День ❤️",
    page_icon="❤️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─── Global CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400&family=Inter:wght@300;400;500;600&display=swap');

* { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Background with subtle pattern */
.stApp {
    background:
        radial-gradient(circle at 20% 20%, rgba(255,182,200,0.25) 0%, transparent 50%),
        radial-gradient(circle at 80% 80%, rgba(255,210,180,0.20) 0%, transparent 50%),
        radial-gradient(circle at 50% 50%, rgba(255,240,245,1) 0%, #fff5f7 100%);
    min-height: 100vh;
}

/* ── hero ── */
.hero-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: clamp(2rem, 8vw, 3.2rem);
    font-weight: 700; color: #b5435e;
    text-align: center; line-height: 1.15; margin-bottom: 0.4rem;
    letter-spacing: -0.02em;
}
.hero-sub {
    font-size: clamp(0.9rem, 3vw, 1.05rem);
    color: #9a6070; text-align: center; margin-bottom: 1.6rem;
    font-weight: 300; letter-spacing: 0.01em;
}

/* ── floating heart ── */
@keyframes float {
    0%,100% { transform: translateY(0) rotate(-5deg); }
    50%      { transform: translateY(-12px) rotate(5deg); }
}
.float-heart { animation: float 3s ease-in-out infinite; display: inline-block; }

/* ── section labels ── */
.section-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: clamp(1.5rem, 5vw, 2rem);
    font-weight: 700; color: #b5435e;
    text-align: center; margin: 0.6rem 0 0.2rem; letter-spacing: -0.01em;
}
.section-sub {
    color: #9a6070; text-align: center;
    font-size: clamp(0.82rem, 2.5vw, 0.95rem);
    margin-bottom: 1.2rem; font-weight: 300;
}

/* ── quiz card ── */
.quiz-card {
    background: white;
    border-radius: 28px;
    padding: clamp(1.4rem, 5vw, 2.4rem) clamp(1rem, 4vw, 2rem);
    box-shadow: 0 8px 40px rgba(181,67,94,.12), 0 2px 8px rgba(0,0,0,.04);
    margin: 1rem 0;
    border: 1.5px solid rgba(232,132,154,.3);
    text-align: center;
    position: relative; overflow: hidden;
}
.quiz-card::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 4px;
    background: linear-gradient(90deg, #f0a0b8, #c0607e, #e8849a, #f5c0d0);
    background-size: 200% 100%;
    animation: shimmer 3s linear infinite;
}
@keyframes shimmer { 0%{background-position:0% 0%} 100%{background-position:200% 0%} }

.quiz-emoji { font-size: clamp(2.4rem, 8vw, 3.4rem); display: block; margin-bottom: 0.5rem; }
.quiz-question {
    font-family: 'Cormorant Garamond', serif;
    font-size: clamp(1.25rem, 4vw, 1.65rem);
    color: #6b2040 !important; font-weight: 600; line-height: 1.3;
}

/* ── progress ── */
.prog-wrap { margin: 0.8rem 0 0.2rem; }
.prog-label {
    display: flex; justify-content: space-between;
    font-size: 0.78rem; color: #b07a8a; margin-bottom: 5px; font-weight: 500;
}
.prog-bg {
    background: rgba(232,132,154,.15);
    border-radius: 20px; height: 6px; overflow: hidden;
}
.prog-fill {
    background: linear-gradient(90deg, #f0a0b8, #c0607e);
    border-radius: 20px; height: 6px;
    transition: width 0.5s cubic-bezier(0.4,0,0.2,1);
    box-shadow: 0 0 8px rgba(192,96,126,.4);
}

/* ── place cards ── */
@keyframes cardIn {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}

.place-card {
    background: #ffffff;
    border-radius: 20px;
    padding: 1.1rem 0.85rem 0.9rem;
    border: 2px solid rgba(232,132,154,.25);
    text-align: center;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 2px 14px rgba(0,0,0,.05);
    position: relative; overflow: hidden;
    animation: cardIn 0.4s ease backwards;
    min-height: 180px;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
}
.place-card::after {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, #f0a0b8, #c0607e);
    transform: scaleX(0); transform-origin: left;
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.place-card:hover::after { transform: scaleX(1); }
.place-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 14px 36px rgba(181,67,94,.18);
    border-color: rgba(232,132,154,.5);
}
.place-card.selected {
    background: linear-gradient(145deg, #fff0f5, #fff7f0);
    border-color: #c0607e;
    box-shadow: 0 10px 36px rgba(181,67,94,.22), 0 0 0 3px rgba(192,96,126,.12);
    transform: translateY(-3px);
}
.place-card.selected::after { transform: scaleX(1); }

.card-emoji {
    font-size: clamp(2rem, 7vw, 2.6rem);
    margin-bottom: 0.45rem; display: block;
    filter: drop-shadow(0 3px 6px rgba(0,0,0,.12));
}
.card-name {
    font-family: 'Cormorant Garamond', serif;
    font-size: clamp(0.95rem, 3vw, 1.05rem);
    font-weight: 700; color: #1a0a10 !important;
    margin-bottom: 0.2rem; line-height: 1.25;
}
.card-tagline {
    font-size: clamp(0.72rem, 2.2vw, 0.78rem);
    color: #b5435e !important; font-style: italic;
    margin-bottom: 0.35rem; font-weight: 500;
}
.card-desc {
    font-size: clamp(0.7rem, 2vw, 0.75rem);
    color: #3d2535 !important;
    line-height: 1.5; margin-bottom: 0.4rem;
}
.card-meta {
    font-size: 0.68rem; color: #7a5060 !important;
    background: rgba(192,96,126,.07);
    border-radius: 20px; padding: 0.18rem 0.6rem;
    display: inline-block; margin-top: 0.2rem; font-weight: 500;
}

/* ── Stas box ── */
@keyframes pulse-border {
    0%,100% { border-color: rgba(232,132,154,.5); box-shadow: 0 0 0 0 rgba(232,132,154,.3); }
    50%      { border-color: rgba(192,96,126,.8);  box-shadow: 0 0 0 8px rgba(232,132,154,.0); }
}
.stas-box {
    background: linear-gradient(135deg, rgba(255,240,248,.9), rgba(255,248,235,.9));
    border: 2px dashed rgba(232,132,154,.6);
    border-radius: 24px; padding: 1.5rem 1rem;
    text-align: center; margin: 1.2rem 0;
    animation: pulse-border 2.5s ease-in-out infinite;
}
.stas-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: clamp(1.2rem, 4vw, 1.5rem);
    color: #b5435e !important; margin-bottom: 0.35rem; font-weight: 700;
}
.stas-sub { color: #7a5060 !important; font-size: 0.88rem; margin-bottom: 0.8rem; font-weight: 300; }

@keyframes stas-pulse {
    0%   { box-shadow: 0 0 0 0 rgba(192,96,126,.6); }
    70%  { box-shadow: 0 0 0 14px rgba(192,96,126,.0); }
    100% { box-shadow: 0 0 0 0 rgba(192,96,126,.0); }
}
.stas-btn-wrap .stButton > button {
    animation: stas-pulse 2s ease-in-out infinite !important;
    font-size: 1.05rem !important; padding: 0.7rem 2rem !important;
}

/* ── info banners ── */
.banner-green {
    background: linear-gradient(135deg, #e8f5e9, #f1f8e9);
    border: 1.5px solid #a5d6a7; border-radius: 16px;
    padding: 0.9rem 1.1rem; text-align: center;
    color: #1b5e20 !important; font-weight: 600; margin: 0.8rem 0;
    font-size: 0.95rem;
}
.banner-hint {
    text-align: center; color: #9a7080 !important;
    font-size: 0.88rem; margin-top: 1.4rem; font-weight: 300;
}

/* ── block divider ── */
.divider {
    height: 2px; margin: 2rem 0 1.6rem;
    background: linear-gradient(90deg, transparent, rgba(232,132,154,.4), transparent);
    border: none;
}

/* ── timeline ── */
.tl-item {
    background: white; border-radius: 16px;
    padding: 0.9rem 1.2rem; margin-bottom: 0.55rem;
    border-left: 5px solid #e8849a;
    box-shadow: 0 2px 12px rgba(0,0,0,.05);
    transition: transform 0.2s;
}
.tl-item:hover { transform: translateX(3px); }
.tl-time { color: #c0607e !important; font-weight: 700; font-size: 0.88rem; letter-spacing: 0.03em; }
.tl-name { font-family: 'Cormorant Garamond', serif; font-size: 1.1rem; color: #1a0a10 !important; font-weight: 600; margin-top: 0.1rem; }
.tl-meta { font-size: 0.78rem; color: #7a6070 !important; margin-top: 0.1rem; }

/* ── warn ── */
.warn {
    background: #fff8e1; border-left: 4px solid #ffb74d;
    border-radius: 12px; padding: 0.8rem 1rem;
    color: #7a5500 !important; font-size: 0.88rem; margin: 0.8rem 0;
}

/* ── final card ── */
.final-plan {
    background: linear-gradient(145deg, #fff5f8, #fff8f0);
    border-radius: 28px; padding: 1.8rem 1.4rem;
    border: 2px solid rgba(232,132,154,.3);
    box-shadow: 0 8px 40px rgba(181,67,94,.1);
    margin: 0.8rem 0;
}

/* ── love closing ── */
.love-banner {
    background: linear-gradient(135deg, #fce8f0, #fff5ed);
    border-radius: 20px; padding: 1.3rem;
    text-align: center; border: 2px solid rgba(232,132,154,.3);
    color: #6b2040 !important; line-height: 2; margin-top: 1.2rem;
    font-size: clamp(0.88rem, 2.5vw, 1rem);
}

/* ── streamlit overrides ── */
.stButton > button {
    border-radius: 50px !important;
    border: 2px solid #e8849a !important;
    background: white !important;
    color: #b5435e !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    min-height: 48px !important;
    font-size: 0.95rem !important;
    transition: all 0.2s cubic-bezier(0.4,0,0.2,1) !important;
}
.stButton > button:hover {
    background: #fff0f5 !important;
    color: #8b2040 !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #e8849a, #c0607e) !important;
    color: white !important;
    border-color: transparent !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #d4728a, #a84f6c) !important;
    color: white !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(192,96,126,.4) !important;
}
.stButton > button:disabled {
    opacity: 0.35 !important;
    transform: none !important;
    color: #c0a0a8 !important;
    background: #f8f0f2 !important;
    border-color: #f0d6de !important;
}

div[data-testid="stRadio"] > label { display: none; }
div[data-testid="stRadio"] > div {
    display: flex; flex-direction: column; gap: 0.5rem;
}
div[data-testid="stRadio"] > div > label {
    background: white !important;
    border: 2px solid rgba(232,132,154,.3) !important;
    border-radius: 14px !important;
    padding: 0.85rem 1.1rem !important;
    font-size: clamp(0.9rem, 3vw, 1rem) !important;
    color: #1a0a10 !important;
    transition: all 0.2s !important; text-align: center;
    min-height: 52px !important;
}
div[data-testid="stRadio"] > div > label *,
div[data-testid="stRadio"] > div > label p,
div[data-testid="stRadio"] > div > label span {
    color: #1a0a10 !important;
}
div[data-testid="stRadio"] > div > label:hover {
    border-color: #e8849a !important;
    background: #fff0f5 !important;
}
div[data-testid="stRadio"] > div > label:hover *,
div[data-testid="stRadio"] > div > label:hover span,
div[data-testid="stRadio"] > div > label:hover p {
    color: #8b2040 !important;
}
div[data-testid="stRadio"] > div > label[data-checked="true"] {
    border-color: #c0607e !important;
    background: linear-gradient(135deg, #fff0f5, #fff8f0) !important;
    font-weight: 600 !important;
}
div[data-testid="stRadio"] > div > label[data-checked="true"],
div[data-testid="stRadio"] > div > label[data-checked="true"] *,
div[data-testid="stRadio"] > div > label[data-checked="true"] p,
div[data-testid="stRadio"] > div > label[data-checked="true"] span {
    color: #6b2040 !important; font-weight: 600 !important;
}

/* ── slider ── */
div[data-testid="stSlider"] > div > div > div > div {
    background: linear-gradient(90deg, #e8849a, #c0607e) !important;
}

/* ── mobile ── */
@media (max-width: 480px) {
    .place-card { min-height: 160px; padding: 0.9rem 0.7rem; }
    .card-desc  { display: none; }
    .stButton > button { min-height: 44px !important; font-size: 0.85rem !important; }
}
</style>
""", unsafe_allow_html=True)

# ─── State ────────────────────────────────────────────────────────────────────
_DEF: dict = {
    "page": "home",
    "quiz_step": 0,
    "selected_activities": [],
    "stas_unlocked": False,
    "selected_food": None,
    "my_day": [],
}

def _init():
    for k, v in _DEF.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init()
all_places   = load_places()
activities   = get_activities(all_places)
food_places  = get_food(all_places)
places_index = places_by_id(all_places)

def go(page: str):
    st.session_state["page"] = page
    st.rerun()

def restart():
    for k, v in _DEF.items():
        st.session_state[k] = v
    st.rerun()

def _place_label(p: dict) -> str:
    return f"{p.get('emoji','')} {p['name']}"


# ══════════════════════════════════════════════════════════════════════════════
# HOME
# ══════════════════════════════════════════════════════════════════════════════
def page_home():
    st.markdown(
        '<div style="text-align:center;font-size:clamp(3rem,12vw,5rem);margin-top:1.5rem">'
        '<span class="float-heart">💕</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="hero-title">Наш Ідеальний День</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-sub">Оберемо разом — і буде незабутньо ✨</div>',
        unsafe_allow_html=True,
    )

    st.markdown("""
    <div style="background:white;border-radius:24px;padding:1.6rem 1.4rem;
                box-shadow:0 4px 24px rgba(181,67,94,.09);
                border:1.5px solid rgba(232,132,154,.25);
                margin:0 0 2rem;position:relative;overflow:hidden;">
        <div style="position:absolute;top:0;left:0;right:0;height:3px;
                    background:linear-gradient(90deg,#f0a0b8,#c0607e,#e8849a)"></div>
        <div style="text-align:center;line-height:2.1;color:#3d2535;font-size:clamp(.9rem,3vw,1rem);">
            🌸 Кілька романтичних питань<br>
            💝 Обираєш активність на день<br>
            🍽️ Обираєш де поїсти<br>
            🗺️ Отримуєш план із картою та таймлайном
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Почати наш ідеальний день ❤️", type="primary", use_container_width=True):
            go("quiz")


# ══════════════════════════════════════════════════════════════════════════════
# QUIZ
# ══════════════════════════════════════════════════════════════════════════════
def page_quiz():
    step  = st.session_state["quiz_step"]
    total = len(QUESTIONS)
    q     = QUESTIONS[step]
    pct   = int(step / total * 100)

    st.markdown(f"""
    <div class="prog-wrap">
        <div class="prog-label">
            <span>Питання {step+1} з {total}</span><span>{pct}%</span>
        </div>
        <div class="prog-bg"><div class="prog-fill" style="width:{pct}%"></div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="quiz-card">
        <span class="quiz-emoji">{q['emoji']}</span>
        <div class="quiz-question">{q['text']}</div>
    </div>
    """, unsafe_allow_html=True)

    st.radio(q["text"], q["options"], key=f"r_{step}", label_visibility="collapsed")

    st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)
    col_b, col_f = st.columns([1, 2])
    with col_b:
        if step > 0 and st.button("← Назад", use_container_width=True):
            st.session_state["quiz_step"] -= 1
            st.rerun()
    with col_f:
        label = "Далі →" if step < total - 1 else "Обираємо наш день 💝"
        if st.button(label, type="primary", use_container_width=True):
            if step < total - 1:
                st.session_state["quiz_step"] += 1
                st.rerun()
            else:
                go("pick_day")


# ══════════════════════════════════════════════════════════════════════════════
# PICK DAY
# ══════════════════════════════════════════════════════════════════════════════
def _card(p: dict, selected: bool) -> str:
    cls = "place-card selected" if selected else "place-card"
    return f"""
    <div class="{cls}">
        <div class="card-emoji">{p['emoji']}</div>
        <div class="card-name">{p['name']}</div>
        <div class="card-tagline">{p['tagline']}</div>
        <div class="card-desc">{p['description']}</div>
        <div class="card-meta">📍 {p['distance_from_lviv']} км &nbsp;·&nbsp; 🕐 {p['time_needed']}</div>
    </div>
    """


def _render_grid(places: list[dict], sel_ids: list[str], key_prefix: str,
                 max_sel: int = 1, on_select=None, on_deselect=None):
    cols = st.columns(2)
    for i, place in enumerate(places):
        pid    = place["id"]
        is_sel = pid in sel_ids
        can    = len(sel_ids) < max_sel or is_sel

        with cols[i % 2]:
            st.markdown(_card(place, is_sel), unsafe_allow_html=True)
            if is_sel:
                if st.button("✅ Обрано", key=f"{key_prefix}_{pid}", use_container_width=True):
                    if on_deselect:
                        on_deselect(pid)
            elif can:
                if st.button("Обрати ❤️", key=f"{key_prefix}_{pid}",
                             type="primary", use_container_width=True):
                    if on_select:
                        on_select(pid)
            else:
                st.button("Обрати ❤️", key=f"{key_prefix}_{pid}",
                          disabled=True, use_container_width=True)


def page_pick_day():
    sel_act       = st.session_state["selected_activities"]
    stas_unlocked = st.session_state["stas_unlocked"]
    sel_food      = st.session_state["selected_food"]
    max_act       = 2 if stas_unlocked else 1

    # ── Block 1: Activity ─────────────────────────────────────────────────────
    st.markdown('<div class="section-title">Де проведемо час? 🌸</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="section-sub">{"Обери до двох місць" if stas_unlocked else "Обери одне місце"}</div>',
        unsafe_allow_html=True,
    )

    def act_select(pid):
        st.session_state["selected_activities"] = sel_act + [pid]
        st.rerun()

    def act_deselect(pid):
        st.session_state["selected_activities"] = [x for x in sel_act if x != pid]
        st.rerun()

    _render_grid(activities, sel_act, "act", max_act, act_select, act_deselect)

    # ── Stas block ────────────────────────────────────────────────────────────
    if len(sel_act) == 1 and not stas_unlocked:
        st.markdown("""
        <div class="stas-box">
            <div class="stas-title">🥺 Хочеш іще одне місце?</div>
            <div class="stas-sub">
                Можна взяти два — але для цього потрібен дозвіл Стаса ❤️
            </div>
        </div>
        """, unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="stas-btn-wrap">', unsafe_allow_html=True)
            if st.button("Попросити Стаса 💕", type="primary", use_container_width=True):
                st.session_state["stas_unlocked"] = True
                st.balloons()
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    elif stas_unlocked and len(sel_act) < 2:
        st.markdown("""
        <div class="banner-green">🎉 Стас сказав ТАК! Обери ще одне місце ❤️❤️</div>
        """, unsafe_allow_html=True)

    elif stas_unlocked and len(sel_act) == 2:
        st.markdown("""
        <div class="banner-green">✅ Два місця обрано — Стас пишається! ❤️❤️</div>
        """, unsafe_allow_html=True)

    # ── Block 2: Food ─────────────────────────────────────────────────────────
    if sel_act:
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Де поїмо? 🍽️</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">Обери ресторан або місце для вечері</div>', unsafe_allow_html=True)

        def food_select(pid):
            st.session_state["selected_food"] = pid
            st.rerun()

        def food_deselect(_pid):
            st.session_state["selected_food"] = None
            st.rerun()

        _render_grid(
            food_places,
            [sel_food] if sel_food else [],
            "food", 1,
            food_select, food_deselect,
        )

    # ── CTA ───────────────────────────────────────────────────────────────────
    if sel_act and sel_food:
        st.markdown("<div style='margin:2rem 0 0.5rem'></div>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Будуємо наш день! ❤️", type="primary", use_container_width=True):
                day = [places_index[pid] for pid in sel_act if pid in places_index]
                if sel_food and sel_food in places_index:
                    day.append(places_index[sel_food])
                st.session_state["my_day"] = day
                go("my_day")
    elif sel_act and not sel_food:
        st.markdown(
            '<div class="banner-hint">👆 Оберіть місце для вечері, щоб продовжити</div>',
            unsafe_allow_html=True,
        )


# ══════════════════════════════════════════════════════════════════════════════
# MY DAY
# ══════════════════════════════════════════════════════════════════════════════
def page_my_day():
    my_day: list[dict] = st.session_state.get("my_day", [])

    st.markdown('<div class="section-title">Наш план 🌸</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Ти обрала з любов\'ю — складаємо маршрут!</div>', unsafe_allow_html=True)

    if not my_day:
        st.markdown('<div style="text-align:center;padding:2rem;color:#9a7080">💝 Список порожній</div>',
                    unsafe_allow_html=True)
        if st.button("← Назад", type="primary"):
            go("pick_day")
        return

    st.markdown(
        '<div style="font-size:.82rem;color:#9a7080;margin-bottom:.5rem;font-weight:500">'
        'Перетягни, щоб змінити порядок:</div>',
        unsafe_allow_html=True,
    )
    labels    = [_place_label(p) for p in my_day]
    sorted_lbl = sort_items(labels)
    lmap      = {_place_label(p): p for p in my_day}
    reordered = [lmap[l] for l in sorted_lbl if l in lmap]
    st.session_state["my_day"] = reordered

    for i, place in enumerate(reordered):
        c1, c2 = st.columns([6, 1])
        with c1:
            st.markdown(
                f'<div style="padding:.3rem 0;color:#1a0a10;font-size:.95rem">'
                f'<b style="color:#b5435e">{i+1}.</b> {place.get("emoji","")} '
                f'<b style="color:#1a0a10">{place["name"]}</b>'
                f'<span style="color:#9a7080;font-size:.82rem"> — {place.get("time_needed","")}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
        with c2:
            if st.button("✕", key=f"del_{place['id']}_{i}"):
                st.session_state["my_day"] = [p for p in reordered if p["id"] != place["id"]]
                st.rerun()

    warn = day_warning(reordered)
    if warn:
        st.markdown(f'<div class="warn">⚠️ {warn}</div>', unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-family:\'Cormorant Garamond\',serif;font-size:1.4rem;'
        'color:#b5435e;text-align:center;margin-bottom:.8rem;font-weight:700">🕐 Таймлайн</div>',
        unsafe_allow_html=True,
    )

    start_h  = st.slider("Початок дня:", 7, 12, 10, format="%d:00")
    timeline = build_timeline(reordered, start_hour=start_h)
    dur      = total_duration(timeline)

    for entry in timeline:
        p = entry["place"]
        st.markdown(f"""
        <div class="tl-item">
            <div class="tl-time">{entry['arrive']} – {entry['depart']}</div>
            <div class="tl-name">{p.get('emoji','')} {p['name']}</div>
            <div class="tl-meta">{p.get('time_needed','')} &nbsp;·&nbsp; {p.get('distance_from_lviv',0)} км від Львова</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="text-align:center;background:linear-gradient(135deg,white,#fff8f0);
                border-radius:16px;padding:.9rem;border:2px solid rgba(232,132,154,.3);
                color:#b5435e;font-weight:700;font-size:1.05rem;margin-top:.8rem;
                box-shadow:0 4px 16px rgba(181,67,94,.1)">
        ⏱ Загальний час разом: {dur} 💝
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-family:\'Cormorant Garamond\',serif;font-size:1.4rem;'
        'color:#b5435e;text-align:center;margin-bottom:.8rem;font-weight:700">🗺️ Карта маршруту</div>',
        unsafe_allow_html=True,
    )
    st_folium(build_map(reordered), width=None, height=380)

    st.markdown("<div style='margin:1.5rem 0'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("← Змінити", use_container_width=True):
            go("pick_day")
    with c2:
        if st.button("Фінальний план ✨", type="primary", use_container_width=True):
            go("final")
    with c3:
        if st.button("Заново 🔄", use_container_width=True):
            restart()


# ══════════════════════════════════════════════════════════════════════════════
# FINAL
# ══════════════════════════════════════════════════════════════════════════════
def page_final():
    my_day   = st.session_state.get("my_day", [])
    timeline = build_timeline(my_day)
    dur      = total_duration(timeline)

    st.markdown(
        '<div style="text-align:center;font-size:clamp(2.5rem,10vw,4rem);margin-top:1.5rem">'
        '<span class="float-heart">🌹</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="section-title">Ваш ідеальний день готовий!</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-sub">Обрала з любов\'ю — він точно буде незабутнім 💕</div>',
        unsafe_allow_html=True,
    )

    st.markdown(f"""
    <div class="final-plan">
        <div style="font-family:'Cormorant Garamond',serif;font-size:clamp(1.5rem,6vw,2rem);
                    color:#b5435e;text-align:center;margin-bottom:.4rem;font-weight:700">
            Наш ідеальний день 💝
        </div>
        <div style="color:#9a6070;text-align:center;font-size:.9rem;margin-bottom:1.2rem;font-weight:300">
            {len(my_day)} місць · {dur} разом
        </div>
    """, unsafe_allow_html=True)

    for i, entry in enumerate(timeline):
        p = entry["place"]
        st.markdown(f"""
        <div style="background:white;border-radius:14px;padding:.85rem 1.1rem;margin:.4rem 0;
                    border-left:4px solid #e8849a;
                    box-shadow:0 2px 10px rgba(0,0,0,.05)">
            <div style="color:#c0607e;font-weight:700;font-size:.78rem;letter-spacing:.05em;
                        text-transform:uppercase">{entry['arrive']} – {entry['depart']}</div>
            <div style="font-family:'Cormorant Garamond',serif;font-size:1.1rem;
                        color:#1a0a10;font-weight:600;margin-top:.1rem">
                {p.get('emoji','')} {i+1}. {p['name']}
            </div>
            <div style="font-size:.78rem;color:#6a5060;margin-top:.1rem">{p['description'][:85]}…</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st_folium(build_map(my_day), width=None, height=340)

    st.markdown("""
    <div class="love-banner">
        💕 Майте незабутній день разом<br>
        🌸 Кожен момент — ваша спільна казка<br>
        ❤️ З любов'ю, ваш помічник ідеального дня
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='margin:1.5rem 0'></div>", unsafe_allow_html=True)

    plan_text = _plan_txt(timeline, dur)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("← Редагувати", use_container_width=True):
            go("my_day")
    with c2:
        if st.button("Заново 🔄", use_container_width=True):
            restart()

    st.markdown("<div style='margin:0.6rem 0'></div>", unsafe_allow_html=True)
    _tg_button(plan_text)

    st.markdown("<div style='margin:0.4rem 0'></div>", unsafe_allow_html=True)
    st.download_button(
        "💾 Зберегти план (.txt)",
        plan_text,
        "ідеальний_день.txt", "text/plain",
        use_container_width=True,
    )


def _plan_txt(timeline: list[dict], dur: str) -> str:
    lines = ["💝 Наш Ідеальний День 💝", "=" * 34, ""]
    for i, e in enumerate(timeline):
        p = e["place"]
        lines += [
            f"{p.get('emoji','')} {i+1}. {p['name']}",
            f"   🕐 {e['arrive']} – {e['depart']}",
            f"   📍 {p.get('distance_from_lviv', 0)} км від Львова",
            f"   {p['description']}", "",
        ]
    lines += [f"⏱ Загальний час: {dur}", "", "❤️ З любов'ю ♡"]
    return "\n".join(lines)


def _tg_button(text: str) -> None:
    import urllib.parse
    encoded = urllib.parse.quote(text)
    url = f"https://t.me/share/url?text={encoded}"
    st.markdown(f"""
    <a href="{url}" target="_blank" style="
        display: block; width: 100%; text-align: center;
        background: linear-gradient(135deg, #29a7e1, #1e8bc3);
        color: white !important; font-weight: 600;
        border-radius: 50px; padding: 0.82rem 1rem;
        font-size: 0.95rem; text-decoration: none;
        font-family: 'Inter', sans-serif;
        box-shadow: 0 4px 16px rgba(41,167,225,.35);
        transition: all 0.2s;
        min-height: 48px; line-height: 1.3;
    ">
        ✈️ Надіслати Стасу в Telegram
    </a>
    """, unsafe_allow_html=True)


# ─── Router ───────────────────────────────────────────────────────────────────
{
    "home":     page_home,
    "quiz":     page_quiz,
    "pick_day": page_pick_day,
    "my_day":   page_my_day,
    "final":    page_final,
}.get(st.session_state.get("page", "home"), page_home)()
