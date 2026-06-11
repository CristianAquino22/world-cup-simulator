import pandas as pd
import random
import itertools
import numpy as np
from collections import defaultdict

from simulator import (
    simulate_match, simulate_knockout_match, MatchResult,  home_field_a, compute_xg, estimate_outcome_probabilities, sample_scoreline)

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


    
print("--- SIMULATING 2026 WORLD CUP GROUP STAGE... \n")

def get_hfa(team_a, team_b):
    a_is_host = team_a in hosts
    b_is_host = team_b in hosts

    if a_is_host and b_is_host:
        return 0.0
    elif a_is_host:
        return home_field_a
    elif b_is_host:
        return - home_field_a
    else:
        return 0.0


#initializes group standings dictionary
def make_standings(teams):
    return {
        team: {
            'pts': 0, 'gf':0, 'ga':0, 'gd': 0,
            'w':0, 'd':0, 'l': 0,
            'elo': elo_dict.get(team),
        }
        for team in teams
    }

#Updates group standings based on result
def update_standings(standings, result = MatchResult):
    a, b = result.team_a , result.team_b
    ga, gb = result.goals_a, result. goals_b

    standings[a]['gf'] += ga;  standings[a]['ga'] += gb
    standings[b]['gf'] += gb;  standings[b]['ga'] += ga
    standings[a]['gd'] += (ga - gb)
    standings[b]['gd'] += (gb - ga)

    if ga > gb:
        standings[a]['pts'] += 3;  standings[a]['w'] += 1
        standings[b]['l'] += 1
    elif gb > ga:
        standings[b]['pts'] += 3;  standings[b]['w'] += 1
        standings[a]['l'] += 1
    else:
        standings[a]['pts'] += 1;  standings[a]['d'] += 1
        standings[b]['pts'] += 1;  standings[b]['d'] += 1

#Sorts standings by points, goal difference, then goals in favour, and finally by elo. 
def sort_standings(standings):
    return sorted(standings.items(),
                  key = lambda x: (
                      x[1]['pts'],
                      x[1]['gd'],
                      x[1]['gf'],
                      x[1]['elo'],
                  ),
                  reverse = True
                  )

#IMPORTANTTTT use of OFFICIAL FIFA ANNEX C WOOOHOOOOO
def load_annex_c():
    annex_c_table = {}
    headers = ['Group A', 'Group B', 'Group D', 'Group E', 'Group G', 'Group I', 'Group K', 'Group L']

    with open('data/raw/annex_c.txt', 'r') as file:
        lines = file.readlines()
    
    for line in lines:
        parts = line.strip().split()

        if not parts or parts[0] == 'Option':
            continue

        thirds = [p.replace('3', '') for p in parts[1:]] #extracts just the letters of 3rd place teams

        combo_key = ",".join(sorted(thirds))

        matchups = {headers[i]: thirds[i] for i in range(8)}
        annex_c_table[combo_key] = matchups

    return annex_c_table

annex_c = load_annex_c()


def assign_third_place_teams(advancing_thirds, annex_c):
    group_letters = sorted([t['group'].replace('Group ', '') for t in advancing_thirds])
    combo_key = ','.join(group_letters)
    try:
        matchup_rules = annex_c[combo_key]
    except KeyError:
        raise ValueError(
            f"Annex C combination '{combo_key}' not found. ")
    
    assigned = {}

    for winner_group_label, letter in matchup_rules.items():
        target_group = f'Group {letter}'
        for team_dict in advancing_thirds:
            if team_dict['group'].replace('Group ', '') == letter:
                assigned[winner_group_label] = team_dict['team']
                break
    
    return assigned

def simulate_group_match(team_a, team_b, hfa):
    ra = elo_dict.get(team_a)
    rb = elo_dict.get(team_b)
    xg_a, xg_b = compute_xg(ra, rb, hfa)
    xg_a, xg_b = compute_xg(ra, rb, hfa)
    prob_a_win, prob_draw, prob_b_win = estimate_outcome_probabilities(xg_a, xg_b)
    goals_a, goals_b = sample_scoreline(xg_a, xg_b)
 
    return MatchResult(
        team_a=team_a, team_b=team_b,
        goals_a=goals_a, goals_b=goals_b,
        prob_a_win=prob_a_win,
        prob_draw=prob_draw,
        prob_b_win=prob_b_win,
    )
 


