#!/usr/bin/env python3
"""
Premier League Historical Data Pipeline (2010/11 - 2025/26)
===========================================================
Extracts, transforms, and exports 4 comprehensive datasets:
1. epl_team_season_stats.csv - Standings, match stats, advanced metrics (xG, xGA, PPDA, xPTS, Deep completions), transfers & coaches
2. epl_player_season_stats.csv - Player appearances, goals, assists, xG, xA, npxG, key passes, shots, xGChain, xGBuildup, valuation
3. epl_transfers.csv - All incoming/outgoing transfers for PL clubs with fees, market values, and transfer windows
4. epl_coaches_history.csv - Manager appointments, departures, match records, PPG, win rates
"""

import os
import io
import gzip
import re
import datetime
import requests
import pandas as pd
import numpy as np

try:
    from understatapi import UnderstatClient
    HAS_UNDERSTAT = True
except ImportError:
    HAS_UNDERSTAT = False

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
RAW_DIR = os.path.join(DATA_DIR, 'raw')
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(RAW_DIR, exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

R2_BASE = 'https://pub-e682421888d945d684bcae8890b0ec20.r2.dev/data/'

def log(msg):
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}")

def download_csv_gz(url):
    filename = url.split('/')[-1]
    local_path = os.path.join(RAW_DIR, filename)
    if os.path.exists(local_path) and os.path.getsize(local_path) > 1000:
        log(f"Loading cached {filename} ({os.path.getsize(local_path)//1024} KB)...")
        return pd.read_csv(local_path, compression='gzip', low_memory=False)
    log(f"Downloading {url} ...")
    r = requests.get(url, headers=HEADERS, timeout=120)
    r.raise_for_status()
    with open(local_path, 'wb') as f:
        f.write(r.content)
    log(f"  Cached {filename} to disk.")
    return pd.read_csv(local_path, compression='gzip', low_memory=False)

def download_csv(url):
    filename = url.split('/')[-1]
    local_path = os.path.join(RAW_DIR, filename)
    if os.path.exists(local_path) and os.path.getsize(local_path) > 100:
        log(f"Loading cached {filename} ...")
        return pd.read_csv(local_path)
    log(f"Downloading {url} ...")
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    with open(local_path, 'wb') as f:
        f.write(r.content)
    return pd.read_csv(local_path)

def normalize_team_name(name):
    if not isinstance(name, str):
        return name
    name = name.strip()
    mapping = {
        'Man United': 'Manchester United',
        'Man Utd': 'Manchester United',
        'Man City': 'Manchester City',
        'Tottenham': 'Tottenham Hotspur',
        'Spurs': 'Tottenham Hotspur',
        'Newcastle': 'Newcastle United',
        'Wolves': 'Wolverhampton Wanderers',
        'West Ham': 'West Ham United',
        'Leicester': 'Leicester City',
        'Brighton': 'Brighton & Hove Albion',
        'Brighton and Hove Albion': 'Brighton & Hove Albion',
        'Leeds': 'Leeds United',
        'Norwich': 'Norwich City',
        'Cardiff': 'Cardiff City',
        'Swansea': 'Swansea City',
        'Hull': 'Hull City',
        'Stoke': 'Stoke City',
        'West Brom': 'West Bromwich Albion',
        'QPR': 'Queens Park Rangers',
        'Blackburn': 'Blackburn Rovers',
        'Bolton': 'Bolton Wanderers',
        'Wigan': 'Wigan Athletic',
        'Huddersfield': 'Huddersfield Town',
        'Sheffield United': 'Sheffield United',
        'Sheff Utd': 'Sheffield United',
        'Nottm Forest': 'Nottingham Forest',
        'Nottingham': 'Nottingham Forest',
        'Luton': 'Luton Town',
        'Ipswich': 'Ipswich Town',
        'Bournemouth': 'AFC Bournemouth',
        'AFC Bournemouth': 'AFC Bournemouth',
        'Liverpool FC': 'Liverpool FC',
        'Liverpool': 'Liverpool FC',
        'Arsenal FC': 'Arsenal FC',
        'Arsenal': 'Arsenal FC',
        'Chelsea FC': 'Chelsea FC',
        'Chelsea': 'Chelsea FC',
        'Everton FC': 'Everton FC',
        'Everton': 'Everton FC',
        'Southampton FC': 'Southampton FC',
        'Southampton': 'Southampton FC',
        'Fulham FC': 'Fulham FC',
        'Fulham': 'Fulham FC',
        'Aston Villa': 'Aston Villa',
        'Crystal Palace': 'Crystal Palace',
        'Brentford FC': 'Brentford FC',
        'Brentford': 'Brentford FC',
        'Burnley FC': 'Burnley FC',
        'Burnley': 'Burnley FC',
        'Watford FC': 'Watford FC',
        'Watford': 'Watford FC',
        'Middlesbrough FC': 'Middlesbrough FC',
        'Middlesbrough': 'Middlesbrough FC',
        'Sunderland AFC': 'Sunderland AFC',
        'Sunderland': 'Sunderland AFC',
        'Reading FC': 'Reading FC',
        'Reading': 'Reading FC'
    }
    return mapping.get(name, name)

