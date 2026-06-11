import pandas as pd
import numpy as np
from dataclasses import dataclass

home_field_a = 65 #sets HFA to 65, just as in elo engine

base_xg = 1.15 #average goals per team in international football

xg_elo_scale = 600 #around 40% xG boost for 200 elo gap

dixon_coles_rho = -0.11 #low score correlation correction

@dataclass
class MatchResult:
    team_a: str
    team_b: str
    goals_a: int
    goals_b: int
    prob_a_win: float
    prob_b_win: float
    prob_draw: float

    @property
    def winner(self):
        if self.goals_a > self.goals_b:
            return self.team_a
        elif self.goals_b > self.goals_a:
            return self.team_b
        else:
            return None
        
    @property

    def scoreline(self):
        return f"{self.goals_a} - {self.goals_b}"
    
    @property
    def result_label(self):
        if self.goals_a > self.goals_b:
            return f"{self.team_a} win"
        elif self.goals_b > self.goals_a:
            return f"{self.team_b} win"
        else:
            return "Draw"


def win_probability(rating_a, rating_b, hfa= 0):
    return 1 / (1 + 10 ** ((rating_b - (rating_a + hfa)) / 400))

def compute_xg(rating_a, rating_b, hfa = 0):
    #xG_a = BASE_XG × exp(( Elo_a + HFA - Elo_b) / XG_ELO_SCALE)
    #xG_b = BASE_XG × exp(( Elo_b         - Elo_a - HFA) / XG_ELO_SCALE)
    elo_diff_a = (rating_a + hfa - rating_b) / xg_elo_scale
    elo_diff_b =  (rating_b - rating_a - hfa) / xg_elo_scale

    xg_a = base_xg * np.exp(elo_diff_a)
    xg_b = base_xg * np.exp(elo_diff_b)

    return xg_a, xg_b

def dixon_coles(goals_a, goals_b, xg_a, xg_b, rho):
    ''' The raw Poisson model treats the two teams' goal counts as independent,
    which produces systematic errors at low scores. This function returns
    a multiplicative weight for the four affected scorelines:
 
        0-0: Poisson underestimates this (teams defend more carefully)
        1-1: Poisson underestimates this
        1-0: Poisson overestimates this
        0-1: Poisson overestimates this
        
    Dixon & Coles (1997), "Modelling Association Football Scores
    and Inefficiencies in the Football Betting Market"
    '''
    if goals_a == 0 and goals_b == 0:
        return 1 - xg_a * xg_b * rho
    elif goals_a == 1 and goals_b == 0:
        return 1 + xg_b * rho
    elif goals_a == 0 and goals_b == 1:
        return 1 + xg_a * rho
    elif goals_a == 1 and goals_b == 1:
        return 1 - rho
    else:
        return 1.0
    
def sample_scoreline(xg_a, xg_b, rho = dixon_coles_rho):
    while True:
        g_a = int(np.random.poisson(xg_a))
        g_b = int(np.random.poisson(xg_b))

        if g_a <= 1 and g_b <= 1:
            dc_weight = dixon_coles(g_a, g_b, xg_a, xg_b, rho)

            if np.random.random() < dc_weight / 1.1:
                return g_a, g_b
        
        else:
            return g_a, g_b
        

def estimate_outcome_probabilities(xg_a, xg_b, n_samples = 50000, rho = dixon_coles_rho):
    g_a = np.random.poisson(xg_a, n_samples).astype(int)
    g_b = np.random.poisson(xg_b, n_samples).astype(int)
    dc_weights = np.ones(n_samples)
    mask_00 = (g_a == 0) & (g_b == 0)
    mask_10 = (g_a == 1) & (g_b == 0)
    mask_01 = (g_a == 0) & (g_b == 1)
    mask_11 = (g_a == 1) & (g_b == 1)
    dc_weights[mask_00] = 1 - xg_a * xg_b * rho
    dc_weights[mask_10] = 1 + xg_b * rho
    dc_weights[mask_01] = 1 + xg_a * rho
    dc_weights[mask_11] = 1 - rho
 
    total_weight = dc_weights.sum()
    wins_a = dc_weights[g_a > g_b].sum() / total_weight
    draws  = dc_weights[g_a == g_b].sum() / total_weight
    wins_b = dc_weights[g_b > g_a].sum() / total_weight
 
    return float(wins_a), float(draws), float(wins_b)


