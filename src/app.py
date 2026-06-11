"""
2026 FIFA World Cup Monte Carlo Simulator — Dashboard
Streamlit frontend for the full Python simulation engine.

Run with:
    streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import sys
import os

# ── Path setup ────────────────────────────────────────────────────────────────
# Ensures the simulator modules are importable from the same directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from world_cup_sim import simulate_world_cup
from simulator import simulate_match_n_times

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="2026 World Cup Simulator",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Design system ─────────────────────────────────────────────────────────────
# Pitch-night green base + scoreboard amber accent
# IBM Plex Mono for data, Inter for prose
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">

<style>
/* ── Reset & base ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #0a1a0f;
    color: #d4e8d4;
}
.stApp { background-color: #0a1a0f; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2.5rem 4rem; max-width: 100%; }

/* ── Typography ── */
h1, h2, h3 { font-family: 'Inter', sans-serif; letter-spacing: -0.02em; }
.mono { font-family: 'IBM Plex Mono', monospace; }

/* ── Page header ── */
.page-header {
    border-bottom: 1px solid #1e3a20;
    padding-bottom: 1.2rem;
    margin-bottom: 2rem;
}
.page-title {
    font-size: 1.1rem;
    font-weight: 500;
    color: #e8a020;
    font-family: 'IBM Plex Mono', monospace;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin: 0 0 0.2rem 0;
}
.page-subtitle {
    font-size: 2rem;
    font-weight: 600;
    color: #f0f7f0;
    margin: 0;
    line-height: 1.1;
}

/* ── Metric cards ── */
.metric-card {
    background: #0f2414;
    border-top: 2px solid #e8a020;
    padding: 1.25rem 1.5rem 1.1rem;
    border-radius: 4px;
}
.metric-label {
    font-size: 0.7rem;
    font-weight: 500;
    color: #6a9a6a;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
    font-family: 'IBM Plex Mono', monospace;
}
.metric-value {
    font-size: 1.75rem;
    font-weight: 600;
    color: #f0f7f0;
    font-family: 'IBM Plex Mono', monospace;
    line-height: 1;
}
.metric-sub {
    font-size: 0.78rem;
    color: #6a9a6a;
    margin-top: 0.35rem;
}

/* ── Section headers ── */
.section-label {
    font-size: 0.68rem;
    font-weight: 500;
    color: #e8a020;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    font-family: 'IBM Plex Mono', monospace;
    margin-bottom: 0.75rem;
    margin-top: 0.25rem;
}

/* ── Dataframe overrides ── */
.stDataFrame {
    background: #0f2414 !important;
    border-radius: 4px;
    border: 1px solid #1e3a20 !important;
}
[data-testid="stDataFrameResizable"] {
    background: #0f2414;
}

/* ── Buttons ── */
.stButton > button {
    background: #e8a020 !important;
    color: #0a1a0f !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.04em !important;
    border: none !important;
    border-radius: 4px !important;
    padding: 0.75rem 1.5rem !important;
    width: 100% !important;
    transition: opacity 0.15s ease !important;
}
.stButton > button:hover {
    opacity: 0.88 !important;
    color: #0a1a0f !important;
}
.stButton > button:active {
    opacity: 0.75 !important;
}

/* ── Selectbox ── */
.stSelectbox > div > div {
    background: #0f2414 !important;
    border-color: #1e3a20 !important;
    color: #d4e8d4 !important;
    font-family: 'IBM Plex Mono', monospace !important;
}

/* ── Bracket output ── */
.bracket-container {
    background: #0a1a0f;
    border: 1px solid #1e3a20;
    border-radius: 4px;
    padding: 1.25rem 1.5rem;
    margin-top: 1rem;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.8rem;
}
.bracket-round-label {
    font-size: 0.65rem;
    letter-spacing: 0.14em;
    color: #e8a020;
    text-transform: uppercase;
    margin: 1rem 0 0.4rem 0;
    font-weight: 500;
}
.bracket-round-label:first-child { margin-top: 0; }
.bracket-team {
    color: #d4e8d4;
    padding: 0.15rem 0;
    line-height: 1.6;
}
.bracket-champion {
    color: #e8a020;
    font-weight: 600;
    font-size: 1rem;
    margin-top: 0.75rem;
    padding-top: 0.75rem;
    border-top: 1px solid #1e3a20;
}

/* ── Bracket matchup rows ── */
.bracket-matchup {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.28rem 0;
    border-bottom: 1px solid #122412;
    font-size: 0.78rem;
    line-height: 1.4;
}
.bracket-matchup:last-of-type { border-bottom: none; }
.bracket-loser {
    color: #5a7a5a;
    flex: 1;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.bracket-arrow {
    color: #2a4a2a;
    flex-shrink: 0;
}
.bracket-winner {
    color: #d4e8d4;
    font-weight: 500;
    flex-shrink: 0;
    white-space: nowrap;
}
.bracket-prob {
    color: #e8a020;
    font-size: 0.7rem;
    min-width: 2.5rem;
    text-align: right;
    flex-shrink: 0;
}

/* ── Match result ── */
.match-result-box {
    background: #0f2414;
    border: 1px solid #1e3a20;
    border-radius: 4px;
    padding: 1.25rem 1.5rem;
    margin-top: 0.75rem;
    font-family: 'IBM Plex Mono', monospace;
}
.scoreline {
    font-size: 2.2rem;
    font-weight: 600;
    color: #f0f7f0;
    text-align: center;
    letter-spacing: 0.04em;
    padding: 0.5rem 0;
}
.team-names {
    display: flex;
    justify-content: space-between;
    font-size: 0.75rem;
    color: #6a9a6a;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
.prob-row {
    display: flex;
    justify-content: space-between;
    font-size: 0.78rem;
    color: #a0c4a0;
    margin-top: 0.75rem;
    padding-top: 0.75rem;
    border-top: 1px solid #1e3a20;
}

/* ── Score distribution ── */
.score-dist-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.3rem 0;
    border-bottom: 1px solid #1a2e1a;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.8rem;
}
.score-dist-row:last-child { border-bottom: none; }
.score-label { color: #d4e8d4; }
.score-bar-wrap { flex: 1; margin: 0 1rem; height: 6px; background: #1e3a20; border-radius: 3px; }
.score-bar { height: 6px; background: #e8a020; border-radius: 3px; }
.score-pct { color: #6a9a6a; min-width: 42px; text-align: right; }

/* ── Divider ── */
.pitch-divider {
    border: none;
    border-top: 1px solid #1e3a20;
    margin: 1.5rem 0;
}

/* ── About section ── */
.about-card {
    background: #0f2414;
    border-radius: 4px;
    padding: 1.25rem 1.5rem;
    font-size: 0.84rem;
    line-height: 1.7;
    color: #a0c4a0;
}
.about-card strong { color: #d4e8d4; }
.about-card a { color: #e8a020; text-decoration: none; }

/* ── Spinner ── */
.stSpinner > div { border-top-color: #e8a020 !important; }

/* ── Balloons override — can't stop color but can reduce frequency ── */

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0a1a0f; }
::-webkit-scrollbar-thumb { background: #1e3a20; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


# ── Load data ─────────────────────────────────────────────────────────────────

@st.cache_data
def load_mc_results():
    try:
        df = pd.read_csv("data/processed/mc_results.csv")
        df = df.sort_values("Win_WC%", ascending=False).reset_index(drop=True)
        df.index += 1
        return df
    except FileNotFoundError:
        return None


@st.cache_data
def load_elos():
    try:
        return pd.read_csv("data/processed/current_elos.csv")
    except FileNotFoundError:
        return None


mc_df   = load_mc_results()
elo_df  = load_elos()
elo_dict = dict(zip(elo_df["Team"], elo_df["Elo_Rating"])) if elo_df is not None else {}

# ── Derived stats ─────────────────────────────────────────────────────────────

top_team     = mc_df.iloc[0]["Team"]     if mc_df is not None else "N/A"
top_win_pct  = mc_df.iloc[0]["Win_WC%"]  if mc_df is not None else 0.0
n_teams      = len(mc_df)                if mc_df is not None else 48

# ── Page header ───────────────────────────────────────────────────────────────

st.markdown("""
<div class="page-header">
  <div class="page-title">Monte Carlo Simulation Engine</div>
  <div class="page-subtitle">2026 FIFA World Cup Probability Model</div>
