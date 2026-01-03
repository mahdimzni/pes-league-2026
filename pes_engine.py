import pandas as pd
import numpy as np
from functools import cmp_to_key

# ==========================================
# بخش ۱: منطق بازی، جدول و قهرمانی
# ==========================================

def check_h2h_winner(df, season_id, p1, p2):
    """
    برنده بازی رو در رو را مشخص می‌کند.
    اولويت ۱: امتیاز بیشتر در بازی‌های بین دو نفر
    اولویت ۲: تفاضل گل بهتر در بازی‌های بین دو نفر
    """
    matches = df[(df['season_id'] == season_id) & 
                 (((df['p1_name'] == p1) & (df['p2_name'] == p2)) | 
                  ((df['p1_name'] == p2) & (df['p2_name'] == p1)))]
    
    if matches.empty:
        return None

    p1_pts = 0; p2_pts = 0
    p1_goals = 0; p2_goals = 0

    for _, row in matches.iterrows():
        # تشخیص اینکه کدام بازیکن p1 است و کدام p2 در این ردیف
        if row['p1_name'] == p1:
            my_s, op_s = row['p1_score'], row['p2_score']
        else:
            my_s, op_s = row['p2_score'], row['p1_score']
        
        p1_goals += my_s
        p2_goals += op_s

        if my_s > op_s: p1_pts += 3
        elif op_s > my_s: p2_pts += 3
        else:
            p1_pts += 1
            p2_pts += 1

    # مقایسه امتیاز رو در رو
    if p1_pts > p2_pts: return p1
    if p2_pts > p1_pts: return p2
    
    # مقایسه تفاضل گل رو در رو (اگر امتیاز برابر بود)
    if p1_goals > p2_goals: return p1
    if p2_goals > p1_goals: return p2
    
    return None

def get_season_table(df, season_id):
    season_df = df[df['season_id'] == season_id]
    players = set(season_df['p1_name'].unique()) | set(season_df['p2_name'].unique())
    data = []

    for p in players:
        matches = season_df[(season_df['p1_name'] == p) | (season_df['p2_name'] == p)]
        matches_played = len(matches)
        
        points = 0; gf = 0; ga = 0
        for _, row in matches.iterrows():
            if row['p1_name'] == p:
                my_s, op_s = row['p1_score'], row['p2_score']
            else:
                my_s, op_s = row['p2_score'], row['p1_score']
            
            gf += my_s
            ga += op_s
            
            if my_s > op_s: points += 3
            elif my_s == op_s: points += 1
        
        data.append({
            'Player': p, 
            'Matches': matches_played, 
            'Points': points, 
            'GD': gf - ga, 
            'GF': gf, 
            'GA': ga
        })

    # تابع مقایسه برای چیدن جدول
    def compare_players(item1, item2):
        # 1. امتیاز
        if item1['Points'] != item2['Points']: 
            return item1['Points'] - item2['Points']
        
        # 2. بازی رو در رو
        p1, p2 = item1['Player'], item2['Player']
        h2h = check_h2h_winner(df, season_id, p1, p2)
        
        if h2h == p1: return 1  # p1 برنده است، پس بالاتر قرار می‌گیرد
        if h2h == p2: return -1 # p2 برنده است
        
        # 3. تفاضل گل کلی
        if item1['GD'] != item2['GD']: 
            return item1['GD'] - item2['GD']
        
        # 4. گل زده کلی
        return item1['GF'] - item2['GF']

    # مرتب‌سازی (reverse=True یعنی از بزرگ به کوچک)
    sorted_data = sorted(data, key=cmp_to_key(compare_players), reverse=True)
    
    df_table = pd.DataFrame(sorted_data)
    
    if not df_table.empty:
        df_table = df_table[['Player', 'Matches', 'Points', 'GF', 'GA', 'GD']]
        df_table = df_table.rename(columns={'GF': '+', 'GA': '-'})
        df_table.index = range(1, len(df_table) + 1)
        
    return df_table

def get_champion(df, season_id):
    table = get_season_table(df, season_id)
    if table.empty: return "No Data"
    
    # اگر تعداد بازی‌ها نابرابر باشد
    if table['Matches'].nunique() > 1:
        return "there is no champion in this season"
        
    return table.iloc[0]['Player']