#Simulates all groups, returning group winners, group runners up, and the third place pool
def simulate_group_stage():
    group_winners = {}
    group_runners_up = {}
    third_place_pool = []

    for letter, teams in groups_2026.items():
        clean_letter = letter.replace('Group ', '')
        standings = make_standings(teams)

        for team_a, team_b in itertools.combinations(teams, 2):
            hfa = get_hfa(team_a, team_b)
            result = simulate_group_match(team_a, team_b, hfa)
            update_standings(standings, result)
        
        sorted_group = sort_standings(standings)

        group_winners[clean_letter] = sorted_group[0][0]
        group_runners_up[clean_letter] = sorted_group[1][0]
        third_place_pool.append({
            'team': sorted_group[2][0],
            'pts' : sorted_group[2][1]['pts'],
            'gd' : sorted_group[2][1]['gd'],
            'gf' : sorted_group[2][1]['gf'],
            'elo' : sorted_group[2][1]['elo'],
            'group' : clean_letter,
        })
    
    return group_winners, group_runners_up, third_place_pool


def build_r32_bracket(gw, ru, thirds,):
    """
    Constructs the Round of 32 bracket using the official 2026 fixture list.
    gw = group winners, ru = runners-up, thirds = assigned third-place teams.
 
    The bracket is fixed. winner of match 1 plays winner of match 2, etc.
    """
    return [
        #R16 match 1 feed
        (gw['E'],  thirds.get('Group E')),
        (gw['I'],  thirds.get('Group I')),
        #R16 match 2 feed
        (ru['A'],  ru['B']),
        (gw['F'],  ru['C']),
        #R16 match 3 feed
        (gw['C'],  ru['F']),
        (ru['E'],  ru['I']),
        #R16 match 4 feed
        (gw['A'],  thirds.get('Group A')),
        (gw['L'],  thirds.get('Group L')),
        #R16 match 5 feed
        (ru['K'],  ru['L']),
        (gw['H'],  ru['J']),
        #R16 match 6 feed
        (gw['D'],  thirds.get('Group D')),
        (gw['G'],  thirds.get('Group G')),
        #R16 match 7 feed
        (gw['J'],  ru['H']),
        (ru['D'],  ru['G']),
        #R16 match 8 feed
        (gw['B'],  thirds.get('Group B')),
        (gw['K'],  thirds.get('Group K')),
    ]
 

def simulate_knockout_round(matchups, round, commentary = True):
    #Prints bracked decorations, turn it off when doing monte carlo 
    if commentary:
        print(f"\n {'-'*52}")
        print(f" {round}")
        print(f"  {'─'*52}")
    
    winners = []

    for team_a, team_b in matchups:

        hfa = get_hfa(team_a, team_b)

        ra = elo_dict[team_a]
        rb = elo_dict[team_b]

        result = simulate_knockout_match(team_a, team_b, elo_dict, neutral =(hfa ==0), team_a_is_home = (hfa > 0))

        if commentary:
            winner_marker = '🟢'
            loser  = team_b if result.winner == team_a else team_a
            print(
                f"  {team_a:22} vs {team_b:22} | "
                f"{winner_marker} {result.winner} ({result.scoreline})"
            )
 
        winners.append(result.winner)
    
    if len(winners) == 1:
        return winners
 
    #Pair winners in bracket order: [0,1] → match, [2,3] → match, etc.
    next_round = [
        (winners[i], winners[i + 1])
        for i in range(0, len(winners) - 1, 2)
    ]
    return next_round


