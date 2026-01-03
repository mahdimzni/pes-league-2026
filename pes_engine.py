import pandas as pd
import numpy as np
from functools import cmp_to_key

def get_season_table(df, season_id):
    """
    جدول لیگ را محاسبه می‌کند.
    تغییرات جدید:
    1. اضافه شدن ستون Matches
    2. رتبه‌بندی بر اساس: امتیاز > بازی رو در رو > تفاضل گل > گل زده
    """
    # فیلتر کردن بازی‌های همین فصل
    season_df = df[df['season_id'] == season_id].copy()
    
    # پیدا کردن لیست تمام بازیکنانی که در این فصل بازی کرده‌اند
    players = set(season_df['p1_name'].unique()) | set(season_df['p2_name'].unique())
    players = list(players)
    
    # ساخت دیکشنری برای ذخیره آمار هر بازیکن
    # P همان Matches است که برای محاسبات داخلی استفاده می‌کنیم
    stats = {player: {'P': 0, 'W': 0, 'D': 0, 'L': 0, 
                      'GF': 0, 'GA': 0, 'GD': 0, 'Pts': 0} 
             for player in players}
    
    # محاسبه امتیازات پایه
    for _, row in season_df.iterrows():
        p1, p2 = row['p1_name'], row['p2_name']
        s1, s2 = row['p1_score'], row['p2_score']
        
        # آمار بازیکن 1
        stats[p1]['P'] += 1
        stats[p1]['GF'] += s1
        stats[p1]['GA'] += s2
        stats[p1]['GD'] += (s1 - s2)
        
        # آمار بازیکن 2
        stats[p2]['P'] += 1
        stats[p2]['GF'] += s2
        stats[p2]['GA'] += s1
        stats[p2]['GD'] += (s2 - s1)
        
        # امتیازدهی
        if s1 > s2:
            stats[p1]['W'] += 1
            stats[p1]['Pts'] += 3
            stats[p2]['L'] += 1
        elif s2 > s1:
            stats[p2]['W'] += 1
            stats[p2]['Pts'] += 3
            stats[p1]['L'] += 1
        else:
            stats[p1]['D'] += 1
            stats[p1]['Pts'] += 1
            stats[p2]['D'] += 1
            stats[p2]['Pts'] += 1

    # --- تابع مقایسه پیشرفته برای مرتب‌سازی (بازی رو در رو) ---
    def compare_players(player_a, player_b):
        stat_a = stats[player_a]
        stat_b = stats[player_b]
        
        # 1. مقایسه امتیاز
        if stat_a['Pts'] != stat_b['Pts']:
            return stat_a['Pts'] - stat_b['Pts']
        
        # 2. مقایسه بازی رو در رو (Head-to-Head)
        h2h_matches = season_df[
            ((season_df['p1_name'] == player_a) & (season_df['p2_name'] == player_b)) |
            ((season_df['p1_name'] == player_b) & (season_df['p2_name'] == player_a))
        ]
        
        pts_a_h2h = 0
        pts_b_h2h = 0
        
        for _, match in h2h_matches.iterrows():
            if match['p1_name'] == player_a:
                sc_a, sc_b = match['p1_score'], match['p2_score']
            else:
                sc_a, sc_b = match['p2_score'], match['p1_score']
                
            if sc_a > sc_b:
                pts_a_h2h += 3
            elif sc_b > sc_a:
                pts_b_h2h += 3
            else:
                pts_a_h2h += 1
                pts_b_h2h += 1
        
        if pts_a_h2h != pts_b_h2h:
            return pts_a_h2h - pts_b_h2h
            
        # 3. مقایسه تفاضل گل کلی
        if stat_a['GD'] != stat_b['GD']:
            return stat_a['GD'] - stat_b['GD']
            
        # 4. مقایسه گل زده بیشتر
        return stat_a['GF'] - stat_b['GF']

    # مرتب‌سازی
    sorted_players = sorted(players, key=cmp_to_key(compare_players), reverse=True)
    
    # ساخت دیتای نهایی
    final_data = []
    rank = 1
    for p in sorted_players:
        row = stats[p]
        row['Player'] = p
        row['Rank'] = rank
        # اینجا ستون P را به Matches تغییر نام می‌دهیم که واضح باشد
        row['Matches'] = row['P'] 
        final_data.append(row)
        rank += 1
        
    table_df = pd.DataFrame(final_data)
    
    # ترتیب ستون‌ها: Matches بعد از Player قرار گرفت
    cols = ['Rank', 'Player', 'Matches', 'Pts', 'W', 'D', 'L', 'GF', 'GA', 'GD']
    
    if table_df.empty:
        return pd.DataFrame(columns=cols)
        
    return table_df[cols].set_index('Rank')

