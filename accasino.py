import random
import time
import streamlit as st

st.set_page_config(
    page_title="Inverse Cancel Casino",
    page_icon="🎰",
    layout="wide",
)

SYMBOLS = ["🚗", "🥩", "✈️", "🛢️", "🧴", "🍔", "🌍", "💸", "🚬", "🧢"]
WIN_SYMBOLS = {
    "jackpot": "💸",
    "major": "🛢️",
    "medium": "🌍",
    "minor": "🧢",
}

OUTCOMES = [
    {
        "id": "jackpot",
        "label": "Jackpot",
        "weight": 4,
        "dealer_take": 5,
        "message": "JACKPOT. You won. Leave your wager in the machine and GIVE 5 extra cancel tokens to the dealer.",
        "tone": "positive",
    },
    {
        "id": "major",
        "label": "Major scandal",
        "weight": 10,
        "dealer_take": 3,
        "message": "You won. Leave your wager in the machine and GIVE 3 extra cancel tokens to the dealer.",
        "tone": "positive",
    },
    {
        "id": "medium",
        "label": "Bad optics",
        "weight": 16,
        "dealer_take": 2,
        "message": "You won. Leave your wager in the machine and GIVE 2 extra cancel tokens to the dealer.",
        "tone": "positive",
    },
    {
        "id": "minor",
        "label": "Mild controversy",
        "weight": 20,
        "dealer_take": 1,
        "message": "You won. Leave your wager in the machine and GIVE 1 extra cancel token to the dealer.",
        "tone": "positive",
    },
    {
        "id": "lose",
        "label": "Loss",
        "weight": 50,
        "dealer_take": -2,
        "message": "You lost. Take back the 1 token you placed and grab 1 extra token from the dealer. In total, take 2 tokens from the dealer.",
        "tone": "neutral",
    },
]


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
    if outcome["id"] != "lose":
        symbol = WIN_SYMBOLS[outcome["id"]]
        return [symbol, symbol, symbol]

    mode = random.choice(["pair_left", "pair_right", "sandwich", "all_diff"])

    if mode == "pair_left":
        a = random_symbol()
        b = random.choice([s for s in SYMBOLS if s != a])
        reels = [a, a, b]
    elif mode == "pair_right":
        a = random_symbol()
        b = random.choice([s for s in SYMBOLS if s != a])
        reels = [b, a, a]
    elif mode == "sandwich":
        a = random_symbol()
        b = random.choice([s for s in SYMBOLS if s != a])
        reels = [a, b, a]
    else:
        reels = random.sample(SYMBOLS, 3)

    if reels[0] == reels[1] == reels[2]:
        reels[2] = random.choice([s for s in SYMBOLS if s != reels[0]])
    return reels


