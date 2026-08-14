"""
Walk-forward backtest of the Elo + Dixon-Coles match model.

Method
------
Elo is inherently sequential, so instead of a random train/test split we walk
forward through the match history in date order. For every match after the
cutoff we (1) predict win/draw/loss using ONLY the ratings as they stand at
kickoff, then (2) update the ratings with the actual result. The model never
sees a result before predicting it, so there is no look-ahead leakage.

Scoring
-------
Multi-class Brier score and log loss, compared against a base-rate baseline
(the historical home/draw/away frequencies computed on the training portion
only). The baseline ignores team identity entirely, so it is the floor any
real model must clear.

Usage
-----
Requires elo_engine.py to expose its constants/helpers on import. Wrap the
script body of elo_engine.py in `if __name__ == "__main__":` first.

    python backtest.py
"""

import numpy as np
import pandas as pd
from scipy.stats import poisson

from elo_engine import (
    CONFEDERATION_WEIGHTS,
    TEAM_CONFEDERATION,
    get_k_factor,
    margin_of_victory_multiplier,
)
from simulator import base_xg, xg_elo_scale, dixon_coles_rho, home_field_a

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

DATA_PATH = "data/processed/cleaned_matches.csv"
N_TEST = 2000        # number of most recent matches to hold out
MAX_GOALS = 10       # goal grid for the analytic Poisson calculation


# ---------------------------------------------------------------------------
# Analytic match probabilities (exact — no Monte Carlo noise)
# ---------------------------------------------------------------------------

def match_probabilities(xg_a, xg_b, rho=dixon_coles_rho, max_goals=MAX_GOALS):
    """
    Exact win/draw/loss probabilities under the Dixon-Coles bivariate Poisson.

    Builds the full scoreline probability matrix P(i, j) = Pois(i | xg_a) *
    Pois(j | xg_b), applies the Dixon-Coles multiplicative correction to the
    four low-scoring cells, renormalizes, then sums the relevant regions.

    Returns (p_a_win, p_draw, p_b_win).
    """
    goals = np.arange(max_goals + 1)
    pa = poisson.pmf(goals, xg_a)
    pb = poisson.pmf(goals, xg_b)

    matrix = np.outer(pa, pb)

    # Dixon-Coles low-score correction
    matrix[0, 0] *= 1 - xg_a * xg_b * rho
    matrix[1, 0] *= 1 + xg_b * rho
    matrix[0, 1] *= 1 + xg_a * rho
    matrix[1, 1] *= 1 - rho

    matrix /= matrix.sum()

    p_draw = np.trace(matrix)
    p_a_win = np.tril(matrix, -1).sum()   # rows > cols  -> a scored more
    p_b_win = np.triu(matrix, 1).sum()    # cols > rows  -> b scored more

    return p_a_win, p_draw, p_b_win


def expected_goals(rating_a, rating_b, hfa=0):
    """Same xG mapping as simulator.compute_xg."""
    xg_a = base_xg * np.exp((rating_a + hfa - rating_b) / xg_elo_scale)
    xg_b = base_xg * np.exp((rating_b - rating_a - hfa) / xg_elo_scale)
    return xg_a, xg_b


# ---------------------------------------------------------------------------
# Scoring functions
# ---------------------------------------------------------------------------

def brier_score(probs, outcomes):
    """
    Multi-class Brier score. probs is (n, 3), outcomes is (n, 3) one-hot.
    Range 0 (perfect) to 2 (maximally wrong). Lower is better.
    """
    return float(np.mean(np.sum((probs - outcomes) ** 2, axis=1)))


def log_loss(probs, outcomes, eps=1e-15):
    """Multi-class log loss. Lower is better."""
    clipped = np.clip(probs, eps, 1 - eps)
    return float(-np.mean(np.sum(outcomes * np.log(clipped), axis=1)))


# ---------------------------------------------------------------------------
# Walk-forward backtest
# ---------------------------------------------------------------------------