def standard_club_name(name):
    if not isinstance(name, str):
        return name
    n = normalize_team_name(name)
    clean = n.replace(' FC', '').replace(' AFC', '').strip()
    return clean

def get_season_code(season_start_year):
    y1 = str(season_start_year)[-2:]
    y2 = str(season_start_year + 1)[-2:]
    return f"{y1}{y2}"

def parse_season_year(s, date_str):
    if pd.notna(s):
        s_str = str(s).strip()
        if s_str.isdigit():
            return int(s_str)
        try:
            f_val = float(s_str)
            if not np.isnan(f_val):
                return int(f_val)
        except:
            pass
        if '/' in s_str:
            parts = s_str.split('/')
            try:
                if len(parts[0]) == 2:
                    y = int(parts[0])
                    return 2000 + y if y < 50 else 1900 + y
                elif len(parts[0]) == 4:
                    return int(parts[0])
            except:
                pass
    if isinstance(date_str, str) and len(date_str) >= 4:
        try:
            year = int(date_str[:4])
            m = int(date_str[5:7]) if len(date_str) >= 7 else 7
            return year if m >= 6 else year - 1
        except:
            pass
    return 2020

def fetch_football_data_matches():
    log("Fetching match statistics from Football-Data.co.uk (2010-2026)...")
    season_years = range(2010, 2026)  # 2010/11 through 2025/26
    dfs = []
    
    for year in season_years:
        code = get_season_code(year)
        season_label = f"{year}-{year+1}"
        local_filename = f"fd_{code}_E0.csv"
        local_path = os.path.join(RAW_DIR, local_filename)
        
        # Don't cache ongoing season permanently so latest games refresh
        use_cache = os.path.exists(local_path) and os.path.getsize(local_path) > 1000 and year < 2025
        if use_cache:
            df = pd.read_csv(local_path, on_bad_lines='skip')
        else:
            url = f"https://www.football-data.co.uk/mmz4281/{code}/E0.csv"
            try:
                r = requests.get(url, headers=HEADERS, timeout=15)
                if r.status_code == 200:
                    with open(local_path, 'wb') as f:
                        f.write(r.content)
                    df = pd.read_csv(local_path, on_bad_lines='skip')
                else:
                    df = pd.DataFrame()
            except Exception as e:
                log(f"  Error fetching season {season_label}: {e}")
                df = pd.DataFrame()
                
        if 'HomeTeam' in df.columns and 'AwayTeam' in df.columns and len(df) > 0:
            df['season'] = season_label
            df['season_year'] = year
            dfs.append(df)
            log(f"  Loaded season {season_label} ({len(df)} matches)")
            
    if not dfs:
        return pd.DataFrame()
        
    all_matches = pd.concat(dfs, ignore_index=True)
    all_matches = all_matches.dropna(subset=['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG'])
    all_matches['HomeTeam'] = all_matches['HomeTeam'].apply(standard_club_name)
    all_matches['AwayTeam'] = all_matches['AwayTeam'].apply(standard_club_name)
    return all_matches