# ==========================================
# بخش ۲: آمار کلی (بدون تغییر منطق قبلی)
# ==========================================

def get_all_time_summary(df):
    seasons = df['season_id'].unique()
    champ_counts = {}
    golden_cups = {}
    ultra_golden_cups = {}
    
    for s in seasons:
        c_name = get_champion(df, s)
        if c_name == "there is no champion in this season" or c_name == "No Data":
            continue

        champ_counts[c_name] = champ_counts.get(c_name, 0) + 1
        season_df = df[df['season_id'] == s]
        matches = season_df[(season_df['p1_name'] == c_name) | (season_df['p2_name'] == c_name)]
        losses = 0; wins = 0; total_games = len(matches)
        
        for _, row in matches.iterrows():
            if row['p1_name'] == c_name: my_s, op_s = row['p1_score'], row['p2_score']
            else: my_s, op_s = row['p2_score'], row['p1_score']
            if my_s < op_s: losses += 1
            elif my_s > op_s: wins += 1
            
        if losses == 0:
            if wins == total_games and total_games > 0: ultra_golden_cups[c_name] = ultra_golden_cups.get(c_name, 0) + 1
            else: golden_cups[c_name] = golden_cups.get(c_name, 0) + 1

    players = set(df['p1_name'].unique()) | set(df['p2_name'].unique())
    stats_data = []
    
    for p in players:
        matches = df[(df['p1_name'] == p) | (df['p2_name'] == p)]
        total_matches = len(matches)
        
        wins = 0; draws = 0; losses = 0; total_points = 0
        total_gf = 0; total_ga = 0
        
        for _, row in matches.iterrows():
            if row['p1_name'] == p: my_s, op_s = row['p1_score'], row['p2_score']
            else: my_s, op_s = row['p2_score'], row['p1_score']
            
            total_gf += my_s
            total_ga += op_s
            
            if my_s > op_s: wins += 1; total_points += 3
            elif my_s == op_s: draws += 1; total_points += 1
            else: losses += 1
        
        if total_matches > 0:
            avg_gf = round(total_gf / total_matches, 2)
            avg_ga = round(total_ga / total_matches, 2)
            ppm = round(total_points / total_matches, 3)
        else:
            avg_gf = 0; avg_ga = 0; ppm = 0

        stats_data.append({
            'Player': p,
            'Championships': champ_counts.get(p, 0),
            'Ultra Golden': ultra_golden_cups.get(p, 0),
            'Golden Cup': golden_cups.get(p, 0),
            'Matches': total_matches,
            'Wins': wins, 'Draws': draws, 'Losses': losses,
            'Point per Match': ppm,
            'XG_F': avg_gf, 'XG_A': avg_ga,
            '+': total_gf, '-': total_ga, 'GD': total_gf - total_ga
        })
        
    summary_df = pd.DataFrame(stats_data)
    if 'Ultra Golden' not in summary_df.columns: summary_df['Ultra Golden'] = 0

    total_games_col = summary_df['Wins'] + summary_df['Draws'] + summary_df['Losses']
    summary_df['Win %'] = (summary_df['Wins'] / total_games_col * 100).fillna(0).round(1)
    summary_df['Draw %'] = (summary_df['Draws'] / total_games_col * 100).fillna(0).round(1)
    summary_df['Loss %'] = (summary_df['Losses'] / total_games_col * 100).fillna(0).round(1)

    column_order = [
        'Player', 'Championships', 'Ultra Golden', 'Golden Cup',
        'Matches', 'Wins', 'Draws', 'Losses',
        'Win %', 'Draw %', 'Loss %',
        'XG_F', 'XG_A',
        '+', '-', 'GD',
        'Point per Match'
    ]
    summary_df = summary_df[column_order]
    summary_df = summary_df.sort_values(by=['Point per Match', 'GD'], ascending=[False, False])
    summary_df.index = range(1, len(summary_df) + 1)
    return summary_df

# ==========================================
# بخش ۳: ابزارهای کمکی
# ==========================================