def run_backtest(data_path=DATA_PATH, n_test=N_TEST):
    df = pd.read_csv(data_path)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    cutoff_idx = len(df) - n_test
    if cutoff_idx <= 0:
        raise ValueError(f"n_test={n_test} exceeds dataset size {len(df)}")

    print(f"Total matches:    {len(df):,}")
    print(f"Training on:      {cutoff_idx:,} matches "
          f"({df.loc[0, 'date'].date()} to {df.loc[cutoff_idx - 1, 'date'].date()})")
    print(f"Testing on:       {n_test:,} matches "
          f"({df.loc[cutoff_idx, 'date'].date()} to {df.loc[len(df) - 1, 'date'].date()})")
    print()

    elo = {}
    train_outcomes = []          # for the base-rate baseline
    pred_probs = []
    actual_onehot = []

    for i, row in df.iterrows():
        home, away = row["home_team"], row["away_team"]
        home_score, away_score = row["home_score"], row["away_score"]
        goal_diff = home_score - away_score

        elo.setdefault(home, 1500)
        elo.setdefault(away, 1500)

        hfa = 0 if row["neutral"] else home_field_a

        # ---- outcome index: 0 = home win, 1 = draw, 2 = away win ----
        if goal_diff > 0:
            outcome = 0
        elif goal_diff == 0:
            outcome = 1
        else:
            outcome = 2

        # ---- PREDICT (test period only, before any update) ----
        if i >= cutoff_idx:
            xg_h, xg_a = expected_goals(elo[home], elo[away], hfa)
            p_home, p_draw, p_away = match_probabilities(xg_h, xg_a)

            pred_probs.append([p_home, p_draw, p_away])
            onehot = [0.0, 0.0, 0.0]
            onehot[outcome] = 1.0
            actual_onehot.append(onehot)
        else:
            train_outcomes.append(outcome)

        # ---- UPDATE ratings (both periods — this is the walk-forward part) ----
        k = get_k_factor(row["tournament"])
        if row["date"].year < 2000:
            k *= 0.5

        w_home = CONFEDERATION_WEIGHTS.get(TEAM_CONFEDERATION.get(home), 0.85)
        w_away = CONFEDERATION_WEIGHTS.get(TEAM_CONFEDERATION.get(away), 0.85)
        conf_weight = (w_home + w_away) / 2

        home_expected = 1 / (1 + 10 ** ((elo[away] - (elo[home] + hfa)) / 400))
        away_expected = 1 - home_expected

        if goal_diff > 0:
            elo_diff_at_kickoff = elo[home] - elo[away]
            home_result, away_result = 1.0, 0.0
        elif goal_diff < 0:
            elo_diff_at_kickoff = elo[away] - elo[home]
            home_result, away_result = 0.0, 1.0
        else:
            elo_diff_at_kickoff = 0
            home_result, away_result = 0.5, 0.5

        mov = margin_of_victory_multiplier(abs(goal_diff), elo_diff_at_kickoff)
        effective_k = k * conf_weight * mov

        elo[home] += effective_k * (home_result - home_expected)
        elo[away] += effective_k * (away_result - away_expected)

    pred_probs = np.array(pred_probs)
    actual_onehot = np.array(actual_onehot)

    # ---- baseline: training-set base rates, repeated for every test match ----
    train_outcomes = np.array(train_outcomes)
    base_rates = np.array([
        (train_outcomes == 0).mean(),
        (train_outcomes == 1).mean(),
        (train_outcomes == 2).mean(),
    ])
    baseline_probs = np.tile(base_rates, (len(pred_probs), 1))

    # ---- scores ----
    model_brier = brier_score(pred_probs, actual_onehot)
    base_brier = brier_score(baseline_probs, actual_onehot)
    model_ll = log_loss(pred_probs, actual_onehot)
    base_ll = log_loss(baseline_probs, actual_onehot)

    brier_improvement = (base_brier - model_brier) / base_brier * 100
    ll_improvement = (base_ll - model_ll) / base_ll * 100

    # ---- accuracy (argmax pick) ----
    model_acc = (pred_probs.argmax(axis=1) == actual_onehot.argmax(axis=1)).mean()
    base_acc = (baseline_probs.argmax(axis=1) == actual_onehot.argmax(axis=1)).mean()

    print(f"Base rates (train): home {base_rates[0]:.3f} | "
          f"draw {base_rates[1]:.3f} | away {base_rates[2]:.3f}")
    print()
    print(f"{'':<22}{'Model':>10}{'Baseline':>12}{'Improvement':>14}")
    print("-" * 58)
    print(f"{'Brier score':<22}{model_brier:>10.4f}{base_brier:>12.4f}{brier_improvement:>13.1f}%")
    print(f"{'Log loss':<22}{model_ll:>10.4f}{base_ll:>12.4f}{ll_improvement:>13.1f}%")
    print(f"{'Accuracy':<22}{model_acc:>10.1%}{base_acc:>12.1%}")
    print()
    print("Résumé line:")
    print(f"  validated on {len(pred_probs):,} held-out matches at a Brier score of "
          f"{model_brier:.3f} versus {base_brier:.3f} for a base-rate baseline "
          f"({brier_improvement:.0f}% improvement)")

    return {
        "n_test": len(pred_probs),
        "model_brier": model_brier,
        "baseline_brier": base_brier,
        "model_log_loss": model_ll,
        "baseline_log_loss": base_ll,
        "model_accuracy": float(model_acc),
    }


if __name__ == "__main__":
    run_backtest()