def fetch_understat_data():
    if not HAS_UNDERSTAT:
        log("understatapi not installed, skipping Understat advanced metrics.")
        return pd.DataFrame(), pd.DataFrame()

    log("Fetching advanced metrics (xG, xGA, PPDA, xPTS, Deep completions) from Understat (2014-2025)...")
    u = UnderstatClient()
    understat_years = range(2014, 2026)
    
    team_records = []
    player_records = []
    
    for s_year in understat_years:
        season_str = str(s_year)
        season_label = f"{s_year}-{s_year+1}"
        
        # 1. Team Data
        try:
            team_data = u.league(league='EPL').get_team_data(season=season_str)
            for t_id, t_info in team_data.items():
                title = standard_club_name(t_info['title'])
                hist = pd.DataFrame(t_info['history'])
                
                # PPDA calculations
                ppda_att = sum([x['att'] for x in hist['ppda']])
                ppda_def = sum([x['def'] for x in hist['ppda']])
                ppda = round(ppda_att / ppda_def, 2) if ppda_def > 0 else None
                
                ppda_al_att = sum([x['att'] for x in hist['ppda_allowed']])
                ppda_al_def = sum([x['def'] for x in hist['ppda_allowed']])
                ppda_allowed = round(ppda_al_att / ppda_al_def, 2) if ppda_al_def > 0 else None
                
                xg = round(hist['xG'].astype(float).sum(), 2)
                xga = round(hist['xGA'].astype(float).sum(), 2)
                npxg = round(hist['npxG'].astype(float).sum(), 2)
                npxga = round(hist['npxGA'].astype(float).sum(), 2)
                deep = int(hist['deep'].astype(int).sum())
                deep_al = int(hist['deep_allowed'].astype(int).sum())
                xpts = round(hist['xpts'].astype(float).sum(), 2)
                
                team_records.append({
                    'team_name': title,
                    'season_year': s_year,
                    'xG': xg,
                    'xGA': xga,
                    'xGD': round(xg - xga, 2),
                    'npxG': npxg,
                    'npxGA': npxga,
                    'npxGD': round(npxg - npxga, 2),
                    'ppda': ppda,
                    'ppda_allowed': ppda_allowed,
                    'deep_completions': deep,
                    'deep_allowed': deep_al,
                    'xPTS': xpts
                })
        except Exception as e:
            log(f"  Understat team data error for {season_label}: {e}")

        # 2. Player Data
        try:
            player_data = u.league(league='EPL').get_player_data(season=season_str)
            for p in player_data:
                player_records.append({
                    'player_name': p.get('player_name'),
                    'team_name': standard_club_name(p.get('team_title')),
                    'season_year': s_year,
                    'understat_games': int(p.get('games', 0)),
                    'understat_minutes': int(p.get('time', 0)),
                    'understat_goals': int(p.get('goals', 0)),
                    'understat_npg': int(p.get('npg', 0)),
                    'understat_assists': int(p.get('assists', 0)),
                    'xG': round(float(p.get('xG', 0)), 2),
                    'npxG': round(float(p.get('npxG', 0)), 2),
                    'xA': round(float(p.get('xA', 0)), 2),
                    'shots': int(p.get('shots', 0)),
                    'key_passes': int(p.get('key_passes', 0)),
                    'xGChain': round(float(p.get('xGChain', 0)), 2),
                    'xGBuildup': round(float(p.get('xGBuildup', 0)), 2)
                })
            log(f"  Loaded Understat stats for season {season_label} ({len(player_data)} players)")
        except Exception as e:
            log(f"  Understat player data error for {season_label}: {e}")

    df_team_understat = pd.DataFrame(team_records)
    df_player_understat = pd.DataFrame(player_records)
    return df_team_understat, df_player_understat

