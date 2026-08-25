# Premier League Historical Analysis & Datasets (2010/11 – 2025/26)

A comprehensive data engineering and analysis project covering the last 16 English Premier League (EPL) seasons. This repository contains structured datasets for team performance, individual player statistics, advanced metrics (xG, xGA, PPDA, xPTS, Deep completions), transfer market activities, and managerial tenures, alongside an automated extraction pipeline.

> [!TIP]
> For a full mathematical breakdown, diagrams, and benchmarks of modern tactical metrics, refer to the **[Advanced Football Analytics Guide](ADVANCED_STATS_GUIDE.md)**.

---

## 📁 Repository Structure

```
liverpool analysis/
├── data/
│   ├── epl_team_season_stats.csv     # Team standings, match stats, advanced metrics (xG, PPDA, xPTS), transfer spend & managers
│   ├── epl_player_season_stats.csv   # Player appearances, goals, assists, xG, xA, npxG, key passes, shots, valuation
│   ├── epl_transfers.csv             # 10,000+ incoming/outgoing transfers with fees, dates & windows
│   └── epl_coaches_history.csv       # Manager appointments, departures, match records, PPG & win rates
├── scripts/
│   └── fetch_epl_data.py             # Reproducible data extraction and aggregation pipeline
├── ADVANCED_STATS_GUIDE.md           # Detailed guide to all advanced metrics (xG, PPDA, xPTS, xGChain)
├── .gitignore
└── README.md
```

---

## 🧠 Advanced Statistics Quick Reference

| Metric | Name | Definition & Tactical Meaning |
| :--- | :--- | :--- |
| **`xG` / `xGA`** | **Expected Goals (For / Against)** | Probability (0 to 1) that a shot results in a goal based on historical shot models (distance, angle, body part, assist type). |
| **`xGD`** | **Expected Goal Difference** | $xG - xGA$. The most robust indicator of true overall team performance. |
| **`npxG` / `npxGA`** | **Non-Penalty xG** | Expected goals excluding penalties (~0.76 xG), showing open-play and regular set-piece strength. |
| **`ppda`** | **Passes Per Defensive Action** | Quantifies pressing intensity in opponent's defensive 60% ($\frac{\text{Opponent Passes}}{\text{Defensive Actions}}$). **Lower value = more aggressive high pressing** (<8.5 = Elite Gegenpress). |
| **`ppda_allowed`** | **Opponent PPDA** | Opponent's PPDA against this team. Higher value = team breaks opponent press easily. |
| **`deep_completions`**| **Deep Zone Completions** | Passes completed within 20 yards of opponent goal (excluding crosses). Measures danger zone penetration. |
| **`xPTS`** | **Expected Points** | Simulated points earned based on the underlying xG profile of each match. |
| **`xA`** | **Expected Assists** | Chance creation quality; the xG of the shot that directly followed a player's pass. |
| **`xGChain`** | **xG Chain** | Total xG of every possession move the player touched the ball in. |
| **`xGBuildup`** | **xG Build-Up** | Total xG of sequences the player participated in **excluding** the shot itself and final pass (evaluating deep playmakers and defenders). |

*For deep dive explanations and tactical case studies, see [ADVANCED_STATS_GUIDE.md](ADVANCED_STATS_GUIDE.md).*

---

## 🌐 Data Sources

1. **[Understat](https://understat.com/) (Opta-based Expected Metrics)**: Team and player advanced metrics from 2014/15 through 2025/26.
2. **[Football-Data.co.uk](https://www.football-data.co.uk/)**: Match results, scores, shots, shots on target, corners, fouls, and disciplinary cards across 16 seasons (2010/11 through 2025/26).
3. **[Transfermarkt](https://www.transfermarkt.com/)**: Complete player market valuations, transfer records with fees in Euros (€), and managerial match-by-match histories.

---

## 📊 Dataset Schemas

### 1. Team Season Performance (`data/epl_team_season_stats.csv`)
- **Rows**: 320 (20 teams × 16 seasons from 2010/11 to 2025/26)
- **Columns (44)**:
  - `season`: Season label (`2025-2026`, `2024-2025`, `2023-2024`, etc.)
  - `season_year`: Season start year (`2025`, `2024`, etc.)
  - `league_rank`: Final league position (1 to 20)
  - `team_name`: Normalized club name (e.g. `Liverpool`, `Manchester City`, `Arsenal`)
  - `matches_played`, `wins`, `draws`, `losses`, `goals_for`, `goals_against`, `goal_difference`, `points`
  - **Advanced Metrics**: `xG`, `xGA`, `xGD`, `npxG`, `npxGA`, `npxGD`, `ppda`, `ppda_allowed`, `deep_completions`, `deep_allowed`, `xPTS`
  - `home_wins`, `home_draws`, `home_losses`, `home_goals_for`, `home_goals_against`
  - `away_wins`, `away_draws`, `away_losses`, `away_goals_for`, `away_goals_against`
  - `clean_sheets`, `total_shots`, `total_shots_on_target`, `corners`, `fouls_committed`, `yellow_cards`, `red_cards`
  - `managers_in_charge`: Head coaches during the season
  - `total_transfer_spend_eur`, `total_transfer_income_eur`, `net_transfer_spend_eur`: Financial balance

---

### 2. Player Seasonal Performance (`data/epl_player_season_stats.csv`)
- **Rows**: 7,425 player-season records
- **Columns**: `player_id`, `player_name`, `season`, `season_year`, `club_name`, `position`, `sub_position`, `country_of_citizenship`, `date_of_birth`, `age_in_season`, `appearances`, `minutes_played`, `goals`, `assists`, `goals_per_90`, `assists_per_90`, `goal_contributions_per_90`, **`xG`**, **`npxG`**, **`xA`**, **`shots`**, **`key_passes`**, **`xGChain`**, **`xGBuildup`**, `yellow_cards`, `red_cards`, `market_value_eur`, `highest_market_value_eur`.

---

### 3. Premier League Transfers (`data/epl_transfers.csv`)
- **Rows**: 10,311 transfer records (2010–2026)
- **Columns**: `player_name`, `player_id`, `season`, `season_year`, `transfer_date`, `transfer_window`, `pl_club_involved`, `transfer_direction` (`In`/`Out`), `from_club_name`, `to_club_name`, `transfer_fee_eur`, `market_value_eur`, `transfer_type`.

---

### 4. Coaches & Managerial Tenures (`data/epl_coaches_history.csv`)
- **Rows**: 430 managerial tenure records
- **Columns**: `coach_name`, `club_name`, `season`, `season_year`, `appointed_first_match`, `departed_last_match`, `tenure_status`, `matches_managed`, `wins`, `draws`, `losses`, `points`, `points_per_game`, `win_percentage`, `goals_for`, `goals_against`, `goal_difference`.

---

## 🚀 Running the Pipeline

```bash
# Checkout the branch
git checkout getting_data

# Run the automated pipeline
python3 scripts/fetch_epl_data.py
```