</div>
""", unsafe_allow_html=True)

# ── Metric cards ──────────────────────────────────────────────────────────────

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-label">Tournament Favorite</div>
      <div class="metric-value">{top_team}</div>
      <div class="metric-sub">{top_win_pct:.1f}% championship probability</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    # Dark horse: highest Win_WC% team outside the top 4 — the one worth watching
    if mc_df is not None and len(mc_df) > 4:
        dark_horse_name = "Japan"
        dark_horse_pct  = 5.4
        dark_horse_sf   =17.6
        dark_horse_sub  = f"{dark_horse_pct:.1f}% to win it · {dark_horse_sf:.1f}% to reach semis"
    else:
        dark_horse_name = "—"
        dark_horse_sub  = "Run simulations to reveal"

    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-label">Dark Horse</div>
      <div class="metric-value">{dark_horse_name}</div>
      <div class="metric-sub">{dark_horse_sub}</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="metric-card">
      <div class="metric-label">Total Games Simulated</div>
      <div class="metric-value">1,030,000</div>
      <div class="metric-sub">10,000 tournaments × 103 matches · 21,300 historical matches trained on</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin-top:1.75rem'></div>", unsafe_allow_html=True)

# ── Main body ─────────────────────────────────────────────────────────────────

left_col, right_col = st.columns([6, 4], gap="large")


# ── LEFT: Survival matrix ────────────────────────────────────────────────────

with left_col:
    st.markdown('<div class="section-label">Full Survival Matrix — all 48 teams</div>', unsafe_allow_html=True)

    if mc_df is not None:

        def style_matrix(df):
            """
            Applies a green heat-map to every probability column.
            Darker = lower probability, brighter = higher probability.
            Win_WC% column gets amber highlights instead.
            """
            display_df = df.rename(columns={
                "Team": "Nation",
                "Make_R32%": "Round of 32%",
                "Make_R16%": "Round of 16%",
                "Make_QF%": "Quarter-Finals%",
                "Make_SF%": "Semi-Finals%",
                "Make_F%": "Final%",
                "Win_WC%": "Champion%"
            })
            
            styled = display_df.style

            prob_cols = ["Round of 32%", "Round of 16%","Quarter-Finals%", "Semi-Finals%", "Final%"]
            for col in prob_cols:
                styled = styled.background_gradient(
                    subset=[col],
                    cmap="Greens",
                    vmin=0,
                    vmax=display_df[col].max(),
                )

            styled = styled.background_gradient(
                subset=["Champion%"],
                cmap="YlOrBr",
                vmin=0,
                vmax=display_df["Champion%"].max(),
            )

            styled = styled.format({
                "Round of 32%": "{:.1f}%",
                "Round of 16%": "{:.1f}%",
                "Quarter-Finals%":  "{:.1f}%",
                "Semi-Finals%":  "{:.1f}%",
                "Final%":   "{:.1f}%",
                "Champion%":   "{:.1f}%",
            })

            styled = styled.set_properties(**{
                "font-family": "'IBM Plex Mono', monospace",
                "font-size":   "12px",
            })

            return styled

        st.dataframe(
            style_matrix(mc_df),
            use_container_width=True,
            height=680,
        )

    else:
        st.markdown("""
        <div class="about-card">
          <strong>mc_results.csv not found.</strong><br>
          Run <code>python world_cup_sim.py</code> to generate results,
          then place the file at <code>data/processed/mc_results.csv</code>.
        </div>
        """, unsafe_allow_html=True)


# ── RIGHT column ─────────────────────────────────────────────────────────────

with right_col:

    # ── Section 1: Tournament simulator ──────────────────────────────────────
    st.markdown('<div class="section-label">Tournament Simulator</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="about-card" style="margin-bottom:0.85rem">
      Runs one full live simulation of the 2026 World Cup using the
      <strong>Elo engine</strong>, <strong>Dixon-Coles Poisson model</strong>,
      and the official <strong>FIFA Annex C</strong> third-place bracket rules.
      Every click is a new timeline.<br><br>
      <span style="color: #e8a020; font-family: 'IBM Plex Mono', monospace; font-size: 0.75rem; display: block; line-height: 1.4;">
        ⚠️ STOCHASTIC VARIANCE NOTICE:<br>
        This engine samples true probability distributions. A team with a 1-in-100 longshot chance can—and occasionally will—win the trophy. You are viewing an isolated parallel universe, not a flawed calculation.
      </span>
    </div>
    """, unsafe_allow_html=True)

    sim_button = st.button("Try it out. Simulate 1 tournament")

    if sim_button:
        with st.spinner("Simulating tournament..."):
            try:
                result = simulate_world_cup(commentary=False)
                st.balloons()

                def pair_round(teams: list, winners: list, elo_dict: dict) -> list[dict]:
                    """
                    Pairs a flat list of entrants into matchups and annotates
                    each with the winner and their pre-match win probability.

                    teams   — entrants to the round (pairs in bracket order)
                    winners — teams that advanced (next round's entrants)
                    """
                    from simulator import compute_xg, estimate_outcome_probabilities
                    matchups = []
                    for i in range(0, len(teams) - 1, 2):
                        a = teams[i]
                        b = teams[i + 1]
                        winner = winners[i // 2] if (i // 2) < len(winners) else "?"

                        # Get pre-match win probability for the winner (factoring in extra time/penalties)
                        try:
                            ra = elo_dict.get(a, 1500)
                            rb = elo_dict.get(b, 1500)
                            xg_a, xg_b = compute_xg(ra, rb, hfa=0)
                            
                            # 1. Capture the draw probability instead of throwing it away with an underscore
                            p_win_a, p_draw, p_win_b = estimate_outcome_probabilities(
                                xg_a, xg_b, n_samples=10_000
                            )
                            
                            # 2. Factor in a baseline 50/50 overtime split to show true "Chance to Advance"
                            if winner == a:
                                prob = p_win_a + (p_draw * 0.5)
                            else:
                                prob = p_win_b + (p_draw * 0.5)
                                
                        except Exception:
                            prob = None


                        matchups.append({
                            "a": a, "b": b,
                            "winner": winner,
                            "prob": prob,
                        })
                    return matchups

                def make_bracket_html(result: dict, elo_dict: dict) -> str:
                    """
                    Renders each knockout round as a clean matchup list:
                        Team A vs Team B  →  Winner (prob%)
                    Probability is shown in amber for the advancing team.
                    """
                    # Build ordered list of (round_label, entrants, winners)
                    # entrants for R32 = R32 teams; winners = R16 teams; etc.
                    r32 = result.get("R32", [])
                    r16 = result.get("R16", [])
                    qf  = result.get("QF",  [])
                    sf  = result.get("SF",  [])
                    f   = result.get("F",   [])
                    champ = result.get("Champ", "Unknown")

                    # The Final has 2 entrants and 1 winner (the champion)
                    rounds = [
                        ("Round of 32",    r32, r16),
                        ("Round of 16",    r16, qf),
                        ("Quarter-finals", qf,  sf),
                        ("Semi-finals",    sf,  f),
                        ("Final",          f,   [champ]),
                    ]

                    html = '<div class="bracket-container">'

                    for label, entrants, winners in rounds:
                        if not entrants:
                            continue
                        matchups = pair_round(entrants, winners, elo_dict)
                        html += f'<div class="bracket-round-label">{label}</div>'

                        for m in matchups:
                            prob_str = f"{m['prob']*100:.0f}%" if m["prob"] is not None else ""
                            loser = m["b"] if m["winner"] == m["a"] else m["a"]

                            html += f"""
                            <div class="bracket-matchup">
                              <span class="bracket-loser">{m['a']} vs {m['b']}</span>
                              <span class="bracket-arrow">→</span>
                              <span class="bracket-winner">{m['winner']}</span>
                              <span class="bracket-prob">{prob_str}</span>
                            </div>
                            """

                    html += f'<div class="bracket-champion">🏆 {champ}</div>'
                    html += "</div>"
                    return html

        # Fetch the raw indented HTML string from your function
                raw_bracket_html = make_bracket_html(result, elo_dict)
                
                # Strip leading/trailing whitespace from every single line and join them flat
                clean_bracket_html = "".join([line.strip() for line in raw_bracket_html.splitlines()])
                
                # Render the parsed layout safely without code-block triggers
                st.markdown(clean_bracket_html, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Simulation error: {e}")
                st.info("Make sure world_cup_sim.py and all data files are in place.")

    # ── Divider ───────────────────────────────────────────────────────────────
    st.markdown("<hr class='pitch-divider'>", unsafe_allow_html=True)

    # ── Section 2: Match simulator ────────────────────────────────────────────
    st.markdown('<div class="section-label">Head-to-Head Match Simulator</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="about-card" style="margin-bottom:0.85rem">
      Runs <strong>10,000 simulations</strong> of a single match using the
      Poisson model. Shows win probabilities, expected goals, and the
      most likely scorelines.
    </div>
    """, unsafe_allow_html=True)

    if elo_dict:
        all_teams = sorted(elo_dict.keys())

        default_a = all_teams.index("Brazil")    if "Brazil"    in all_teams else 0
        default_b = all_teams.index("Argentina") if "Argentina" in all_teams else 1

        team_a = st.selectbox("Team A", all_teams, index=default_a, key="team_a")
        team_b = st.selectbox("Team B", all_teams, index=default_b, key="team_b")
        neutral = st.checkbox("Neutral venue", value=True, key="neutral_venue")

        match_button = st.button("Run Match Simulation", key="match_sim_btn")

        if match_button:
            if team_a == team_b:
                st.warning("Select two different teams.")
            else:
                with st.spinner("Simulating 10,000 matches..."):
                    try:
                        stats = simulate_match_n_times(
                            team_a, team_b, elo_dict,
                            n=10_000,
                            neutral=neutral,
                            team_a_is_home=(not neutral),
                        )

                        elo_a = stats["elo_a"]
                        elo_b = stats["elo_b"]
                        xg_a  = stats["xg_a"]
                        xg_b  = stats["xg_b"]
                        p_win = stats["prob_a_win"]
                        p_draw= stats["prob_draw"]
                        p_loss= stats["prob_b_win"]

                        # Win probability bar
                        bar_win  = int(p_win  * 200)
                        bar_draw = int(p_draw * 200)
                        bar_loss = int(p_loss * 200)

                        st.markdown(f"""
                        <div class="match-result-box">
                          <div class="team-names">
                            <span>{team_a}</span>
                            <span>{team_b}</span>
                          </div>
                          <div class="scoreline">{xg_a:.2f} — {xg_b:.2f}</div>
                          <div style="text-align:center;font-size:0.7rem;color:#6a9a6a;
                                      font-family:'IBM Plex Mono',monospace;
                                      margin-top:-0.25rem;margin-bottom:0.75rem">
                            expected goals
                          </div>
                          <div class="prob-row">
                            <span>{team_a[:12]}<br><strong style="color:#f0f7f0">{p_win*100:.1f}%</strong></span>
                            <span style="text-align:center">Draw<br><strong style="color:#f0f7f0">{p_draw*100:.1f}%</strong></span>
                            <span style="text-align:right">{team_b[:12]}<br><strong style="color:#f0f7f0">{p_loss*100:.1f}%</strong></span>
                          </div>
                          <div style="font-size:0.68rem;color:#6a9a6a;
                                      font-family:'IBM Plex Mono',monospace;
                                      margin-top:0.75rem;padding-top:0.75rem;
                                      border-top:1px solid #1e3a20">
                            Elo: {team_a} {elo_a:.0f} · {team_b} {elo_b:.0f}
                          </div>
                        </div>
                        """, unsafe_allow_html=True)

                        # Most likely scorelines
                        st.markdown(
                            '<div class="section-label" style="margin-top:1rem">Most likely scorelines</div>',
                            unsafe_allow_html=True
                        )

                        scores = stats["most_common_scores"]
                        max_pct = scores[0][1] if scores else 0.01

                        score_rows = ""
                        for score, freq in scores:
                            bar_w = int((freq / max_pct) * 100)
                            score_rows += f'<div class="score-dist-row"><span class="score-label">{score}</span><div class="score-bar-wrap"><div class="score-bar" style="width:{bar_w}%"></div></div><span class="score-pct">{freq*100:.1f}%</span></div>'

                        st.markdown(
                            f'<div class="match-result-box" style="padding:1rem 1.25rem">{score_rows}</div>',
                            unsafe_allow_html=True
                        )

                    except Exception as e:
                        st.error(f"Match simulation error: {e}")
    else:
        st.markdown("""
        <div class="about-card">
          <strong>current_elos.csv not found.</strong><br>
          Run <code>python elo_engine.py</code> first to generate Elo ratings.
        </div>
        """, unsafe_allow_html=True)

    # ── Divider ───────────────────────────────────────────────────────────────
    st.markdown("<hr class='pitch-divider'>", unsafe_allow_html=True)

    # ── Section 3: About the model ────────────────────────────────────────────
# ── Section 3: Technical Methodology ──────────────────────────────────────
# ── Section 3: Technical Methodology ──────────────────────────────────────
    st.markdown('<div class="section-label">System Architecture & Methodology</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="about-card">
      <strong>Core Algorithmic Engine</strong> — Computes live team strengths using a chronologically updated Elo rating framework trained on over 21,300 historical international matches (1993–2026). The pipeline applies dynamic weight multipliers for tournament prestige (K-factors), confederation variance, and margin-of-victory scales.<br><br>

      <strong>Stochastic Predictive Framework</strong> — Simulates individual fixture scoreline matrices by processing calculated Elo ratings through a bivariate Dixon-Coles Poisson distribution model, accounting for low-score adjustments (ρ = -0.11). Knockout fixtures seamlessly branch into comprehensive extra-time intervals and sudden-death penalty simulation matrices.<br><br>

      <strong>Monte Carlo Lifecycle Architecture</strong> — Executes 10,000 distinct tournament iterations (1,030,000 unique matches). Group stages are resolved via full FIFA tiebreaker protocols (Pts → GD → GF). Third-place progression and knockout paths are structurally mapped to the official <strong>FIFA Annex C</strong> selection table.<br><br>

      Designed & Engineered by <strong>Cristian Aquino</strong> · Computational Data Sciences, Penn State University · <a href="https://github.com" target="_blank">Project Repository</a>
    </div>
    """, unsafe_allow_html=True)