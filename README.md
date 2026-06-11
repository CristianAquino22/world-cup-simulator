# 2026 FIFA World Cup Monte Carlo Simulator

**By Cris — Computational Data Sciences, Penn State University (Expected May 2027)**

 **Live App:** https://world-cup-simulator-2026woowoo.streamlit.app/
📁 **Dataset:** https://www.kaggle.com/datasets/martj42/international-football-results-from-1872-to-2017/data

---

## Project Overview

This project simulates the entire 2026 FIFA World Cup,  48 teams, 12 groups, a 32-team knockout bracket, using a custom-built probability engine trained on over 21,300 international matches. Running 10,000 full tournament simulations produces championship probabilities, round-by-round advancement rates, and a live interactive bracket for every team in the field.

The interactive Streamlit dashboard lets users explore the full survival matrix across all 48 teams, simulate a live tournament in real time with a single button click, and run head-to-head match simulations between any two countries with scoreline probability distributions.

Football is inherently shaped by stochastic chance, a single lucky bounce or bad referee call can alter a country's entire trajectory. I built this project to look past media hype and gut feelings, using data to calculate the actual mathematical probabilities of how this expanded tournament could unfold.
---

## Motivation and Thought Process

I've followed football seriously for a long time. When the 2026 World Cup draw was announced, I was already thinking about which teams had real paths to the final and which were getting overhyped. I figured if I was going to have that argument anyway, I might as well build something that could back it up with numbers.