def build_coaches_history(games_df):
    log("Building coaches history dataset...")
    games_epl = games_df[games_df['competition_id'] == 'GB1'].copy()
    games_epl['date'] = pd.to_datetime(games_epl['date'])
    games_epl = games_epl.sort_values('date')

    home_recs = games_epl[['game_id', 'season', 'date', 'home_club_name', 'home_club_manager_name', 'home_club_goals', 'away_club_goals']].copy()
    home_recs.columns = ['game_id', 'season_year', 'date', 'club_name', 'coach_name', 'goals_for', 'goals_against']
    home_recs['is_home'] = 1
    
    away_recs = games_epl[['game_id', 'season', 'date', 'away_club_name', 'away_club_manager_name', 'away_club_goals', 'home_club_goals']].copy()
    away_recs.columns = ['game_id', 'season_year', 'date', 'club_name', 'coach_name', 'goals_for', 'goals_against']
    away_recs['is_home'] = 0

    all_coach_matches = pd.concat([home_recs, away_recs], ignore_index=True)
    all_coach_matches = all_coach_matches.dropna(subset=['coach_name', 'club_name'])
    all_coach_matches['club_name'] = all_coach_matches['club_name'].apply(standard_club_name)
    
    def get_res(row):
        if row['goals_for'] > row['goals_against']:
            return 'W', 3
        elif row['goals_for'] == row['goals_against']:
            return 'D', 1
        else:
            return 'L', 0

    results = all_coach_matches.apply(get_res, axis=1)
    all_coach_matches['result'] = [r[0] for r in results]
    all_coach_matches['points'] = [r[1] for r in results]
    all_coach_matches['win'] = (all_coach_matches['result'] == 'W').astype(int)
    all_coach_matches['draw'] = (all_coach_matches['result'] == 'D').astype(int)
    all_coach_matches['loss'] = (all_coach_matches['result'] == 'L').astype(int)

    grouped = all_coach_matches.groupby(['coach_name', 'club_name', 'season_year'])
    coach_records = []

    for (coach, club, s_year), group in grouped:
        s_year_int = int(s_year)
        season_label = f"{s_year_int}-{s_year_int+1}"
        matches_managed = len(group)
        wins = int(group['win'].sum())
        draws = int(group['draw'].sum())
        losses = int(group['loss'].sum())
        points = int(group['points'].sum())
        gf = int(group['goals_for'].sum())
        ga = int(group['goals_against'].sum())
        gd = gf - ga
        ppg = round(points / matches_managed, 2) if matches_managed > 0 else 0.0
        win_pct = round((wins / matches_managed) * 100, 1) if matches_managed > 0 else 0.0
        start_date = group['date'].min().strftime('%Y-%m-%d')
        end_date = group['date'].max().strftime('%Y-%m-%d')
        
        tenure_status = "Full Season" if matches_managed >= 38 else ("Partial Season (Early Exit)" if group['date'].max().month in [9,10,11,12,1,2,3] and matches_managed < 30 else "Partial Season / Interim")

        coach_records.append({
            'coach_name': coach,
            'club_name': club,
            'season': season_label,
            'season_year': s_year_int,
            'appointed_first_match': start_date,
            'departed_last_match': end_date,
            'tenure_status': tenure_status,
            'matches_managed': matches_managed,
            'wins': wins,
            'draws': draws,
            'losses': losses,
            'points': points,
            'points_per_game': ppg,
            'win_percentage': win_pct,
            'goals_for': gf,
            'goals_against': ga,
            'goal_difference': gd
        })

    coaches_df = pd.DataFrame(coach_records)
    coaches_df = coaches_df.sort_values(['season_year', 'club_name', 'appointed_first_match'], ascending=[False, True, True])
    return coaches_df

