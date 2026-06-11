# --- QUICK AUDIT: IS GROUP C BROKEN OR JUST LUCKY? ---
print("\n🔍 DEBUGGING GROUP C DATA...")
group_c_teams = ['Brazil', 'Morocco', 'Haiti', 'Scotland']

for team in group_c_teams:
    print(f"{team:12} | Elo Rating: {elo_dict.get(team, 'NOT FOUND')}")

# Run Group C 10,000 times to see the true distribution
print("\n🔄 SIMULATING GROUP C 10,000 TIMES...")
last_place_counts = {team: 0 for team in group_c_teams}

for _ in range(10000):
    standings = {team: {'Points': 0, 'Elo': elo_dict[team]} for team in group_c_teams}
    for team_a, team_b in itertools.combinations(group_c_teams, 2):
        _, pts_a, _, pts_b = simulate_group_match(team_a, team_b)
        standings[team_a]['Points'] += pts_a
        standings[team_b]['Points'] += pts_b
        
    sorted_group = sorted(standings.items(), key=lambda x: (x[1]['Points'], x[1]['Elo']), reverse=True)
    last_place_team = sorted_group[-1][0]
    last_place_counts[last_place_team] += 1

print("\n📊 Percentage of times finishing LAST in Group C:")
for team, count in last_place_counts.items():
    print(f"{team:12} | Last Place: {(count / 10000) * 100:.1f}%")