def get_podium_stats(df):
    all_players = list(set(df['p1_name'].unique()) | set(df['p2_name'].unique()))
    stats = {p: {1: 0, 2: 0, 3: 0, 4: 0} for p in all_players}
    seasons = sorted(df['season_id'].unique())
    
    for s in seasons:
        table = get_season_table(df, s)
        if table.empty or table['Matches'].nunique() > 1:
            continue

        for rank, row in table.iterrows():
            player = row['Player']
            if rank <= 4: stats[player][rank] += 1
                
    result_df = pd.DataFrame.from_dict(stats, orient='index')
    result_df.columns = ['1st Place', '2nd Place', '3rd Place', '4th Place']
    result_df = result_df.sort_values(by=['1st Place', '2nd Place', '3rd Place', '4th Place'], ascending=False)
    return result_df

def get_detailed_h2h(df):
    players = sorted(list(set(df['p1_name'].unique()) | set(df['p2_name'].unique())))
    table_data = []
    win_matrix = pd.DataFrame(0, index=players, columns=players)
    seen_pairs = set()

    for p1 in players:
        for p2 in players:
            if p1 == p2: continue
            matches = df[((df['p1_name'] == p1) & (df['p2_name'] == p2)) | 
                         ((df['p1_name'] == p2) & (df['p2_name'] == p1))]
            total_games = len(matches)
            if total_games == 0: continue
            p1_wins = 0; p2_wins = 0; draws = 0; p1_goals = 0; p2_goals = 0
            for _, row in matches.iterrows():
                if row['p1_name'] == p1: s1, s2 = row['p1_score'], row['p2_score']
                else: s1, s2 = row['p2_score'], row['p1_score']
                p1_goals += s1; p2_goals += s2
                if s1 > s2: p1_wins += 1
                elif s2 > s1: p2_wins += 1
                else: draws += 1
            win_matrix.loc[p1, p2] = p1_wins
            pair_key = tuple(sorted((p1, p2)))
            if pair_key not in seen_pairs:
                seen_pairs.add(pair_key)
                table_data.append({
                    'Matchup': f"{p1} vs {p2}", 'Matches': total_games,
                    'P1 Goals': p1_goals, 'P2 Goals': p2_goals,
                    'P1 Win %': f"{(p1_wins/total_games)*100:.1f}%", 'P2 Win %': f"{(p2_wins/total_games)*100:.1f}%",
                    'Detailed Stats': f"{p1}: {p1_wins} | {p2}: {p2_wins} | D: {draws}"
                })
    return pd.DataFrame(table_data), win_matrix

def get_match_history(df, p1, p2, target='all'):
    if target != 'all': matches_df = df[df['season_id'] == target]
    else: matches_df = df
    mask = (((matches_df['p1_name'] == p1) & (matches_df['p2_name'] == p2)) |
            ((matches_df['p1_name'] == p2) & (matches_df['p2_name'] == p1)))
    relevant_matches = matches_df[mask]
    data = []
    for _, row in relevant_matches.iterrows():
        if row['p1_name'] == p1: score1 = row['p1_score']; score2 = row['p2_score']
        else: score1 = row['p2_score']; score2 = row['p1_score']
        data.append({p1: score1, p2: score2})
    result_df = pd.DataFrame(data)
    if not result_df.empty: result_df.index = range(1, len(result_df) + 1)
    return result_df

def get_high_scores(df, p1=None, p2=None, min_goals=None, min_diff=None):
    temp_df = df.copy()
    temp_df['goal_diff'] = abs(temp_df['p1_score'] - temp_df['p2_score'])
    final_mask = pd.Series([True] * len(temp_df), index=temp_df.index)
    if min_goals is not None: final_mask &= ((temp_df['p1_score'] >= min_goals) | (temp_df['p2_score'] >= min_goals))
    if min_diff is not None: final_mask &= (temp_df['goal_diff'] >= min_diff)
    if p1 and p2: final_mask &= (((temp_df['p1_name'] == p1) & (temp_df['p2_name'] == p2)) | ((temp_df['p1_name'] == p2) & (temp_df['p2_name'] == p1)))
    elif p1 and not p2: final_mask &= ((temp_df['p1_name'] == p1) | (temp_df['p2_name'] == p1))
    elif p2 and not p1: final_mask &= ((temp_df['p1_name'] == p2) | (temp_df['p2_name'] == p2))
    
    filtered_df = temp_df[final_mask]
    data = []
    for _, row in filtered_df.iterrows():
        n1, n2 = row['p1_name'], row['p2_name']; s1, s2 = row['p1_score'], row['p2_score']
        swap = False
        if p1 and p2: 
            if n1 == p2: swap = True
        elif p1: 
            if n1 != p1: swap = True
        elif p2: 
            if n1 != p2: swap = True
        else: 
            if s2 > s1: swap = True
        if swap: n1, n2 = n2, n1; s1, s2 = s2, s1
        data.append({'p1': n1, 'p2': n2, 'Score1': f"{n1}:{s1}", 'Score2': f"{n2}:{s2}", 'Diff': abs(s1 - s2)})
    
    result_df = pd.DataFrame(data)
    if not result_df.empty: result_df.index = range(1, len(result_df) + 1)
    return result_df