def get_champion(df, season_id):
    """
    قهرمان را مشخص می‌کند اما فقط اگر تعداد بازی‌ها برابر باشد.
    """
    table = get_season_table(df, season_id)
    
    if table.empty:
        return "No Data"
        
    # بررسی نابرابری تعداد بازی‌ها
    # اگر تعداد مقادیر یکتای ستون Matches بیشتر از 1 باشد، یعنی بازی‌ها برابر نیست
    if table['Matches'].nunique() > 1:
        return "There is no champion in this season (Unequal Matches)"
        
    # در غیر این صورت نفر اول لیست قهرمان است
    return table.iloc[0]['Player']

# --- توابع کمکی دیگر (بدون تغییر) ---

def get_all_time_summary(df):
    players = set(df['p1_name'].unique()) | set(df['p2_name'].unique())
    summary = []
    for p in players:
        matches = df[(df['p1_name'] == p) | (df['p2_name'] == p)]
        played = len(matches)
        wins = 0
        draws = 0
        goals = 0
        for _, row in matches.iterrows():
            if row['p1_name'] == p:
                goals += row['p1_score']
                if row['p1_score'] > row['p2_score']: wins += 1
                elif row['p1_score'] == row['p2_score']: draws += 1
            else:
                goals += row['p2_score']
                if row['p2_score'] > row['p1_score']: wins += 1
                elif row['p1_score'] == row['p2_score']: draws += 1
        points = (wins * 3) + draws
        summary.append({'Player': p, 'Matches': played, 'Wins': wins, 'Goals': goals, 'Total Points': points})
    return pd.DataFrame(summary).sort_values('Total Points', ascending=False).reset_index(drop=True)

def get_podium_stats(df):
    seasons = df['season_id'].unique()
    stats = {}
    for s in seasons:
        table = get_season_table(df, s)
        # فقط در صورتی آمار سکو ثبت می‌شود که لیگ عادلانه تمام شده باشد (بازی‌ها برابر)
        if table.empty or table['Matches'].nunique() > 1:
            continue
            
        table = table.reset_index()
        for idx, row in table.iterrows():
            p = row['Player']
            rank = row['Rank']
            if p not in stats: stats[p] = {'1st':0, '2nd':0, '3rd':0, '4th':0}
            if rank == 1: stats[p]['1st'] += 1
            elif rank == 2: stats[p]['2nd'] += 1
            elif rank == 3: stats[p]['3rd'] += 1
            elif rank == 4: stats[p]['4th'] += 1
    return pd.DataFrame.from_dict(stats, orient='index').fillna(0).astype(int).sort_values('1st', ascending=False)

def get_winning_streaks(df):
    return pd.DataFrame()

def get_extreme_stats(df):
    if df.empty: return pd.DataFrame()
    df['total_goals'] = df['p1_score'] + df['p2_score']
    df['diff'] = abs(df['p1_score'] - df['p2_score'])
    highest_scoring = df.loc[df['total_goals'].idxmax()]
    biggest_win = df.loc[df['diff'].idxmax()]
    stats = [
        {'Record': 'Most Goals in Match', 'Value': highest_scoring['total_goals'],
         'Match': f"{highest_scoring['p1_name']} {highest_scoring['p1_score']}-{highest_scoring['p2_score']} {highest_scoring['p2_name']}"},
        {'Record': 'Biggest Win Margin', 'Value': biggest_win['diff'],
         'Match': f"{biggest_win['p1_name']} {biggest_win['p1_score']}-{biggest_win['p2_score']} {biggest_win['p2_name']}"}
    ]
    return pd.DataFrame(stats)

def get_match_history(df, p1, p2):
    mask = ((df['p1_name'] == p1) & (df['p2_name'] == p2)) | \
           ((df['p1_name'] == p2) & (df['p2_name'] == p1))
    return df[mask].sort_values('date', ascending=False)

def get_detailed_h2h(df):
    players = sorted(list(set(df['p1_name'].unique()) | set(df['p2_name'].unique())))
    matrix = pd.DataFrame(index=players, columns=players).fillna('-')
    for p1 in players:
        for p2 in players:
            if p1 == p2: continue
            matches = df[((df['p1_name'] == p1) & (df['p2_name'] == p2)) | 
                         ((df['p1_name'] == p2) & (df['p2_name'] == p1))]
            p1_wins = 0
            for _, m in matches.iterrows():
                if m['p1_name'] == p1 and m['p1_score'] > m['p2_score']: p1_wins += 1
                elif m['p2_name'] == p1 and m['p2_score'] > m['p1_score']: p1_wins += 1
            matrix.loc[p1, p2] = f"Won {p1_wins}"
    return matrix, players

def get_high_scores(df, min_goals=None, min_diff=None):
    mask = pd.Series([True] * len(df))
    if min_goals: mask = mask & ((df['p1_score'] + df['p2_score']) >= min_goals)
    if min_diff: mask = mask & (abs(df['p1_score'] - df['p2_score']) >= min_diff)
    return df[mask]