def build_transfers(transfers_raw, epl_clubs_set):
    log("Building transfers dataset...")
    df = transfers_raw.copy()
    df['from_club_clean'] = df['from_club_name'].apply(standard_club_name)
    df['to_club_clean'] = df['to_club_name'].apply(standard_club_name)

    mask = df['from_club_clean'].isin(epl_clubs_set) | df['to_club_clean'].isin(epl_clubs_set)
    df_epl = df[mask].copy()

    def get_window(dt_str):
        if not isinstance(dt_str, str) or len(dt_str) < 7:
            return 'Summer'
        try:
            m = int(dt_str.split('-')[1])
            if m in [1, 2]:
                return 'Winter'
            elif m in [6, 7, 8, 9]:
                return 'Summer'
            else:
                return 'Other'
        except:
            return 'Summer'

    df_epl['transfer_window'] = df_epl['transfer_date'].apply(get_window)

    records = []
    for idx, row in df_epl.iterrows():
        p_name = row['player_name']
        p_id = row['player_id']
        t_date = row['transfer_date']
        raw_season = row['transfer_season']
        
        season_y = parse_season_year(raw_season, t_date)
        season_label = f"{season_y}-{season_y+1}"
        
        from_c = row['from_club_clean']
        to_c = row['to_club_clean']
        fee = row['transfer_fee']
        mv = row['market_value_in_eur']
        fee_clean = float(fee) if (pd.notna(fee) and fee >= 0) else 0.0
        mv_clean = float(mv) if (pd.notna(mv) and mv >= 0) else 0.0

        is_in = to_c in epl_clubs_set
        is_out = from_c in epl_clubs_set

        if is_in:
            records.append({
                'player_name': p_name,
                'player_id': p_id,
                'season': season_label,
                'season_year': season_y,
                'transfer_date': t_date,
                'transfer_window': row['transfer_window'],
                'pl_club_involved': to_c,
                'transfer_direction': 'In (Arrival)',
                'from_club_name': from_c,
                'to_club_name': to_c,
                'transfer_fee_eur': fee_clean,
                'market_value_eur': mv_clean,
                'transfer_type': 'Free / Loan' if fee_clean == 0 else 'Permanent Transfer'
            })
        if is_out:
            records.append({
                'player_name': p_name,
                'player_id': p_id,
                'season': season_label,
                'season_year': season_y,
                'transfer_date': t_date,
                'transfer_window': row['transfer_window'],
                'pl_club_involved': from_c,
                'transfer_direction': 'Out (Departure)',
                'from_club_name': from_c,
                'to_club_name': to_c,
                'transfer_fee_eur': fee_clean,
                'market_value_eur': mv_clean,
                'transfer_type': 'Free / Loan' if fee_clean == 0 else 'Permanent Transfer'
            })

    out_df = pd.DataFrame(records)
    out_df = out_df[out_df['season_year'] >= 2010]
    out_df = out_df.sort_values(['transfer_date', 'pl_club_involved'], ascending=[False, True])
    return out_df

