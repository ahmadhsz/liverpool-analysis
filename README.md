# Premier League Historical Analysis & Datasets (2010/11 – 2025/26)

A comprehensive data engineering and analysis project covering the last 16 English Premier League (EPL) seasons. This repository contains structured datasets for team performance, individual player statistics, advanced metrics (xG, xGA, PPDA, xPTS, Deep completions), transfer market activities, and managerial tenures, alongside an automated extraction pipeline.

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
├── .gitignore
└── README.md
```

---

## 🌐 Data Sources & Methodology

1. **Football-Data.co.uk**: Match-by-match results, scores, shots, shots on target, corners, fouls, and disciplinary cards across 16 seasons (2010/11 through 2025/26).
2. **Understat (Opta-based Expected Metrics)**: Team and player advanced metrics from 2014/15 through 2025/26:
   - **`xG` / `xGA`**: Expected goals scored and conceded based on shot quality.
   - **`npxG` / `npxGA` / `npxGD`**: Non-penalty expected goal metrics.
   - **`ppda`**: Passes Allowed Per Defensive Action (pressing intensity: lower value = more intense, aggressive pressing).
   - **`ppda_allowed`**: Opponent PPDA against the team (resistance to opponent pressing).
   - **`deep_completions` / `deep_allowed`**: Passes completed within 20 yards of the opponent's goal.
   - **`xPTS`**: Expected points based on match xG simulations.
   - **`xA`, `shots`, `key_passes`, `xGChain`, `xGBuildup`**: Granular player creative and build-up involvement.
3. **Transfermarkt**: Complete player career valuations, transfer records with fees (€), and managerial match-by-match histories.

---

## 📊 Dataset Schemas

### 1. Team Season Performance (`data/epl_team_season_stats.csv`)
- **Rows**: 320 (20 teams × 16 seasons from 2010/11 to 2025/26)
- **Columns (44)**:
  - `season`: Season label (`2025-2026`, `2024-2025`, `2023-2024`, etc.)
  - `season_year`: Season start year (`2025`, `2024`, etc.)
  - `league_rank`: Final league position (1 to 20)
  - `team_name`: Normalized club name (e.g. `Liverpool`, `Manchester City`, `Arsenal`)
  - `matches_played`, `wins`, `draws`, `losses`: Win/draw/loss counts
  - `goals_for`, `goals_against`, `goal_difference`, `points`: Standard table
  - **Advanced Metrics (Understat)**:
    - `xG`: Total Expected Goals
    - `xGA`: Total Expected Goals Against
    - `xGD`: Expected Goal Difference (`xG - xGA`)
    - `npxG`: Non-Penalty Expected Goals
    - `npxGA`: Non-Penalty Expected Goals Against
    - `npxGD`: Non-Penalty Expected Goal Difference
    - `ppda`: Pressing Intensity (Passes Per Defensive Action)
    - `ppda_allowed`: Opponent Pressing Intensity
    - `deep_completions`: Passes completed inside opponent's 20-yard zone
    - `deep_allowed`: Deep completions allowed
    - `xPTS`: Expected Points
  - `home_wins`, `home_draws`, `home_losses`, `home_goals_for`, `home_goals_against`: Home record
  - `away_wins`, `away_draws`, `away_losses`, `away_goals_for`, `away_goals_against`: Away record
  - `clean_sheets`: Zero-goal conceded matches
  - `total_shots`, `total_shots_on_target`: Shot volume & accuracy
  - `corners`, `fouls_committed`, `yellow_cards`, `red_cards`: In-match tactical indicators
  - `managers_in_charge`: Head coaches during the season
  - `total_transfer_spend_eur`, `total_transfer_income_eur`, `net_transfer_spend_eur`: Financial transfer balance

---

### 2. Player Seasonal Performance (`data/epl_player_season_stats.csv`)
- **Rows**: 7,425 player-season records
- **Key Columns**:
  - `player_id`: Unique Transfermarkt player ID
  - `player_name`: Full player name
  - `season`, `season_year`: Season identifier
  - `club_name`: Club represented
  - `position`, `sub_position`: Player role (Attack, Midfield, Defender, Goalkeeper)
  - `country_of_citizenship`, `date_of_birth`, `age_in_season`: Demographics
  - `appearances`, `minutes_played`: Playing time
  - `goals`, `assists`: Traditional output
  - `goals_per_90`, `assists_per_90`, `goal_contributions_per_90`: Per-90 rates
  - **Advanced Metrics**:
    - `xG`: Expected Goals
    - `npxG`: Non-Penalty xG
    - `xA`: Expected Assists
    - `shots`: Total shots taken
    - `key_passes`: Passes leading to a shot
    - `xGChain`: Possession chains leading to a shot
    - `xGBuildup`: Build-up involvement excluding shot & key pass
  - `yellow_cards`, `red_cards`: Discipline
  - `market_value_eur`, `highest_market_value_eur`: Financial market value

---

### 3. Premier League Transfers (`data/epl_transfers.csv`)
- **Rows**: 10,311 transfer records (2010–2026)
- **Key Columns**:
  - `player_name`, `player_id`: Transferred player
  - `season`, `season_year`: Season of transfer
  - `transfer_date`: Exact date (YYYY-MM-DD)
  - `transfer_window`: `Summer` or `Winter`
  - `pl_club_involved`: The Premier League club involved
  - `transfer_direction`: `In (Arrival)` or `Out (Departure)`
  - `from_club_name`, `to_club_name`: Origin and destination clubs
  - `transfer_fee_eur`: Cleaned transfer fee in Euros (`0.0` for free/loans)
  - `market_value_eur`: Estimated market value at transfer time
  - `transfer_type`: `Permanent Transfer` or `Free / Loan`

---

### 4. Coaches & Managerial Tenures (`data/epl_coaches_history.csv`)
- **Rows**: 430 managerial tenure records
- **Key Columns**:
  - `coach_name`: Full name of manager / head coach
  - `club_name`: Club managed
  - `season`, `season_year`: Season of tenure
  - `appointed_first_match`: Date of first match in charge
  - `departed_last_match`: Date of last match in charge
  - `tenure_status`: `Full Season` or `Partial Season / Interim`
  - `matches_managed`: Premier League matches in charge
  - `wins`, `draws`, `losses`, `points`: Match outcomes
  - `points_per_game`: Average points per game (PPG)
  - `win_percentage`: Percentage of matches won
  - `goals_for`, `goals_against`, `goal_difference`: Goal output under this coach

---

## 🚀 Running the Pipeline

```bash
# Checkout the branch
git checkout getting_data

# Run the automated pipeline
python3 scripts/fetch_epl_data.py
```
