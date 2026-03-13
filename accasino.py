import random
import time
import streamlit as st

st.set_page_config(
    page_title="Inverse Cancel Casino",
    page_icon="🎰",
    layout="wide",
)

# -----------------------------
# Config
# -----------------------------
SYMBOLS = ["🚗", "🥩", "✈️", "🛢️", "🧴", "🍔", "🌍", "💸", "🚬", "🧢"]

OUTCOMES = [
    {
        "id": "jackpot",
        "label": "Jackpot",
        "weight": 2,
        "extra_loss": 5,
        "match": ["💸", "💸", "💸"],
        "message": "Jackpot. Extremely unfortunate. +6 tokens removed.",
        "tone": "positive",
    },
    {
        "id": "major",
        "label": "Major scandal",
        "weight": 6,
        "extra_loss": 3,
        "match": ["🛢️", "✈️", "💸"],
        "message": "Big win, bad life choice. +4 tokens removed.",
        "tone": "positive",
    },
    {
        "id": "medium",
        "label": "Bad optics",
        "weight": 12,
        "extra_loss": 2,
        "match": ["🚗", "🥩", "🌍"],
        "message": "Respectable cancellation. +3 tokens removed.",
        "tone": "positive",
    },
    {
        "id": "minor",
        "label": "Mild controversy",
        "weight": 20,
        "extra_loss": 1,
        "match": ["🍔", "🚬", "🧢"],
        "message": "Small win. +2 tokens removed.",
        "tone": "positive",
    },
    {
        "id": "lose",
        "label": "Loss",
        "weight": 60,
        "extra_loss": 1,
        "match": None,
        "message": "You lost. The machine still takes one extra token. +2 tokens removed.",
        "tone": "neutral",
    },
]

# -----------------------------
# Helpers
# -----------------------------
def pick_weighted_outcome():
    total = sum(o["weight"] for o in OUTCOMES)
    roll = random.uniform(0, total)
    upto = 0
    for outcome in OUTCOMES:
        upto += outcome["weight"]
        if roll <= upto:
            return outcome
    return OUTCOMES[-1]


def random_symbol():
    return random.choice(SYMBOLS)


def build_reels(outcome):
    if outcome["match"]:
        return outcome["match"]
    return [random_symbol(), random_symbol(), random_symbol()]