def build_player_season_stats(players_df, appearances_df, games_df, player_understat_df):
    log("Building player seasonal statistics dataset...")
    epl_game_ids = set(games_df[games_df['competition_id'] == 'GB1']['game_id'])
    
    app_epl = appearances_df[appearances_df['game_id'].isin(epl_game_ids)].copy()
    games_lookup = games_df[['game_id', 'season']].drop_duplicates()
    app_epl = app_epl.merge(games_lookup, on='game_id', how='left')

    grouped = app_epl.groupby(['player_id', 'season']).agg(
        appearances=('appearance_id', 'count'),
        minutes_played=('minutes_played', 'sum'),
        goals=('goals', 'sum'),
        assists=('assists', 'sum'),
        yellow_cards=('yellow_cards', 'sum'),
        red_cards=('red_cards', 'sum'),
        player_name=('player_name', 'first')
    ).reset_index()

    p_info = players_df[['player_id', 'name', 'position', 'sub_position', 'country_of_citizenship', 'date_of_birth', 'height_in_cm', 'market_value_in_eur', 'highest_market_value_in_eur', 'current_club_name']].copy()
    p_info['player_name_clean'] = p_info['name']
    
    merged = grouped.merge(p_info, on='player_id', how='left')
    merged['player_name'] = merged['player_name'].fillna(merged['player_name_clean'])

    merged['goals_per_90'] = np.where(merged['minutes_played'] > 0, (merged['goals'] / merged['minutes_played']) * 90, 0.0).round(2)
    merged['assists_per_90'] = np.where(merged['minutes_played'] > 0, (merged['assists'] / merged['minutes_played']) * 90, 0.0).round(2)
    merged['goal_contributions_per_90'] = ((merged['goals'] + merged['assists']) / np.where(merged['minutes_played'] > 0, merged['minutes_played'], np.nan) * 90).round(2).fillna(0.0)

    merged['season_year'] = merged['season'].astype(int)
    merged['season'] = merged['season_year'].apply(lambda y: f"{y}-{y+1}")
    
    def calc_age(dob_str, season_y):
        try:
            b_year = int(str(dob_str)[:4])
            return season_y - b_year
        except:
            return np.nan

    merged['age_in_season'] = merged.apply(lambda r: calc_age(r['date_of_birth'], r['season_year']), axis=1)
    merged['club_name'] = merged['current_club_name'].apply(standard_club_name)

    merged['market_value_eur'] = merged['market_value_in_eur']
    merged['highest_market_value_eur'] = merged['highest_market_value_in_eur']

    # Merge Understat advanced metrics if available
    if not player_understat_df.empty:
        log("Merging Understat xG, xA, shots, and key passes into player stats...")
        # Merge on player_name and season_year
        merged = merged.merge(
            player_understat_df[['player_name', 'season_year', 'xG', 'npxG', 'xA', 'shots', 'key_passes', 'xGChain', 'xGBuildup']],
            on=['player_name', 'season_year'],
            how='left'
        )

    cols = [
        'player_id', 'player_name', 'season', 'season_year', 'club_name',
        'position', 'sub_position', 'country_of_citizenship', 'date_of_birth', 'age_in_season',
        'appearances', 'minutes_played', 'goals', 'assists',
        'goals_per_90', 'assists_per_90', 'goal_contributions_per_90'
    ]
    
    if 'xG' in merged.columns:
        cols += ['xG', 'npxG', 'xA', 'shots', 'key_passes', 'xGChain', 'xGBuildup']
        
    cols += ['yellow_cards', 'red_cards', 'market_value_eur', 'highest_market_value_eur']

    # Keep only available columns
    final_cols = [c for c in cols if c in merged.columns]
    res = merged[final_cols].sort_values(['season_year', 'goals', 'minutes_played'], ascending=[False, False, False])
    return res