def init_state():
    defaults = {
        "reels": ["❔", "❔", "❔"],
        "status": "Place 1 cancel token into the machine to spin.",
        "status_tone": "neutral",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def validate_config():
    assert any(o["id"] == "lose" for o in OUTCOMES), "A loss outcome is required."
    assert sum(o["weight"] for o in OUTCOMES) > 0, "Outcome weights must sum to more than 0."
    loss_weight = sum(o["weight"] for o in OUTCOMES if o["id"] == "lose")
    total_weight = sum(o["weight"] for o in OUTCOMES)
    loss_rate = loss_weight / total_weight
    assert 0.45 <= loss_rate <= 0.55, "Loss probability should stay around 50%."
    for outcome in OUTCOMES:
        assert "message" in outcome and outcome["message"], "Each outcome needs a message."
        assert outcome["tone"] in {"positive", "neutral"}, "Unexpected tone value."
    for outcome_id, symbol in WIN_SYMBOLS.items():
        assert outcome_id in {o["id"] for o in OUTCOMES if o["id"] != "lose"}, "Each win symbol needs a matching outcome id."
        assert symbol in SYMBOLS, "Win symbols must come from SYMBOLS."


validate_config()
init_state()

st.markdown(
    """
    <style>
    .stApp {
        min-height: 100vh;
    }
    [data-testid="stAppViewContainer"] > .main {
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .page-shell {
        width: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    .stApp {
        background:
            radial-gradient(circle at 18% 0%, rgba(236,72,153,0.18), transparent 28%),
            radial-gradient(circle at 82% 10%, rgba(59,130,246,0.16), transparent 28%),
            linear-gradient(180deg, #07070a 0%, #0f172a 100%);
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1.2rem;
        max-width: 900px;
    }
    .hero {
        background: linear-gradient(135deg, rgba(255,255,255,0.09), rgba(255,255,255,0.03));
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 28px;
        padding: 18px 16px 16px 16px;
        box-shadow: 0 24px 80px rgba(0,0,0,0.35);
        margin-bottom: 14px;
        backdrop-filter: blur(12px);
        text-align: center;
    }
    .big-title {
        font-size: clamp(2.2rem, 6vw, 3.5rem);
        font-weight: 900;
        letter-spacing: -0.05em;
        line-height: 0.95;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    .tiny-brand {
        color: #f9a8d4;
        font-size: 0.82rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        font-weight: 700;
        text-align: center;
        margin-top: 0.2rem;
    }
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
        min-height: 180px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: clamp(3.4rem, 10vw, 5rem);
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
    .stButton > button {
        border-radius: 20px;
        min-height: 60px;
        font-weight: 800;
        font-size: 1.05rem;
        border: 1px solid rgba(255,255,255,0.14);
        background: linear-gradient(180deg, #ffffff, #e5e7eb);
        color: #111827;
        box-shadow: 0 14px 30px rgba(0,0,0,0.2);
        width: 100%;
    }
    .footer-note {
        text-align: center;
        color: #cbd5e1;
        font-size: 0.88rem;
        margin-top: 0.6rem;
    }
    @media (max-width: 1024px) {
        .block-container { max-width: 820px; padding-top: 0.5rem; }
        .hero { padding: 16px 14px 14px 14px; border-radius: 24px; }
        .machine-shell { padding: 14px; border-radius: 28px; }
        .reel { min-height: 140px; border-radius: 20px; }
        .status-box { padding: 16px 14px; }
    }
    @media (max-width: 768px) {
        .block-container { max-width: 700px; }
        .reel { min-height: 118px; font-size: clamp(2.8rem, 12vw, 4rem); }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def spin_machine():
    outcome = pick_weighted_outcome()

    machine_placeholder = st.empty()

    # Build final result first so the spin animation can converge to it.
    final_reels = build_reels(outcome)

    # Reel-by-reel slot style animation.
    spin_frames = 14
    for frame in range(spin_frames):
        if frame < 8:
            current = [random_symbol(), random_symbol(), random_symbol()]
        elif frame < 10:
            current = [final_reels[0], random_symbol(), random_symbol()]
        elif frame < 12:
            current = [final_reels[0], final_reels[1], random_symbol()]
        else:
            current = final_reels

        machine_placeholder.markdown(
            f'''
            <div class="machine-shell">
                <div class="reel-wrap">
                    <div class="reel">{current[0]}</div>
                    <div class="reel">{current[1]}</div>
                    <div class="reel">{current[2]}</div>
                </div>
            </div>
            ''',
            unsafe_allow_html=True,
        )
        time.sleep(0.08 if frame < 10 else 0.12)

    st.session_state.reels = final_reels
    st.session_state.status = outcome["message"]
    st.session_state.status_tone = outcome["tone"]


def reset_game():
    for key in ["reels", "status", "status_tone"]:
        if key in st.session_state:
            del st.session_state[key]
    init_state()


status_class = "status-positive" if st.session_state.status_tone == "positive" else "status-neutral"

st.markdown(
    """
    <div class="page-shell">
    <div class="hero">
        <div class="big-title">Inverse Cancel Casino</div>
        <div class="tiny-brand">vibe coded by ac-team</div>
    </div>
    """,
    unsafe_allow_html=True,
)

left, center, right = st.columns([1, 2, 1])

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

    st.button("🎰 Spin the machine", use_container_width=True, on_click=spin_machine)

st.markdown('<div class="footer-note">AC-team experimental casino interface</div></div>', unsafe_allow_html=True)