def get_extreme_stats(df):
    summary = get_all_time_summary(df)
    metrics = [
        {'Type': 'Good', 'Title': 'Highest Win Rate', 'Col': 'Win %', 'Func': 'max', 'Unit': '%'},
        {'Type': 'Good', 'Title': 'Lowest Loss Rate', 'Col': 'Loss %', 'Func': 'min', 'Unit': '%'},
        {'Type': 'Good', 'Title': 'Highest Avg Goals Scored', 'Col': 'XG_F', 'Func': 'max', 'Unit': ''}, 
        {'Type': 'Good', 'Title': 'Best Defense (Lowest Avg GA)', 'Col': 'XG_A', 'Func': 'min', 'Unit': ''}, 
        {'Type': 'Bad', 'Title': 'Lowest Win Rate', 'Col': 'Win %', 'Func': 'min', 'Unit': '%'},
        {'Type': 'Bad', 'Title': 'Highest Loss Rate', 'Col': 'Loss %', 'Func': 'max', 'Unit': '%'},
        {'Type': 'Bad', 'Title': 'Lowest Avg Goals Scored', 'Col': 'XG_F', 'Func': 'min', 'Unit': ''},
        {'Type': 'Bad', 'Title': 'Worst Defense (Highest Avg GA)', 'Col': 'XG_A', 'Func': 'max', 'Unit': ''},
    ]

    data = []
    for item in metrics:
        col = item['Col']
        if item['Func'] == 'max': val = summary[col].max()
        else: val = summary[col].min()
        players = summary[summary[col] == val]['Player'].tolist()
        player_str = ", ".join(players)
        if item['Unit'] == '%': val_str = f"{val}%"
        else: val_str = str(val)
        data.append({
            'Category': item['Type'],
            'Statistic': item['Title'],
            'Value': val_str,
            'Player(s)': player_str
        })
    result_df = pd.DataFrame(data)
    if not result_df.empty: result_df.index = range(1, len(result_df) + 1)
    return result_df

def get_winning_streaks(df):
    seasons = sorted(df['season_id'].unique())
    if not seasons: return pd.DataFrame()
    timeline = []
    for s in seasons:
        champ = get_champion(df, s)
        if champ != "there is no champion in this season" and champ != "No Data":
            timeline.append(champ)

    streaks_found = []
    if not timeline: return pd.DataFrame()
    curr_p = timeline[0]; curr_l = 1
    for i in range(1, len(timeline)):
        if timeline[i] == curr_p: curr_l += 1
        else:
            if curr_l > 1: streaks_found.append({'Player': curr_p, 'Length': curr_l})
            curr_p = timeline[i]; curr_l = 1
    if curr_l > 1: streaks_found.append({'Player': curr_p, 'Length': curr_l})
    
    if not streaks_found: return pd.DataFrame()
    temp_df = pd.DataFrame(streaks_found)
    summary_df = temp_df.groupby(['Player', 'Length']).size().reset_index(name='Count')
    summary_df = summary_df.rename(columns={'Length': 'Consecutive Titles'})
    summary_df['Description'] = summary_df.apply(lambda x: f"{x['Count']} time(s): {x['Consecutive Titles']} in a row", axis=1)
    summary_df = summary_df.sort_values(by=['Consecutive Titles', 'Count'], ascending=[False, False])
    summary_df.index = range(1, len(summary_df) + 1)
    return summary_df