def init_state():
    defaults = {
        "tokens": 30,
        "reels": ["❔", "❔", "❔"],
        "status": "Wager 1 cancel token. Losing costs an extra token, but winning removes even more.",
        "status_tone": "neutral",
        "history": [],
        "spins": 0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# -----------------------------
# Styling
# -----------------------------
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    .big-title {
        font-size: 3rem;
        font-weight: 900;
        letter-spacing: -0.04em;
        margin-bottom: 0.25rem;
    }
    .subtitle {
        color: #9ca3af;
        margin-bottom: 1rem;
    }
    .reel-wrap {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 14px;
        margin: 1rem 0 1rem 0;
    }
    .reel {
        background: linear-gradient(180deg, #1f2937, #111827);
        border: 1px solid #374151;
        border-radius: 22px;
        min-height: 150px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 4rem;
        box-shadow: inset 0 6px 18px rgba(255,255,255,0.04);
    }
    .status-box {
        border-radius: 18px;
        padding: 16px 18px;
        border: 1px solid #374151;
        background: #111827;
        margin-bottom: 1rem;
    }
    .status-positive {
        background: rgba(34, 197, 94, 0.12);
        border: 1px solid rgba(34, 197, 94, 0.35);
    }
    .status-neutral {
        background: rgba(255,255,255,0.04);
        border: 1px solid #374151;
    }
    .status-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.14em;
        color: #9ca3af;
        margin-bottom: 0.35rem;
        font-weight: 700;
    }
    .score-card {
        background: #111827;
        border: 1px solid #374151;
        border-radius: 18px;
        padding: 16px;
    }
    .score-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: #9ca3af;
    }
    .score-value {
        font-size: 2rem;
        font-weight: 900;
        margin-top: 0.25rem;
    }
    .mini-card {
        background: #111827;
        border: 1px solid #374151;
        border-radius: 16px;
        padding: 14px;
        margin-bottom: 10px;
    }
    .history-symbols {
        font-size: 1.8rem;
        margin-bottom: 0.25rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

init_state()

# -----------------------------
# Actions
# -----------------------------
def spin_machine():
    if st.session_state.tokens <= 0:
        st.session_state.status = "No cancel tokens left. Truly healing behavior."
        st.session_state.status_tone = "neutral"
        return

    st.session_state.tokens = max(0, st.session_state.tokens - 1)
    st.session_state.spins += 1

    outcome = pick_weighted_outcome()

    # fake spin animation
    placeholder = st.empty()
    for _ in range(10):
        temp = [random_symbol(), random_symbol(), random_symbol()]
        placeholder.markdown(
            f'''
            <div class="reel-wrap">
                <div class="reel">{temp[0]}</div>
                <div class="reel">{temp[1]}</div>
                <div class="reel">{temp[2]}</div>
            </div>
            ''',
            unsafe_allow_html=True,
        )
        time.sleep(0.07)

    final_reels = build_reels(outcome)
    st.session_state.reels = final_reels

    # everybody loses an extra token on a loss, bigger wins remove more
    extra_loss = outcome["extra_loss"]
    st.session_state.tokens = max(0, st.session_state.tokens - extra_loss)
    total_removed = 1 + extra_loss

    st.session_state.status = outcome["message"]
    st.session_state.status_tone = outcome["tone"]
    st.session_state.history.insert(
        0,
        {
            "reels": final_reels,
            "label": outcome["label"],
            "removed": total_removed,
        },
    )
    st.session_state.history = st.session_state.history[:8]


def reset_game():
    for key in ["tokens", "reels", "status", "status_tone", "history", "spins"]:
        if key in st.session_state:
            del st.session_state[key]
    init_state()


# -----------------------------
# Derived stats
# -----------------------------
total_removed = sum(item["removed"] for item in st.session_state.history)
jackpots = sum(1 for item in st.session_state.history if item["label"] == "Jackpot")
status_class = "status-positive" if st.session_state.status_tone == "positive" else "status-neutral"

# -----------------------------
# UI
# -----------------------------
left, right = st.columns([1.3, 0.9], gap="large")

with left:
    st.markdown('<div class="big-title">Inverse Cancel Casino</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">Spin by wagering 1 cancel token. In this backwards casino, losing still costs you extra, but winning is even worse.</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'''
        <div class="reel-wrap">
            <div class="reel">{st.session_state.reels[0]}</div>
            <div class="reel">{st.session_state.reels[1]}</div>
            <div class="reel">{st.session_state.reels[2]}</div>
        </div>
        ''',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'''
        <div class="status-box {status_class}">
            <div class="status-label">Outcome</div>
            <div>{st.session_state.status}</div>
        </div>
        ''',
        unsafe_allow_html=True,
    )

    a, b = st.columns([1, 1])
    with a:
        st.button("🎰 Wager 1 token", use_container_width=True, on_click=spin_machine)
    with b:
        st.button("↺ Reset", use_container_width=True, on_click=reset_game)

with right:
    st.subheader("Scoreboard")
    s1, s2 = st.columns(2)
    s3, s4 = st.columns(2)

    with s1:
        st.markdown(f'<div class="score-card"><div class="score-label">Tokens left</div><div class="score-value">{st.session_state.tokens}</div></div>', unsafe_allow_html=True)
    with s2:
        st.markdown(f'<div class="score-card"><div class="score-label">Spins</div><div class="score-value">{st.session_state.spins}</div></div>', unsafe_allow_html=True)
    with s3:
        st.markdown(f'<div class="score-card"><div class="score-label">Tokens removed</div><div class="score-value">{total_removed}</div></div>', unsafe_allow_html=True)
    with s4:
        st.markdown(f'<div class="score-card"><div class="score-label">Jackpots</div><div class="score-value">{jackpots}</div></div>', unsafe_allow_html=True)

    st.subheader("Prize table")
    for outcome in OUTCOMES:
        if outcome["match"]:
            st.markdown(
                f'''
                <div class="mini-card">
                    <div style="display:flex;justify-content:space-between;gap:12px;align-items:center;">
                        <strong>{outcome["label"]}</strong>
                        <span>+{1 + outcome["extra_loss"]} removed</span>
                    </div>
                    <div class="history-symbols">{" ".join(outcome["match"])} </div>
                </div>
                ''',
                unsafe_allow_html=True,
            )
    st.markdown(
        '<div class="mini-card"><strong>Loss</strong><div class="tiny">Any other result still removes +2 tokens total.</div></div>',
        unsafe_allow_html=True,
    )

    st.subheader("Recent spins")
    if not st.session_state.history:
        st.markdown('<div class="history-empty">No spins yet. Suspiciously responsible.</div>', unsafe_allow_html=True)
    else:
        for item in st.session_state.history:
            st.markdown(
                f'''
                <div class="mini-card">
                    <div class="history-symbols">{" ".join(item["reels"])} </div>
                    <div style="display:flex;justify-content:space-between;gap:12px;align-items:center;">
                        <span>{item["label"]}</span>
                        <strong>+{item["removed"]} removed</strong>
                    </div>
                </div>
                ''',
                unsafe_allow_html=True,
            )
