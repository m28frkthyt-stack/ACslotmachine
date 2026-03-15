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
        "weight": 4,
        "dealer_take": 5,
        "match": ["💸", "💸", "💸"],
        "message": "JACKPOT. You won. Leave your wager in the machine and GIVE 5 extra cancel tokens to the dealer.",
        "tone": "positive",
    },
    {
        "id": "major",
        "label": "Major scandal",
        "weight": 10,
        "dealer_take": 3,
        "match": ["🛢️", "✈️", "💸"],
        "message": "You won. Leave your wager in the machine and GIVE 3 extra cancel tokens to the dealer.",
        "tone": "positive",
    },
    {
        "id": "medium",
        "label": "Bad optics",
        "weight": 16,
        "dealer_take": 2,
        "match": ["🚗", "🥩", "🌍"],
        "message": "You won. Leave your wager in the machine and GIVE 2 extra cancel tokens to the dealer.",
        "tone": "positive",
    },
    {
        "id": "minor",
        "label": "Mild controversy",
        "weight": 20,
        "dealer_take": 1,
        "match": ["🍔", "🚬", "🧢"],
        "message": "You won. Leave your wager in the machine and GIVE 1 extra cancel token to the dealer.",
        "tone": "positive",
    },
    {
        "id": "lose",
        "label": "Loss",
        "weight": 50,
        "dealer_take": -2,
        "match": None,
        "message": "You lost. Take back the 1 token you placed and grab 1 extra token from the dealer. In total, take 2 tokens from the dealer.",
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
        "reels": ["❔", "❔", "❔"],
        "status": "Place 1 cancel token into the machine to spin. If you lose, take 2 tokens from the dealer. If you win, give extra tokens to the dealer.",
        "status_tone": "neutral",
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
    .stApp {
        background:
            radial-gradient(circle at 18% 0%, rgba(236,72,153,0.18), transparent 28%),
            radial-gradient(circle at 82% 10%, rgba(59,130,246,0.16), transparent 28%),
            linear-gradient(180deg, #07070a 0%, #0f172a 100%);
    }
    .block-container {
        padding-top: 0.8rem;
        padding-bottom: 1.2rem;
        max-width: 980px;
    }
    .hero {
        background: linear-gradient(135deg, rgba(255,255,255,0.09), rgba(255,255,255,0.03));
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 28px;
        padding: 20px 18px 18px 18px;
        box-shadow: 0 24px 80px rgba(0,0,0,0.35);
        margin-bottom: 14px;
        backdrop-filter: blur(12px);
    }
    .big-title {
        font-size: clamp(2.3rem, 6vw, 3.6rem);
        font-weight: 900;
        letter-spacing: -0.05em;
        line-height: 0.95;
        margin-bottom: 0.4rem;
        text-align: center;
    }
    .subtitle {
        color: #dbe4f0;
        margin: 0 auto 0.7rem auto;
        line-height: 1.55;
        max-width: 780px;
        font-size: 1rem;
        text-align: center;
    }
    .tiny-brand {
        color: #f9a8d4;
        font-size: 0.82rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        font-weight: 700;
        text-align: center;
        margin-top: 0.45rem;
    }
    .rules {
        margin-top: 0.9rem;
        display: grid;
        gap: 10px;
    }
    .rule {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 18px;
        padding: 13px 14px;
        color: #eef2ff;
        line-height: 1.45;
        font-size: 0.98rem;
        text-align: center;
    }
    .rule strong { color: white; }
    .machine-shell {
        background: linear-gradient(180deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03));
        border: 1px solid rgba(255,255,255,0.14);
        border-radius: 34px;
        padding: 18px;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.08), 0 30px 90px rgba(0,0,0,0.36);
        margin-bottom: 16px;
    }
    .reel-wrap {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
        margin: 0.3rem 0 0.15rem 0;
    }
    .reel {
        background:
            radial-gradient(circle at 50% 20%, rgba(255,255,255,0.16), transparent 30%),
            linear-gradient(180deg, #1f2937, #0f172a 70%);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 24px;
        min-height: 160px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: clamp(3.2rem, 9vw, 4.8rem);
        box-shadow: inset 0 10px 24px rgba(255,255,255,0.05), inset 0 -18px 35px rgba(0,0,0,0.28);
    }
    .status-box {
        border-radius: 22px;
        padding: 18px 18px;
        border: 1px solid rgba(255,255,255,0.10);
        background: rgba(15,23,42,0.78);
        margin-bottom: 1rem;
        box-shadow: 0 10px 35px rgba(0,0,0,0.22);
        text-align: center;
    }
    .status-positive {
        background: rgba(34, 197, 94, 0.14);
        border: 1px solid rgba(34, 197, 94, 0.38);
    }
    .status-neutral {
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.12);
    }
    .status-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.16em;
        color: #cbd5e1;
        margin-bottom: 0.4rem;
        font-weight: 800;
    }
    .score-grid {
        display:grid;
        grid-template-columns: 1fr;
        gap:12px;
        margin: 0.4rem 0 1rem 0;
    }
    .score-pill {
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 22px;
        padding: 12px 14px;
        color: #f8fafc;
        font-weight: 700;
        text-align:center;
    }
    .score-label {
        font-size:0.78rem;
        text-transform:uppercase;
        letter-spacing:0.12em;
        color:#cbd5e1;
        margin-bottom:4px;
    }
    .score-big {
        font-size: clamp(1.8rem, 5vw, 2.5rem);
        font-weight: 900;
        letter-spacing: -0.05em;
    }
    .stButton > button {
        border-radius: 20px;
        min-height: 58px;
        font-weight: 800;
        font-size: 1.02rem;
        border: 1px solid rgba(255,255,255,0.14);
        background: linear-gradient(180deg, #ffffff, #e5e7eb);
        color: #111827;
        box-shadow: 0 14px 30px rgba(0,0,0,0.2);
        width:100%;
    }
    .footer-note {
        text-align: center;
        color: #cbd5e1;
        font-size: 0.88rem;
        margin-top: 0.6rem;
    }
    @media (max-width: 1024px) {
        .block-container { max-width: 820px; padding-top: 0.5rem; }
        .hero { padding: 18px 16px 16px 16px; border-radius: 24px; }
        .machine-shell { padding: 14px; border-radius: 28px; }
        .reel { min-height: 132px; border-radius: 20px; }
        .status-box { padding: 16px 14px; }
    }
    @media (max-width: 768px) {
        .block-container { max-width: 700px; }
        .reel { min-height: 110px; font-size: clamp(2.6rem, 11vw, 4rem); }
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
    st.session_state.spins += 1

    outcome = pick_weighted_outcome()

    placeholder = st.empty()
    for _ in range(10):
        temp = [random_symbol(), random_symbol(), random_symbol()]
        placeholder.markdown(
            f'''
            <div class="machine-shell">
                <div class="reel-wrap">
                    <div class="reel">{temp[0]}</div>
                    <div class="reel">{temp[1]}</div>
                    <div class="reel">{temp[2]}</div>
                </div>
            </div>
            ''',
            unsafe_allow_html=True,
        )
        time.sleep(0.07)

    final_reels = build_reels(outcome)
    st.session_state.reels = final_reels

        st.session_state.status = outcome["message"]
    st.session_state.status_tone = outcome["tone"]


def reset_game():():
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

st.markdown(
    """
    <div class="hero">
        <div class="big-title">Inverse Cancel Casino</div>
        <div class="subtitle">
        Place <strong>1 cancel token</strong> into the machine to spin.
        <br><br>
        <strong>If you lose:</strong> take back the token you just placed, and then take <strong>1 extra token</strong> from the dealer.
        <br>
        So after a losing spin, you should physically take <strong>2 tokens total</strong> from the dealer.
        <br><br>
        <strong>If you win:</strong> leave your wager in the machine and give <strong>extra tokens</strong> to the dealer, depending on the result.
        </div>
        <div class="rules">
            <div class="rule"><strong>Step 1:</strong> put 1 cancel token into the machine.</div>
            <div class="rule"><strong>Losing spin:</strong> take back your wager and grab 1 extra token from the dealer. <strong>Take 2 tokens total.</strong></div>
            <div class="rule"><strong>Winning spin:</strong> keep your wager in the machine and give the extra number of tokens shown in the message.</div>
        </div>
        <div class="tiny-brand">vibe coded by ac-team</div>
    </div>
    """,
    unsafe_allow_html=True
)

# Center the slot machine
left, center, right = st.columns([1,2,1])

with center:

    st.markdown(
        f'''
        <div class="machine-shell">
            <div class="reel-wrap">
                <div class="reel">{st.session_state.reels[0]}</div>
                <div class="reel">{st.session_state.reels[1]}</div>
                <div class="reel">{st.session_state.reels[2]}</div>
            </div>
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

    st.markdown(
        f"""
        <div class="score-grid">
            <div class="score-pill">
                <div class="score-label">Spins</div>
                <div class="score-big">{st.session_state.spins}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    b1, b2 = st.columns(2)

    with b1:
        st.button("🎰 Spin the machine", use_container_width=True, on_click=spin_machine)

    with b2:
        st.button("↺ Reset", use_container_width=True, on_click=reset_game)

st.markdown('<div class="footer-note">AC-team experimental casino interface</div>', unsafe_allow_html=True)