def simulate_match(team_a, team_b, elo_dict, team_a_is_home = False, neutral = True):
    if team_a not in elo_dict:
        raise ValueError(f"Team not found in Elo database: '{team_a}'")
    if team_b not in elo_dict:
        raise ValueError(f"Team not found in Elo database: '{team_b}'")
 
    rating_a = elo_dict[team_a]
    rating_b = elo_dict[team_b]
 
    #HFA only applies when the match is NOT at a neutral venue
    hfa = 0
    if not neutral and team_a_is_home:
        hfa = home_field_a
 
    #Compute xG from Elo ratings
    xg_a, xg_b = compute_xg(rating_a, rating_b, hfa)
 
    #Estimate outcome probabilities
    prob_a_win, prob_draw, prob_b_win = estimate_outcome_probabilities(xg_a, xg_b)
 
    #Sample scoreline
    goals_a, goals_b = sample_scoreline(xg_a, xg_b)
 
    return MatchResult(
        team_a=team_a,
        team_b=team_b,
        goals_a=goals_a,
        goals_b=goals_b,
        prob_a_win=prob_a_win,
        prob_draw=prob_draw,
        prob_b_win=prob_b_win,
    )


def simulate_match_n_times(team_a, team_b, elo_dict, n = 10000, neutral = True, team_a_is_home = False):
    if team_a not in elo_dict:
        raise ValueError(f"Team not found in Elo database: '{team_a}'")
    if team_b not in elo_dict:
        raise ValueError(f"Team not found in Elo database: '{team_b}'")
 
    rating_a = elo_dict[team_a]
    rating_b = elo_dict[team_b]
    hfa = home_field_a if (not neutral and team_a_is_home) else 0
 
    xg_a, xg_b = compute_xg(rating_a, rating_b, hfa)
 
    #Estimate outcome probabilities once
    prob_a_win, prob_draw, prob_b_win = estimate_outcome_probabilities(xg_a, xg_b, n_samples=100000)
 
    #Simulate all N scorelines
    results = [sample_scoreline(xg_a, xg_b) for _ in range(n)]
 
    #Aggregate
    goals_a_arr = np.array([r[0] for r in results])
    goals_b_arr = np.array([r[1] for r in results])
 
    score_counts: dict[str, int] = {}
    for g_a, g_b in results:
        key = f"{g_a} - {g_b}"
        score_counts[key] = score_counts.get(key, 0) + 1
 
    top_scores = sorted(score_counts.items(), key=lambda x: x[1], reverse=True)[:8]
 
    return {
        "team_a":            team_a,
        "team_b":            team_b,
        "elo_a":             rating_a,
        "elo_b":             rating_b,
        "xg_a":              round(xg_a, 3),
        "xg_b":              round(xg_b, 3),
        "prob_a_win":        round(prob_a_win, 4),
        "prob_draw":         round(prob_draw, 4),
        "prob_b_win":        round(prob_b_win, 4),
        "avg_goals_a":       round(float(goals_a_arr.mean()), 2),
        "avg_goals_b":       round(float(goals_b_arr.mean()), 2),
        "most_common_scores": [(s, round(c / n, 4)) for s, c in top_scores],
        "all_results":       results,
    }
         