def simulate_world_cup(commentary = True):
    if commentary:
        print("\n  ══════════════════════════════════════════════════")
        print("   2026 FIFA WORLD CUP SIMULATOR")
        print("  ══════════════════════════════════════════════════")
        print("\n  Simulating group stage...")
 
    #Group stage
    gw, ru, third_pool = simulate_group_stage()
 
    #Best 8 third-place teams advance
    third_pool.sort(key=lambda x: (x['pts'], x['gd'], x['gf'], x['elo']), reverse=True)
    advancing_thirds = third_pool[:8]
 
    if commentary:
        print("\n  Group winners:")
        for letter in sorted(gw):
            print(f"    Group {letter}: {gw[letter]}")
        print("\n  Third-place qualifiers:")
        for t in advancing_thirds:
            print(f"    Group {t['group']}: {t['team']}  ({t['pts']} pts, GD {t['gd']:+d})")

    #Annex C
    assigned_thirds = assign_third_place_teams(advancing_thirds, annex_c)
 
    #Bracket
    r32_matchups = build_r32_bracket(gw, ru, assigned_thirds)
    r16_matchups = simulate_knockout_round(r32_matchups, "ROUND OF 32", commentary)
    qf_matchups  = simulate_knockout_round(r16_matchups, "ROUND OF 16", commentary)
    sf_matchups  = simulate_knockout_round(qf_matchups,  "QUARTER-FINALS", commentary)
    f_matchups   = simulate_knockout_round(sf_matchups,  "SEMI-FINALS", commentary)
    final = simulate_knockout_round(f_matchups,  "WORLD CUP FINAL", commentary)
 
    #gets champion
    champion = final[0]
 
    if commentary:
        print(f"\n  ══════════════════════════════════════════════════")
        print(f"  🏆  2026 WORLD CUP CHAMPION: {champion.upper()}")
        print(f"  ══════════════════════════════════════════════════\n")
 
    r32_teams = [team for match in r32_matchups for team in match]
    r16_teams = [team for match in r16_matchups for team in match]
    qf_teams  = [team for match in qf_matchups  for team in match]
    sf_teams  = [team for match in sf_matchups  for team in match]
    f_teams   = [team for match in f_matchups   for team in match]

    #Return a complete snapshot dictionary of this tournament's history
    return {
        'R32': r32_teams,
        'R16': r16_teams,
        'QF':  qf_teams,
        'SF':  sf_teams,
        'F':   f_teams,
        'Champ': champion
    }

def run_monte_carlo(n = 1000, commentary = False):
    tracker = defaultdict(lambda: {'R32': 0, 'R16': 0, 'QF': 0, 'SF': 0, 'F': 0, 'Champ': 0}) #each team has a counter for how many times it goes to each round

    for i in range(n):
        comments = (i ==0 and commentary)
        try:
            history = simulate_world_cup(commentary= comments)
            for team in history['R32']: tracker[team]['R32'] += 1
            for team in history['R16']: tracker[team]['R16'] += 1
            for team in history['QF']:  tracker[team]['QF'] += 1
            for team in history['SF']:  tracker[team]['SF'] += 1
            for team in history['F']:   tracker[team]['F'] += 1

            tracker[history['Champ']]['Champ'] += 1


        except Exception as e:
            print(f"Simulation {i+1} failed: {e}")
            continue

        if (i+1) % 100 ==0:
            print(f"Completed {i+1}/{n} simulations...")

    rows = []
    for team, stats in tracker.items():
        rows.append({
            'Team': team,
            'Make_R32%': round(stats['R32'] / n * 100, 1),
            'Make_R16%': round(stats['R16'] / n * 100, 1),
            'Make_QF%':  round(stats['QF'] / n * 100, 1),
            'Make_SF%':  round(stats['SF'] / n * 100, 1),
            'Make_F%':   round(stats['F'] / n * 100, 1),
            'Win_WC%':   round(stats['Champ'] / n * 100, 1)
        })

    results = pd.DataFrame(rows).sort_values(by = 'Win_WC%', ascending = False)

    return results



if __name__ == '__main__':
    #Prints commentary for one world cup and simulates it
    #simulate_world_cup(commentary=True)

    #Monte Carlo — uncomment to run
    print("\nRunning Tiered Monte Carlo (10000 simulations)...")
    results = run_monte_carlo(n=10000, commentary=False)
    print("\n  World Cup probabilities:")
    print(results.head(48).to_string(index=False))
    results.to_csv('data/processed/mc_results.csv', index=False)
    print("\n  Full results saved to data/processed/mc_results.csv")