def build_team_season_stats(fd_matches, coaches_df, transfers_df, team_understat_df):
    log("Building team season statistics dataset...")
    all_teams_by_season = []
    seasons = sorted(fd_matches['season_year'].unique())
    
    for s_year in seasons:
        s_df = fd_matches[fd_matches['season_year'] == s_year]
        season_label = f"{s_year}-{s_year+1}"
        teams = sorted(set(s_df['HomeTeam']).union(set(s_df['AwayTeam'])))
        
        table = []
        for team in teams:
            h_matches = s_df[s_df['HomeTeam'] == team]
            a_matches = s_df[s_df['AwayTeam'] == team]
            
            mp = len(h_matches) + len(a_matches)
            if mp == 0:
                continue

            hw = (h_matches['FTR'] == 'H').sum()
            hd = (h_matches['FTR'] == 'D').sum()
            hl = (h_matches['FTR'] == 'A').sum()
            hgf = h_matches['FTHG'].sum()
            hga = h_matches['FTAG'].sum()

            aw = (a_matches['FTR'] == 'A').sum()
            ad = (a_matches['FTR'] == 'D').sum()
            al = (a_matches['FTR'] == 'H').sum()
            agf = a_matches['FTAG'].sum()
            aga = a_matches['FTHG'].sum()

            w = int(hw + aw)
            d = int(hd + ad)
            l = int(hl + al)
            gf = int(hgf + agf)
            ga = int(hga + aga)
            gd = int(gf - ga)
            pts = int(w * 3 + d)
            
            h_cs = (h_matches['FTAG'] == 0).sum()
            a_cs = (a_matches['FTHG'] == 0).sum()
            clean_sheets = int(h_cs + a_cs)

            h_shots = h_matches['HS'].sum() if 'HS' in h_matches.columns else 0
            a_shots = a_matches['AS'].sum() if 'AS' in a_matches.columns else 0
            total_shots = int(h_shots + a_shots) if pd.notna(h_shots) else 0

            h_sot = h_matches['HST'].sum() if 'HST' in h_matches.columns else 0
            a_sot = a_matches['AST'].sum() if 'AST' in a_matches.columns else 0
            total_sot = int(h_sot + a_sot) if pd.notna(h_sot) else 0

            h_c = h_matches['HC'].sum() if 'HC' in h_matches.columns else 0
            a_c = a_matches['AC'].sum() if 'AC' in a_matches.columns else 0
            total_corners = int(h_c + a_c) if pd.notna(h_c) else 0

            h_f = h_matches['HF'].sum() if 'HF' in h_matches.columns else 0
            a_f = a_matches['AF'].sum() if 'AF' in a_matches.columns else 0
            total_fouls = int(h_f + a_f) if pd.notna(h_f) else 0

            h_yc = h_matches['HY'].sum() if 'HY' in h_matches.columns else 0
            a_yc = a_matches['AY'].sum() if 'AY' in a_matches.columns else 0
            total_yc = int(h_yc + a_yc) if pd.notna(h_yc) else 0

            h_rc = h_matches['HR'].sum() if 'HR' in h_matches.columns else 0
            a_rc = a_matches['AR'].sum() if 'AR' in a_matches.columns else 0
            total_rc = int(h_rc + a_rc) if pd.notna(h_rc) else 0

            c_matches = coaches_df[(coaches_df['season_year'] == s_year) & (coaches_df['club_name'] == team)]
            managers_str = ", ".join(c_matches['coach_name'].unique()) if len(c_matches) > 0 else "N/A"

            t_in = transfers_df[(transfers_df['season_year'] == s_year) & (transfers_df['pl_club_involved'] == team) & (transfers_df['transfer_direction'] == 'In (Arrival)')]
            t_out = transfers_df[(transfers_df['season_year'] == s_year) & (transfers_df['pl_club_involved'] == team) & (transfers_df['transfer_direction'] == 'Out (Departure)')]
            
            spend_eur = t_in['transfer_fee_eur'].sum()
            income_eur = t_out['transfer_fee_eur'].sum()
            net_spend_eur = spend_eur - income_eur

            table.append({
                'season': season_label,
                'season_year': s_year,
                'team_name': team,
                'matches_played': mp,
                'wins': w,
                'draws': d,
                'losses': l,
                'goals_for': gf,
                'goals_against': ga,
                'goal_difference': gd,
                'points': pts,
                'home_wins': int(hw),
                'home_draws': int(hd),
                'home_losses': int(hl),
                'home_goals_for': int(hgf),
                'home_goals_against': int(hga),
                'away_wins': int(aw),
                'away_draws': int(ad),
                'away_losses': int(al),
                'away_goals_for': int(agf),
                'away_goals_against': int(aga),
                'clean_sheets': clean_sheets,
                'total_shots': total_shots,
                'total_shots_on_target': total_sot,
                'corners': total_corners,
                'fouls_committed': total_fouls,
                'yellow_cards': total_yc,
                'red_cards': total_rc,
                'managers_in_charge': managers_str,
                'total_transfer_spend_eur': round(float(spend_eur), 2),
                'total_transfer_income_eur': round(float(income_eur), 2),
                'net_transfer_spend_eur': round(float(net_spend_eur), 2)
            })

        season_table = pd.DataFrame(table)
        season_table = season_table.sort_values(by=['points', 'goal_difference', 'goals_for'], ascending=[False, False, False]).reset_index(drop=True)
        season_table['league_rank'] = season_table.index + 1
        all_teams_by_season.append(season_table)

    final_team_df = pd.concat(all_teams_by_season, ignore_index=True)

    # Merge Understat advanced metrics
    if not team_understat_df.empty:
        log("Merging Understat xG, xGA, PPDA, and xPTS into team season table...")
        final_team_df = final_team_df.merge(
            team_understat_df,
            on=['team_name', 'season_year'],
            how='left'
        )

    cols = [
        'season', 'season_year', 'league_rank', 'team_name', 'matches_played',
        'wins', 'draws', 'losses', 'goals_for', 'goals_against', 'goal_difference', 'points',
        'xG', 'xGA', 'xGD', 'npxG', 'npxGA', 'npxGD', 'ppda', 'ppda_allowed', 'deep_completions', 'deep_allowed', 'xPTS',
        'home_wins', 'home_draws', 'home_losses', 'home_goals_for', 'home_goals_against',
        'away_wins', 'away_draws', 'away_losses', 'away_goals_for', 'away_goals_against',
        'clean_sheets', 'total_shots', 'total_shots_on_target', 'corners', 'fouls_committed',
        'yellow_cards', 'red_cards', 'managers_in_charge',
        'total_transfer_spend_eur', 'total_transfer_income_eur', 'net_transfer_spend_eur'
    ]
    # Filter only available columns
    avail_cols = [c for c in cols if c in final_team_df.columns]
    return final_team_df[avail_cols]

