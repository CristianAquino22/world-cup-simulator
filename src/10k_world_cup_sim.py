import pandas as pd
import random
import itertools
import collections

#Load data
df = pd.read_csv('data/processed/current_elos.csv')
elo_dict = dict(zip(df['Team'], df['Elo_Rating']))
hosts = ['United States', 'Mexico', 'Canada']

#Official 2026 groups
groups_2026 = {
    'Group A': ['Mexico', 'South Africa', 'South Korea', 'Czech Republic'],
    'Group B': ['Canada', 'Bosnia and Herzegovina', 'Qatar', 'Switzerland'],
    'Group C': ['Brazil', 'Morocco', 'Haiti', 'Scotland'],
    'Group D': ['United States', 'Paraguay', 'Australia', 'Turkey'],
    'Group E': ['Germany', 'Curaçao', 'Ivory Coast', 'Ecuador'],
    'Group F': ['Netherlands', 'Japan', 'Sweden', 'Tunisia'],
    'Group G': ['Belgium', 'Egypt', 'Iran', 'New Zealand'],
    'Group H': ['Spain', 'Cape Verde', 'Saudi Arabia', 'Uruguay'],
    'Group I': ['France', 'Senegal', 'Iraq', 'Norway'],
    'Group J': ['Argentina', 'Algeria', 'Austria', 'Jordan'],
    'Group K': ['Portugal', 'DR Congo', 'Uzbekistan', 'Colombia'],
    'Group L': ['England', 'Croatia', 'Ghana', 'Panama']
}

def simulate_match(team_a, team_b, is_group_stage = True):
    rating_a = elo_dict[team_a]
    rating_b = elo_dict[team_b]

    hfa_a = 100 if team_a in hosts else 0
    hfa_b = 100 if team_b in hosts else 0
    hfa = hfa_a - hfa_b

    base_prob_a = 1 / (1 + 10 ** ((rating_b - (rating_a + hfa)) / 400))

    if is_group_stage:
        draw_prob = 0.30 * (1 - abs(base_prob_a - 0.5)*2)
        non_draw_prob = 1 - draw_prob
        win_prob_a = base_prob_a * non_draw_prob
        roll = random.random()
        if roll < win_prob_a:
            return team_a, 3, team_b, 0 #3 points for win
        elif roll < win_prob_a + draw_prob:
            return team_a, 1, team_b, 1 #1 points for draw
        else:
            return team_a, 0, team_b, 3 #0 points for loss
    else:
        roll = random.random()
        return (team_a, base_prob_a) if roll < base_prob_a else (team_b, 1 - base_prob_a)
    
def load_annex_c():
    annex_c_table = {}
    headers = ['Group A', 'Group B', 'Group D', 'Group E', 'Group G', 'Group I', 'Group K', 'Group L']
    with open('data/raw/annex_c.txt', 'r') as file:
        lines = file.readlines()
    for line in lines:
        parts = line.strip().split()
        if not parts or parts[0] == 'Option': continue
        thirds = [p.replace('3', '') for p in parts[1:]]
        combo_key = ",".join(sorted(thirds))
        matchups = {headers[i]: thirds[i] for i in range(8)}
        annex_c_table[combo_key] = matchups
    return annex_c_table

official_annex_c = load_annex_c()


def simulate_entire_world_cup():
    """Runs one full tournament silently and returns the champion."""
    group_winners = {}
    group_runners_up = {}
    third_place_pool = []

    # A. GROUP STAGE
    for group_name, teams in groups_2026.items():
        standings = {team: {'Points': 0, 'Elo': elo_dict[team]} for team in teams}
        for team_a, team_b in itertools.combinations(teams, 2):
            _, pts_a, _, pts_b = simulate_match(team_a, team_b, is_group_stage=True)
            standings[team_a]['Points'] += pts_a
            standings[team_b]['Points'] += pts_b
        
        sorted_group = sorted(standings.items(), key=lambda x: (x[1]['Points'], x[1]['Elo']), reverse=True)
        group_winners[group_name] = sorted_group[0][0]
        group_runners_up[group_name] = sorted_group[1][0]
        third_place_pool.append({'Team': sorted_group[2][0], 'Points': sorted_group[2][1]['Points'], 'Elo': sorted_group[2][1]['Elo'], 'Group': group_name})

    # B. 3RD PLACE ADVANCERS
    third_place_pool.sort(key=lambda x: (x['Points'], x['Elo']), reverse=True)
    advancing_thirds = third_place_pool[:8]

    # C. ANNEX C MATCHMAKING
    group_letters = sorted([t['Group'].replace('Group ', '') for t in advancing_thirds])
    combo_key = ",".join(group_letters)
    
    try:
        matchup_rules = official_annex_c[combo_key]
    except KeyError:
        print(f"CRITICAL ERROR: Combination '{combo_key}' not found in Annex C table!")
        exit()

    assigned_thirds = {}
    for winner_group, target_letter in matchup_rules.items():
        target_group = f"Group {target_letter}"
        for team_dict in advancing_thirds:
            if team_dict['Group'] == target_group:
                assigned_thirds[winner_group] = team_dict['Team']
                break

    # D. THE ROUND OF 32 BRACKET (Using your custom layout)
    matches_r32 = [
        (group_winners['Group E'], assigned_thirds['Group E']),
        (group_winners['Group I'], assigned_thirds['Group I']),
        (group_runners_up['Group A'], group_runners_up['Group B']),
        (group_winners['Group F'], group_runners_up['Group C']),
        (group_winners['Group C'], group_runners_up['Group F']),
        (group_runners_up['Group E'], group_runners_up['Group I']),
        (group_winners['Group A'], assigned_thirds['Group A']),
        (group_winners['Group L'], assigned_thirds['Group L']),
        (group_runners_up['Group K'], group_runners_up['Group L']),
        (group_winners['Group H'], group_runners_up['Group J']),
        (group_winners['Group D'], assigned_thirds['Group D']),
        (group_winners['Group G'], assigned_thirds['Group G']),
        (group_winners['Group J'], group_runners_up['Group H']),
        (group_runners_up['Group D'], group_runners_up['Group G']),
        (group_winners['Group B'], assigned_thirds['Group B']),
        (group_winners['Group K'], assigned_thirds['Group K']),
    ]

    # E. KNOCKOUT RESOLVER
    def run_silent_knockout(matchups):
        next_round = []
        for team_a, team_b in matchups:
            winner, _ = simulate_match(team_a, team_b, is_group_stage=False)
            next_round.append(winner)
        if len(next_round) > 1:
            return [(next_round[i], next_round[i+1]) for i in range(0, len(next_round), 2)]
        return next_round

    r16 = run_silent_knockout(matches_r32)
    qf = run_silent_knockout(r16)
    sf = run_silent_knockout(qf)
    final = run_silent_knockout(sf)
    champion = run_silent_knockout(final)
    
    return champion[0]


if __name__ == "__main__":
    print("\n🔄 Running 100,000 World Cup Simulations... (This will take a few seconds)")
    simulations_to_run = 100000
    champions = collections.Counter()

    for _ in range(simulations_to_run):
        winner = simulate_entire_world_cup()
        champions[winner] += 1

    print("\n --- PROBABILITY OF WINNING THE 2026 WORLD CUP...")
    for team, wins in champions.most_common(48):
        win_percentage = (wins / simulations_to_run) * 100
        print(f"{team:15} | {win_percentage:>5.1f}% chance ({wins} wins)")