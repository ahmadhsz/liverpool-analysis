# Premier League Historical Analysis & Datasets (2010/11 – 2024/25)

A comprehensive data engineering and analysis project covering the last 15 English Premier League (EPL) seasons. This repository contains structured datasets for team performance, individual player statistics, transfer market activities, and managerial tenures, alongside an automated extraction pipeline.

---

## 📁 Repository Structure

```
liverpool analysis/
├── data/
│   ├── epl_team_season_stats.csv     # Team standings, match stats, shots, corners, transfer spend & managers
│   ├── epl_player_season_stats.csv   # Player seasonal appearances, goals, assists, minutes, cards & valuations
│   ├── epl_transfers.csv             # 10,000+ incoming/outgoing transfers with fees, dates & windows
│   └── epl_coaches_history.csv       # Manager appointments, departures, match records, PPG & win rates
├── scripts/
│   └── fetch_epl_data.py             # Reproducible data extraction and aggregation pipeline
├── .gitignore
└── README.md
```

---

## 📊 Dataset Schemas

### 1. Team Season Performance (`data/epl_team_season_stats.csv`)
- **Rows**: 300 (20 teams × 15 seasons from 2010/11 to 2024/25)
- **Key Columns**:
  - `season`: Season format (`2023-2024`, `2022-2023`, etc.)
  - `season_year`: Starting year of the season (e.g. `2023`)
  - `league_rank`: Final league position (1 to 20)
  - `team_name`: Normalized club name (e.g. `Liverpool`, `Manchester City`, `Arsenal`)
  - `matches_played`, `wins`, `draws`, `losses`: Win/draw/loss counts
  - `goals_for`, `goals_against`, `goal_difference`, `points`: Standard standings table
  - `home_wins`, `home_draws`, `home_losses`, `home_goals_for`, `home_goals_against`: Home record
  - `away_wins`, `away_draws`, `away_losses`, `away_goals_for`, `away_goals_against`: Away record
  - `clean_sheets`: Number of matches with zero goals conceded
  - `total_shots`, `total_shots_on_target`: Shot production and accuracy
  - `corners`, `fouls_committed`, `yellow_cards`, `red_cards`: In-match tactical & disciplinary indicators
  - `managers_in_charge`: Comma-separated list of head coaches during the season
  - `total_transfer_spend_eur`, `total_transfer_income_eur`, `net_transfer_spend_eur`: Financial balance

---

### 2. Player Seasonal Performance (`data/epl_player_season_stats.csv`)
- **Rows**: 7,422 player-season records
- **Key Columns**:
  - `player_id`: Unique Transfermarkt player ID
  - `player_name`: Full player name
  - `season`, `season_year`: Season identifier
  - `club_name`: Club represented
  - `position`, `sub_position`: Player role (e.g., Attack, Centre-Forward, Midfield, Defender)
  - `country_of_citizenship`, `date_of_birth`, `age_in_season`: Demographics
  - `appearances`, `minutes_played`: Playing time in the Premier League
  - `goals`, `assists`: Direct goal involvement
  - `goals_per_90`, `assists_per_90`, `goal_contributions_per_90`: Normalized per-90 metrics
  - `yellow_cards`, `red_cards`: Disciplinary actions
  - `market_value_eur`, `highest_market_value_eur`: Estimated market valuation in Euros

---

### 3. Premier League Transfers (`data/epl_transfers.csv`)
- **Rows**: 10,311 transfer records (2010–2025)
- **Key Columns**:
  - `player_name`, `player_id`: Transferred player
  - `season`, `season_year`: Season of transfer
  - `transfer_date`: Exact date (YYYY-MM-DD)
  - `transfer_window`: `Summer` or `Winter`
  - `pl_club_involved`: The Premier League club involved
  - `transfer_direction`: `In (Arrival)` or `Out (Departure)`
  - `from_club_name`, `to_club_name`: Transfer origin and destination
  - `transfer_fee_eur`: Cleaned transfer fee in Euros (`0.0` for free/loans)
  - `market_value_eur`: Player market value at transfer time
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
  - `matches_managed`: Total Premier League matches in charge that season
  - `wins`, `draws`, `losses`, `points`: Match outcomes
  - `points_per_game`: Average points per game (PPG)
  - `win_percentage`: Percentage of matches won
  - `goals_for`, `goals_against`, `goal_difference`: Goals scored and conceded under this coach

---

## 🚀 How to Run the Pipeline

To re-fetch, update, or regenerate the datasets:

```bash
# Ensure you are on the getting_data branch
git checkout getting_data

# Run the automated pipeline
python3 scripts/fetch_epl_data.py
```

The script will automatically use cached raw data if present, or download and process the latest records.

---

## 🔍 Example Python Usage

```python
import pandas as pd

# Load datasets
team_df = pd.read_csv('data/epl_team_season_stats.csv')
coaches_df = pd.read_csv('data/epl_coaches_history.csv')
transfers_df = pd.read_csv('data/epl_transfers.csv')
players_df = pd.read_csv('data/epl_player_season_stats.csv')

# 1. Liverpool Season Summary across 15 seasons
lfc_seasons = team_df[team_df['team_name'] == 'Liverpool']
print(lfc_seasons[['season', 'league_rank', 'points', 'wins', 'goals_for', 'goals_against', 'managers_in_charge']])

# 2. Jürgen Klopp's managerial record at Liverpool
klopp_record = coaches_df[(coaches_df['club_name'] == 'Liverpool') & (coaches_df['coach_name'] == 'Jürgen Klopp')]
print(klopp_record[['season', 'matches_managed', 'wins', 'points_per_game', 'win_percentage']])

# 3. Top 5 most expensive Liverpool signings
top_lfc_signings = transfers_df[
    (transfers_df['pl_club_involved'] == 'Liverpool') & 
    (transfers_df['transfer_direction'] == 'In (Arrival)')
].sort_values('transfer_fee_eur', ascending=False)
print(top_lfc_signings[['player_name', 'season', 'transfer_fee_eur', 'from_club_name']].head(5))

# 4. Mohamed Salah's Premier League stats by season
salah_stats = players_df[players_df['player_name'] == 'Mohamed Salah']
print(salah_stats[['season', 'appearances', 'goals', 'assists', 'goals_per_90', 'minutes_played']])
```