def main():
    log("=== Starting Premier League Historical Data Pipeline ===")
    
    # 1. Ingest Transfermarkt Core Datasets
    log("Step 1: Ingesting Transfermarkt Core Datasets...")
    clubs_df = download_csv_gz(R2_BASE + 'clubs.csv.gz')
    games_df = download_csv_gz(R2_BASE + 'games.csv.gz')
    players_df = download_csv_gz(R2_BASE + 'players.csv.gz')
    transfers_df_raw = download_csv_gz(R2_BASE + 'transfers.csv.gz')
    appearances_df = download_csv_gz(R2_BASE + 'appearances.csv.gz')

    epl_clubs = clubs_df[clubs_df['domestic_competition_id'] == 'GB1']
    epl_clubs_set = set(epl_clubs['name'].apply(standard_club_name))
    log(f"Identified {len(epl_clubs_set)} Premier League clubs.")

    # 2. Fetch Advanced Stats from Understat
    log("Step 2: Fetching Advanced Stats (xG, xGA, PPDA, xPTS, Deep completions)...")
    team_understat_df, player_understat_df = fetch_understat_data()

    # 3. Build Coaches History
    log("Step 3: Processing Coaches & Managerial Tenures...")
    coaches_df = build_coaches_history(games_df)
    coaches_path = os.path.join(DATA_DIR, 'epl_coaches_history.csv')
    coaches_df.to_csv(coaches_path, index=False)
    log(f"-> Saved: {coaches_path} ({len(coaches_df)} records)")

    # 4. Build Transfers
    log("Step 4: Processing Premier League Transfers...")
    transfers_df = build_transfers(transfers_raw=transfers_df_raw, epl_clubs_set=epl_clubs_set)
    transfers_path = os.path.join(DATA_DIR, 'epl_transfers.csv')
    transfers_df.to_csv(transfers_path, index=False)
    log(f"-> Saved: {transfers_path} ({len(transfers_df)} records)")

    # 5. Build Player Season Performance Stats
    log("Step 5: Processing Player Seasonal Performance Stats...")
    players_stats_df = build_player_season_stats(players_df, appearances_df, games_df, player_understat_df)
    player_path = os.path.join(DATA_DIR, 'epl_player_season_stats.csv')
    players_stats_df.to_csv(player_path, index=False)
    log(f"-> Saved: {player_path} ({len(players_stats_df)} records)")

    # 6. Fetch Match Stats & Build Team Season Performance Table
    log("Step 6: Processing Team Standings, Match Stats & Season Performance...")
    fd_matches = fetch_football_data_matches()
    team_stats_df = build_team_season_stats(fd_matches, coaches_df, transfers_df, team_understat_df)
    team_path = os.path.join(DATA_DIR, 'epl_team_season_stats.csv')
    team_stats_df.to_csv(team_path, index=False)
    log(f"-> Saved: {team_path} ({len(team_stats_df)} records)")

    log("=== Data Pipeline Execution Complete! ===")
    print("\nSummary of Generated Datasets:")
    print(f"1. Team Season Stats:    {len(team_stats_df)} rows  -> {team_path}")
    print(f"2. Player Season Stats:  {len(players_stats_df)} rows -> {player_path}")
    print(f"3. Transfers:            {len(transfers_df)} rows  -> {transfers_path}")
    print(f"4. Coaches History:      {len(coaches_df)} rows  -> {coaches_path}")

if __name__ == '__main__':
    main()