My initial plan was pretty modest. I wanted to assign Elo ratings to every team, plug them into a win probability formula, and run a simple bracket simulation. I had taken enough statistics to understand the basic mechanics (Elo is just a rating system that updates based on expected versus actual outcomes, and I'd seen it used in chess and sports contexts before. I hadn't applied it to football specifically, and I definitely hadn't heard of Dixon-Coles or thought seriously about modeling actual scorelines. That all came later.

The first sign that my original approach was too simple came early. After running the Elo engine for the first time on the historical dataset, I realized that some unexpected teams, such as Algeria and Haiti, where overperforming (according from my personal knowledge of football). My first reaction was that I had a bug. After checking the code, I realized the math was technically correct, they just played a lot of matches against weak opposition, won most of them, and accumulated Elo points the same way a team from Europe would. That was the problem. That result forced me to think more carefully about what Elo is actually measuring and what it isn't, and it led directly to the confederation weighting system that became one of the core features of the engine.

From there, the project kept expanding. Once I had proper Elo ratings, I realized that simulating matches as pure binary win/loss outcomes was throwing away real information. Football ends in draws about a quarter of the time. And beyond that, a 4-0 win tells you something fundamentally different about a team than a 1-0 win,as the basic Elo update treats them identically. So I started looking into how serious football models handle this, which is how I landed on Poisson goal modeling and eventually the Dixon-Coles correction.

The bracket logic turned out to be the hardest single piece of the project. The 2026 World Cup has 12 groups instead of the traditional 8, which means 12 third-place teams and only 8 spots in the Round of 32. FIFA uses an official placement table called Annex C to determine which third-place teams play which group winners, where the matchups depend on the exact combination of groups that produced the advancing third-place finishers. There are 495 unique possible combinations, each mapping to a different bracket configuration. Getting that logic right, parsing the Annex C file, and making sure every edge case produced a valid bracket took longer than I expected. When the full simulator finally ran end-to-end (all 12 groups, all 32 knockout matches, a champion at the end) that was the moment the project stopped feeling like an exercise and started feeling like something real.

---

## Dataset

I used a public Kaggle dataset of international football results covering official matches from 1872 to the present. After cleaning, my working dataset includes:

- All **official competitive matches from 1993 onwards** (World Cup qualifiers, continental tournaments, Nations Leagues)
- **Friendlies from 2023 onwards only**  recent enough to carry signal, old enough friendlies filtered out because they're largely meaningless for predicting tournament performance
- A total of approximately **21,300 matches** after filtering

**Key columns used:**
| Column | Description |
|---|---|
| `date` | Match date — used for chronological ordering and pre-2000 K-factor halving |
| `home_team` / `away_team` | Team names — mapped to confederation and Elo dictionary |
| `home_score` / `away_score` | Final score — used for result, goal difference, and MOV multiplier |
| `tournament` | Competition name — determines base K-factor |
| `neutral` | Boolean — True if played at a neutral venue, disables home field advantage |

**Preprocessing steps:**
- Removed rows with null scores (future fixtures in the raw file)
- Filtered by date using a hybrid rule: competitive matches from 1993+, friendlies from 2023+ only
- Sorted chronologically — critical for Elo to update in the correct order
- Mapped every team name to its confederation for the weighting system

**Dataset Link:** https://www.kaggle.com/datasets/martj42/international-football-results-from-1872-to-2017/data

---

## Exploratory Data Analysis

Before building the rating engine, I spent time understanding the shape of the data. A few things stood out.

Goal distributions in international football are lower-scoring than most people expect. The average goals per team per game in competitive matches sits around 1.15, which is noticeably lower than club football, where the equivalent figure is closer to 1.35. That difference matters for the score model and drove the `BASE_XG` parameter I calibrated for the Poisson engine.

Draw rates are substantial. Across all competitive international matches in the dataset, roughly 24–26% end level. Any match simulator that doesn't model draws is going to produce systematically wrong results, especially in tournament group stages where a draw is often the strategically sensible outcome.

The confederation imbalance is evident when you look at match volume. UEFA teams play far more competitive matches against other UEFA teams than, say, CONCACAF teams play against anyone. This imbalance is exactly why naive Elo inflates ratings for teams that farm weak opposition, they accumulate games and wins in a lower-quality pool without ever being stress-tested. Visualizing win rates by confederation made the case for confederation weighting much more concrete than the Haiti/Algeria anomaly alone.


---

## Feature Engineering and Modeling

The core of this project is a three-layer engine: an Elo rating system, a scoreline simulator, and a tournament bracket. Each layer feeds the next.

### Layer 1 — Elo Rating Engine

The base Elo update equation is:

```
R' = R + K_base × W_conf × M_mov × (S − E)
```

Where:
- **K_base** — tournament prestige weight (World Cup = 60, friendly = 13)
- **W_conf** — confederation strength multiplier (UEFA = 1.0, down to OFC = 0.70)
- **M_mov** — margin of victory multiplier using a log scale with autocorrelation correction
- **S** — actual result (1 for W, 0.5 for D, or 0 for L)
- **E** — expected result from the Elo probability formula

The confederation weights were the most important fix over a basic Elo system. Rather than adding or subtracting points based on opponent quality, I scale the K-factor itself. This means a win in a weak confederation earns less Elo — but critically, a loss there also costs less. The system is symmetric, which keeps the math clean.

The margin of victory multiplier uses the 538 formula: `ln(|GD| + 1) × (2.2 / (Δelo × 0.001 + 2.2))`. The second term is the autocorrelation correction — it reduces the reward when a heavy favorite wins big, since that's expected, and increases it when an underdog wins big. The multiplier is capped at 1.75 to prevent a single blowout from causing an unrealistic rating swing.

Home field advantage is set at +65 Elo points, applied only when `neutral = False` in the dataset. This is applied inside the expected score exponent, which means it has a larger effect in close matchups than in lopsided ones — a realistic property.

**One honest limitation:** I initialize every new team at 1500 regardless of their historical strength. A more rigorous approach would use tiered initialization or a burn-in period. The 1993 cutoff and the pre-2000 K-factor halving help, but teams that entered the dataset late start at an arbitrary baseline before the engine has enough data to calibrate them.

### Layer 2 — Score Simulator (Dixon-Coles Poisson Model)

Rather than simulating just win/draw/loss, I model the actual scoreline. Each team's expected goals are derived from their Elo ratings:

```
xG_a = BASE_XG × exp((Elo_a + HFA − Elo_b) / 600)
xG_b = BASE_XG × exp((Elo_b − Elo_a − HFA) / 600)
```

Goals are then sampled from a Poisson distribution. The problem with a basic Poisson model is that it treats each team's goals as independent, which produces systematic errors at low scores, as it overpredicts 1-0 and 0-1 results and underpredicts 0-0 and 1-1 draws. The Dixon-Coles correction applies a small multiplicative adjustment (ρ = −0.11) to those four scorelines specifically, which brings the distribution much closer to what you actually observe in international football.

Win, draw, and loss probabilities are estimated by running 50,000 Poisson samples and measuring the resulting distribution. This is more accurate than analytical calculation because it naturally incorporates the Dixon-Coles correction without requiring closed-form math.

### Layer 3 — Tournament Simulator

The group stage runs all 6 matches per group using `itertools.combinations`, tracks points, goal difference, and goals scored for each team, and sorts standings using FIFA's official tiebreaker rules. The 8 best third-place finishers advance using the Annex C placement table parsed from the official FIFA document.

Knockout matches that finish level go to extra time (25% of 90-minute xG, approximating 30 minutes of tired football) and then penalties if still tied. The penalty model gives the higher-rated team a small edge — ±5% per 200 Elo points, capped at ±10% — since penalties have a real skill component but are largely a lottery.

---

## Application and Deployment

I chose to turn the Python engine into a web app using Streamlit because I wanted a clean, interactive interface that could mask the complex computations running in the background.

To build the application efficiently, I used an AI assistant to help build the initial scaffolding and core code structure of the app. Getting a baseline layout generated saved me from getting bogged down in boilerplate interface code.

Once the structural skeleton was set, I focused on customization. I curated and included the visual information based entirely on what I considered most useful and actionable for someone using the tool. This included:

**Survival Matrix** — A full 48-team table showing each team's probability of reaching every round, from the Round of 32 through to winning the tournament. The table is heat-mapped so you can scan it in a few seconds without reading individual numbers.

**Tournament Simulator** — A single button that runs a complete 2026 World Cup simulation live. It outputs every knockout round as a matchup list with the winner and their advancement probability, so you can see the exact path to the champion in that particular timeline.

**Head-to-Head Match Simulator** — Select any two teams from the full database, run 10,000 simulations of that specific match, and see win probabilities, expected goals, and a ranked distribution of the most likely scorelines.


**Streamlit App:** https://world-cup-simulator-2026woowoo.streamlit.app/

---

## Key Takeaways

**What I got better at:** Building modular Python systems where each component has a clean interface. The three-engine architecture — Elo, match simulator, tournament simulator — made debugging significantly easier than if I had written it as one large script. When something broke, I could isolate which layer the problem was in.

**What I'd improve with more time:** The biggest gap is roster awareness. Right now, a qualification match played without a team's best players gets the same weight as a full-strength fixture. Incorporating injury and squad data would require a more complex data pipeline, but it would meaningfully improve accuracy for near-term predictions. I'd also want to run a proper calibration pass — comparing my pre-tournament probabilities against historical World Cup odds to quantify the model's accuracy rather than just eyeballing whether the output looks reasonable.

**What I learned about building data projects:** The first working version of something is rarely the right version. My initial Elo engine ran correctly and still produced wrong answers because it was missing important context about what the numbers meant. That's a lesson I'll carry into every project after this. Correctness and validity aren't the same thing, and you have to look at the output critically before trusting it.


---

## Tech Stack

| Category | Tools |
|---|---|
| **Core language** | Python 3.11 |
| **Data manipulation** | pandas, numpy |
| **Simulation** | scipy (Poisson), math, random, itertools |
| **Rating engine** | Custom Elo implementation |
| **Score model** | Custom Dixon-Coles Poisson model |
| **Frontend** | Streamlit |

---

*Penn State University · Computational Data Sciences · Expected May 2027*
