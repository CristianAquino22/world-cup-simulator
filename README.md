#  2026 FIFA World Cup Monte Carlo Simulator

A production-grade predictive analytics terminal built to simulate the complete lifecycle of the 2026 World Cup across 10,000 algorithmic parallel universes.

##  System Architecture & Methodology

* **Core Elo Engine:** Trained on over 21,300 historical international matches (1993–2026), updating team strengths chronologically using dynamic weight multipliers for tournament prestige (K-factors), confederation variance, and margin-of-victory scales.
* **Stochastic Predictor:** Fixture scoreline matrices are sampled from a bivariate Dixon-Coles Poisson distribution model, accounting for low-score adjustments ($\rho = -0.11$). Knockout trees branch into comprehensive extra-time intervals and sudden-death penalty matrices.
* **Monte Carlo Lifecycle Simulator:** Executes 10,000 full tournament iterations (1,030,000 matches). Resolves group stages via full FIFA tiebreaker protocols (Pts → GD → GF) and structures knockout paths using official FIFA Annex C rules.

##  Tech Stack
* **Language:** Python 3
* **Analytics & Data Processing:** Pandas, Math
* **User Interface:** Streamlit Cloud Architecture

---
Built by **Cristian Aquino** · Computational Data Sciences, Penn State University