def simulate_knockout_match(team_a, team_b, elo_dict, neutral= True, team_a_is_home= False,):
    """
    Simulates a knockout match. If the score is level after 90 mins,
    adds extra time (slightly elevated scoring rate), then penalties if needed.
 
    Penalty shootout uses a 50/50 coin flip weighted by a small Elo factor
    (±5% max) to give better teams a marginal advantage from the spot.
 
    Returns a MatchResult where goals_a != goals_b always (there is a winner).
    The scoreline reflects 90-minute goals only for realism — the winner
    field reflects the full outcome including ET/penalties.
    """
    result = simulate_match(team_a, team_b, elo_dict, neutral, team_a_is_home)
 
    if result.goals_a != result.goals_b:
        return result  #90 minutes
 
    #Extra time: slightly elevated xG (fatigue + open play), ~0.3 goals per team
    rating_a = elo_dict[team_a]
    rating_b = elo_dict[team_b]
    hfa = home_field_a if (not neutral and team_a_is_home) else 0
    xg_a_et, xg_b_et = compute_xg(rating_a, rating_b, hfa)
 
    #Extra time xG scaled down to ~25% of 90-min (roughly 30 mins of play)
    et_a = int(np.random.poisson(xg_a_et * 0.25))
    et_b = int(np.random.poisson(xg_b_et * 0.25))
 
    total_a = result.goals_a + et_a
    total_b = result.goals_b + et_b
 
    if total_a != total_b:
        #ET winner — report 90-min score but correct winner
        return MatchResult(
            team_a=team_a, team_b=team_b,
            goals_a=total_a, goals_b=total_b,
            prob_a_win=result.prob_a_win,
            prob_draw=result.prob_draw,
            prob_b_win=result.prob_b_win,
        )
 
    #Penalty shootout: base 50/50 with small Elo skew
    elo_diff = rating_a - rating_b
    #±5% advantage for every 200 Elo points — capped at ±10%
    pen_advantage = np.clip(elo_diff / 4000, -0.10, 0.10)
    prob_a_wins_pens = 0.50 + pen_advantage
 
    if np.random.random() < prob_a_wins_pens:
        #Team A wins on penalties — represent as +1 goal for display purposes
        return MatchResult(
            team_a=team_a, team_b=team_b,
            goals_a=result.goals_a + 1, goals_b=result.goals_b,
            prob_a_win=result.prob_a_win,
            prob_draw=result.prob_draw,
            prob_b_win=result.prob_b_win,
        )
    else:
        return MatchResult(
            team_a=team_a, team_b=team_b,
            goals_a=result.goals_a, goals_b=result.goals_b + 1,
            prob_a_win=result.prob_a_win,
            prob_draw=result.prob_draw,
            prob_b_win=result.prob_b_win,
        )
 
 


if __name__ == "__main__":
    try:
        df = pd.read_csv("data/processed/current_elos.csv")
        elo_dict = dict(zip(df["Team"], df["Elo_Rating"]))
    except FileNotFoundError:
        print("Error: current_elos.csv not found. Run elo_engine.py first.")
        exit(1)
 
    # ── Single match test ────────────────────────────────────────────────────
    team_a = "Mexico"
    team_b = "South Africa"
    neutral = True
 
    print(f"\n{'─'*50}")
    print(f"  {team_a} vs {team_b}  {'(neutral)' if neutral else '(home: ' + team_a + ')'}")
    print(f"{'─'*50}")
 
    stats = simulate_match_n_times(team_a, team_b, elo_dict, n=50_000, neutral=neutral)
 
    print(f"\n  Elo:  {team_a} {stats['elo_a']:.0f}  |  {team_b} {stats['elo_b']:.0f}")
    print(f"  xG:   {team_a} {stats['xg_a']:.2f}  |  {team_b} {stats['xg_b']:.2f}")
    print(f"\n  Win probabilities:")
    print(f"    {team_a:<20} {stats['prob_a_win']*100:.1f}%")
    print(f"    Draw                 {stats['prob_draw']*100:.1f}%")
    print(f"    {team_b:<20} {stats['prob_b_win']*100:.1f}%")
    print(f"\n  Most likely scorelines (out of 50k simulations):")
    for score, freq in stats["most_common_scores"]:
        bar = "█" * int(freq * 200)
        print(f"    {score:<8} {freq*100:5.1f}%  {bar}")
 
    # ── Single draw ──────────────────────────────────────────────────────────
    print(f"\n  Sample result: ", end="")
    result = simulate_match(team_a, team_b, elo_dict, neutral=neutral)
    print(f"{result.team_a} {result.goals_a}–{result.goals_b} {result.team_b}  ({result.result_label})")
 
    # ── Knockout test ────────────────────────────────────────────────────────
    print(f"\n  Knockout simulation (ET/pens if needed):")
    ko_result = simulate_knockout_match(team_a, team_b, elo_dict, neutral=neutral)
    print(f"  {ko_result.team_a} {ko_result.goals_a}–{ko_result.goals_b} {ko_result.team_b}  →  Winner: {ko_result.winner}")
