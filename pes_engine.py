import pandas as pd
import numpy as np
from functools import cmp_to_key

# --- 1. توابع مربوط به منطق بازی و جدول ---

def check_h2h_aggregate(df, season_id, p1, p2):
    matches = df[(df['season_id'] == season_id) & 
                 (((df['p1_name'] == p1) & (df['p2_name'] == p2)) | 
                  ((df['p1_name'] == p2) & (df['p2_name'] == p1)))]
    
    p1_goals = 0
    p2_goals = 0
    
    for _, row in matches.iterrows():
        if row['p1_name'] == p1:
            p1_goals += row['p1_score']
            p2_goals += row['p2_score']
        else:
            p1_goals += row['p2_score']
            p2_goals += row['p1_score']
            
    if p1_goals > p2_goals: return p1
    if p2_goals > p1_goals: return p2
    return None

def get_season_table(df, season_id):
    season_df = df[df['season_id'] == season_id]
    players = set(season_df['p1_name'].unique()) | set(season_df['p2_name'].unique())
    data = []

    for p in players:
        matches = season_df[(season_df['p1_name'] == p) | (season_df['p2_name'] == p)]
        points = 0; gf = 0; ga = 0
        
        for _, row in matches.iterrows():
            if row['p1_name'] == p:
                gf += row['p1_score']; ga += row['p2_score']
                if row['p1_score'] > row['p2_score']: points += 3
                elif row['p1_score'] == row['p2_score']: points += 1
            else:
                gf += row['p2_score']; ga += row['p1_score']
                if row['p2_score'] > row['p1_score']: points += 3
                elif row['p2_score'] == row['p1_score']: points += 1
        
        data.append({'Player': p, 'Points': points, 'GD': gf - ga, 'GF': gf, 'GA': ga})

    def compare_players(item1, item2):
        if item1['Points'] != item2['Points']: return item1['Points'] - item2['Points']
        if item1['GD'] != item2['GD']: return item1['GD'] - item2['GD']
        if item1['GF'] != item2['GF']: return item1['GF'] - item2['GF']
        
        p1, p2 = item1['Player'], item2['Player']
        h2h_winner = check_h2h_aggregate(df, season_id, p1, p2)
        
        if h2h_winner == p1: return 1
        if h2h_winner == p2: return -1
        return 0

    sorted_data = sorted(data, key=cmp_to_key(compare_players), reverse=True)
    
    df_table = pd.DataFrame(sorted_data)
    
    # چیدمان ستون‌ها
    df_table = df_table[['Player', 'Points', 'GF', 'GA', 'GD']]
    
    # تغییر نام ستون‌ها
    df_table = df_table.rename(columns={'GF': '+', 'GA': '-'})
    
    # شروع ایندکس از ۱ (تغییر جدید)
    df_table.index = range(1, len(df_table) + 1)
    
    return df_table

    def compare_players(item1, item2):
        if item1['Points'] != item2['Points']: return item1['Points'] - item2['Points']
        if item1['GD'] != item2['GD']: return item1['GD'] - item2['GD']
        if item1['GF'] != item2['GF']: return item1['GF'] - item2['GF']
        
        p1, p2 = item1['Player'], item2['Player']
        h2h_winner = check_h2h_aggregate(df, season_id, p1, p2)
        
        if h2h_winner == p1: return 1
        if h2h_winner == p2: return -1
        return 0

    sorted_data = sorted(data, key=cmp_to_key(compare_players), reverse=True)
    
    # تغییر ۲: ساختن جدول، مرتب‌سازی ستون‌ها و تغییر نام
    df_table = pd.DataFrame(sorted_data)
    
    # چیدمان ستون‌ها: اول بازیکن و امتیاز، بعد گل زده و خورده و تفاضل
    df_table = df_table[['Player', 'Points', 'GF', 'GA', 'GD']]
    
    # تغییر نام ستون‌ها به نمادهای خواسته شده
    df_table = df_table.rename(columns={'GF': '+', 'GA': '-'})
    
    return df_table

    def compare_players(item1, item2):
        if item1['Points'] != item2['Points']: return item1['Points'] - item2['Points']
        if item1['GD'] != item2['GD']: return item1['GD'] - item2['GD']
        if item1['GF'] != item2['GF']: return item1['GF'] - item2['GF']
        
        p1, p2 = item1['Player'], item2['Player']
        h2h_winner = check_h2h_aggregate(df, season_id, p1, p2)
        
        if h2h_winner == p1: return 1
        if h2h_winner == p2: return -1
        return 0

    sorted_data = sorted(data, key=cmp_to_key(compare_players), reverse=True)
    return pd.DataFrame(sorted_data)

def get_champion(df, season_id):
    table = get_season_table(df, season_id)
    if table.empty: return "No Data"
    
    first = table.iloc[0]
    if len(table) == 1 or first['Points'] > table.iloc[1]['Points']:
        return first['Player']
    
    second = table.iloc[1]
    h2h_winner = check_h2h_aggregate(df, season_id, first['Player'], second['Player'])
    if h2h_winner: return h2h_winner
    
    if first['GD'] > second['GD']: return first['Player']
    if second['GD'] > first['GD']: return second['Player']
    if first['GF'] > second['GF']: return first['Player']
    
    return first['Player']

# --- 2. توابع مربوط به آمار کلی و جام‌ها ---

def get_all_time_summary(df):
    seasons = df['season_id'].unique()
    champ_counts = {}
    golden_cups = {}
    ultra_golden_cups = {}
    
    # --- بخش ۱: محاسبه جام‌ها ---
    for s in seasons:
        c_name = get_champion(df, s)
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
            if wins == total_games and total_games > 0:
                ultra_golden_cups[c_name] = ultra_golden_cups.get(c_name, 0) + 1
            else:
                golden_cups[c_name] = golden_cups.get(c_name, 0) + 1

    # --- بخش ۲: محاسبه آمار کلی ---
    players = set(df['p1_name'].unique()) | set(df['p2_name'].unique())
    stats_data = []
    
    for p in players:
        matches = df[(df['p1_name'] == p) | (df['p2_name'] == p)]
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
        
        # محاسبه میانگین‌ها
        total_matches = wins + draws + losses
        if total_matches > 0:
            avg_gf = round(total_gf / total_matches, 2)
            avg_ga = round(total_ga / total_matches, 2)
        else:
            avg_gf = 0; avg_ga = 0

        stats_data.append({
            'Player': p,
            'Championships': champ_counts.get(p, 0),
            'Ultra Golden': ultra_golden_cups.get(p, 0),
            'Golden Cup': golden_cups.get(p, 0),
            'Wins': wins, 'Draws': draws, 'Losses': losses,
            'Total Points': total_points,
            'XG_F': avg_gf, 'XG_A': avg_ga,
            '+': total_gf, '-': total_ga, 'GD': total_gf - total_ga
        })
        
    summary_df = pd.DataFrame(stats_data)
    
    # لگاسی (جام‌های دستی)
    legacy_ultra_golden = {'Mehdi': 3}
    if 'Ultra Golden' not in summary_df.columns: summary_df['Ultra Golden'] = 0
    summary_df['Ultra Golden'] += summary_df['Player'].map(legacy_ultra_golden).fillna(0).astype(int)

    # محاسبه درصدها
    total_games_col = summary_df['Wins'] + summary_df['Draws'] + summary_df['Losses']
    summary_df['Win %'] = (summary_df['Wins'] / total_games_col * 100).fillna(0).round(1)
    summary_df['Draw %'] = (summary_df['Draws'] / total_games_col * 100).fillna(0).round(1)
    summary_df['Loss %'] = (summary_df['Losses'] / total_games_col * 100).fillna(0).round(1)

    # --- بخش ۳: چیدمان و مرتب‌سازی ---
    
    column_order = [
        'Player', 'Championships', 'Ultra Golden', 'Golden Cup',
        'Wins', 'Draws', 'Losses',
        'Win %', 'Draw %', 'Loss %',
        'XG_F', 'XG_A',
        '+', '-', 'GD',
        'Total Points'
    ]
    summary_df = summary_df[column_order]

    # تغییر اصلی اینجاست: مرتب‌سازی بر اساس امتیاز و سپس تفاضل گل (هر دو نزولی)
    summary_df = summary_df.sort_values(by=['Total Points', 'GD'], ascending=[False, False])

    # شروع ایندکس از ۱
    summary_df.index = range(1, len(summary_df) + 1)

    return summary_df

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

            p1_wins = 0; p2_wins = 0; draws = 0
            p1_goals = 0; p2_goals = 0

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
                p1_rate = (p1_wins / total_games) * 100
                p2_rate = (p2_wins / total_games) * 100
                details = f"{p1}: {p1_wins} | {p2}: {p2_wins} | D: {draws}"
                
                table_data.append({
                    'Matchup': f"{p1} vs {p2}",
                    'Matches': total_games,
                    'P1 Goals': p1_goals, 'P2 Goals': p2_goals,
                    'P1 Win %': f"{p1_rate:.1f}%", 'P2 Win %': f"{p2_rate:.1f}%",
                    'Detailed Stats': details
                })
    
    return pd.DataFrame(table_data), win_matrix

def get_match_history(df, p1, p2, target='all'):
    """
    نمایش نتایج بازی‌های مستقیم بین دو نفر.
    target: می‌تواند شماره فصل (مثلا 1) یا رشته 'all' باشد.
    """
    # 1. فیلتر کردن بر اساس فصل
    if target != 'all':
        matches_df = df[df['season_id'] == target]
    else:
        matches_df = df

    # 2. پیدا کردن بازی‌های مشترک (چه رفت و چه برگشت)
    mask = (
        ((matches_df['p1_name'] == p1) & (matches_df['p2_name'] == p2)) |
        ((matches_df['p1_name'] == p2) & (matches_df['p2_name'] == p1))
    )
    relevant_matches = matches_df[mask]

    data = []
    for _, row in relevant_matches.iterrows():
        # تشخیص اینکه کدام امتیاز مال p1 (ورودی تابع) است
        if row['p1_name'] == p1:
            score1 = row['p1_score']
            score2 = row['p2_score']
        else:
            # اگر در اکسل جایشان برعکس بود (p1 ما در اکسل p2 بود)
            score1 = row['p2_score']
            score2 = row['p1_score']

        # ساخت دیکشنری با کلیدهایی برابر با نام بازیکنان
        data.append({p1: score1, p2: score2})

    # 3. ساخت دیتافریم
    result_df = pd.DataFrame(data)

    # مدیریت حالت خالی (اگر هیچ بازی‌ای پیدا نشد)
    if result_df.empty:
        return pd.DataFrame(columns=[p1, p2])

    # تنظیم ایندکس از 1
    result_df.index = range(1, len(result_df) + 1)

    return result_df



def get_high_scores(df, p1=None, p2=None, min_goals=None, min_diff=None):
    """
    پیدا کردن بازی‌های خاص با فیلترهای اختیاری.
    همراه با چاپ ۳ نتیجه سنگین (بر اساس تفاضل گل) در ابتدای اجرا.
    """
    
    # 1. کپی و محاسبات اولیه
    temp_df = df.copy()
    temp_df['goal_diff'] = abs(temp_df['p1_score'] - temp_df['p2_score'])
    
    # 2. ساخت ماسک فیلترها
    final_mask = pd.Series([True] * len(temp_df), index=temp_df.index)
    
    if min_goals is not None:
        final_mask &= ((temp_df['p1_score'] >= min_goals) | (temp_df['p2_score'] >= min_goals))
        
    if min_diff is not None:
        final_mask &= (temp_df['goal_diff'] >= min_diff)
        
    if p1 and p2:
        mask = ((temp_df['p1_name'] == p1) & (temp_df['p2_name'] == p2)) | \
               ((temp_df['p1_name'] == p2) & (temp_df['p2_name'] == p1))
        final_mask &= mask
    elif p1 and not p2:
        final_mask &= ((temp_df['p1_name'] == p1) | (temp_df['p2_name'] == p1))
    elif p2 and not p1:
        final_mask &= ((temp_df['p1_name'] == p2) | (temp_df['p2_name'] == p2))

    # 3. اعمال فیلتر
    filtered_df = temp_df[final_mask]

    # --- بخش جدید: چاپ ۳ نتیجه سنگین ---
    if not filtered_df.empty:
        # مرتب‌سازی بر اساس تفاضل گل (نزولی) برای پیدا کردن سنگین‌ترین‌ها
        top_3 = filtered_df.sort_values(by='goal_diff', ascending=False).head(3)
        
        print("--- Top 3 Heaviest Matches (in this search) ---")
        for _, row in top_3.iterrows():
            # تشخیص برنده برای فرمت چاپ: Winner: 7 vs 1 : Loser
            if row['p1_score'] > row['p2_score']:
                w_name, l_name = row['p1_name'], row['p2_name']
                w_score, l_score = row['p1_score'], row['p2_score']
            else:
                w_name, l_name = row['p2_name'], row['p1_name']
                w_score, l_score = row['p2_score'], row['p1_score']
            
            print(f"{w_name}: {w_score} vs {l_score} : {l_name}")
        print("------------------------------------------------\n")
    # -----------------------------------

    data = []
    for _, row in filtered_df.iterrows():
        n1, n2 = row['p1_name'], row['p2_name']
        s1, s2 = row['p1_score'], row['p2_score']

        # منطق نمایش در دیتافریم (Sort Display)
        swap = False
        if p1 and p2:
            if n1 == p2: swap = True
        elif p1:
            if n1 != p1: swap = True
        elif p2:
            if n1 != p2: swap = True
        else:
            if s2 > s1: swap = True

        if swap:
            n1, n2 = n2, n1
            s1, s2 = s2, s1

        data.append({
            'p1': n1,
            'p2': n2,
            'Score1': f"{n1}:{s1}",
            'Score2': f"{n2}:{s2}",
            'Diff': abs(s1 - s2)
        })

    # 4. خروجی نهایی
    result_df = pd.DataFrame(data)
    
    if result_df.empty:
        return pd.DataFrame(columns=['p1', 'p2', 'Score1', 'Score2', 'Diff'])

    result_df.index = range(1, len(result_df) + 1)
    return result_df


def get_extreme_stats(df):
    """
    نمایش ترین‌های لیگ (آمار خوب و آمار بد).
    شامل: بیشترین برد، کمترین باخت، بیشترین گل زده، کمترین گل خورده (خوب)
    و برعکس آن‌ها (بد).
    """
    # 1. گرفتن خلاصه آمار همه بازیکنان
    summary = get_all_time_summary(df)
    
    # 2. تعریف لیست مواردی که باید محاسبه شوند
    # ساختار: عنوان آمار، نام ستون در جدول خلاصه، روش محاسبه (max یا min)
    metrics = [
        # --- آمار خوب ---
        {'Type': 'Good Stats', 'Title': 'Most Wins',            'Col': 'Wins',   'Func': 'max'},
        {'Type': 'Good Stats', 'Title': 'Fewest Losses',        'Col': 'Losses', 'Func': 'min'},
        {'Type': 'Good Stats', 'Title': 'Most Goals Scored',    'Col': '+',      'Func': 'max'},
        {'Type': 'Good Stats', 'Title': 'Fewest Goals Conceded','Col': '-',      'Func': 'min'},
        
        # --- آمار بد ---
        {'Type': 'Bad Stats',  'Title': 'Fewest Wins',          'Col': 'Wins',   'Func': 'min'},
        {'Type': 'Bad Stats',  'Title': 'Most Losses',          'Col': 'Losses', 'Func': 'max'},
        {'Type': 'Bad Stats',  'Title': 'Fewest Goals Scored',  'Col': '+',      'Func': 'min'},
        {'Type': 'Bad Stats',  'Title': 'Most Goals Conceded',  'Col': '-',      'Func': 'max'},
    ]
    
    data = []
    
    for item in metrics:
        col = item['Col']
        
        # پیدا کردن مقدار هدف (بیشترین یا کمترین)
        if item['Func'] == 'max':
            target_value = summary[col].max()
        else:
            target_value = summary[col].min()
            
        # پیدا کردن بازیکنانی که این مقدار را دارند (مدیریت حالت تساوی)
        players = summary[summary[col] == target_value]['Player'].tolist()
        players_str = ", ".join(players)
        
        data.append({
            'Category': item['Type'],
            'Statistic': item['Title'],
            'Value': target_value,
            'Player(s)': players_str
        })
        
    # 3. ساخت دیتافریم خروجی
    result_df = pd.DataFrame(data)
    
    # ایندکس از 1
    result_df.index = range(1, len(result_df) + 1)
    
    return result_df


def get_winning_streaks(df):
    """
    محاسبه قهرمانی‌های متوالی (Winning Streaks).
    خروجی نشان می‌دهد هر بازیکن چند بار توانسته به یک تعداد خاص (مثلاً ۲ یا ۳ بار)
    پشت سر هم قهرمان شود.
    """
    # 1. دریافت لیست فصل‌ها به ترتیب
    seasons = sorted(df['season_id'].unique())
    if len(seasons) == 0:
        return pd.DataFrame(columns=['Player', 'Consecutive Titles', 'Count', 'Description'])

    # 2. ساخت تایم‌لاین قهرمانان
    timeline = []
    for s in seasons:
        champ = get_champion(df, s)
        timeline.append(champ)

    # 3. شناسایی توالی‌ها
    streaks_found = [] # لیست دیکشنری‌ها: {'Player': ..., 'Length': ...}
    
    if not timeline:
        return pd.DataFrame()

    current_player = timeline[0]
    current_length = 1
    
    for i in range(1, len(timeline)):
        next_player = timeline[i]
        
        if next_player == current_player:
            current_length += 1
        else:
            # اگر توالی قطع شد، چک کن آیا بیشتر از ۱ بوده؟
            if current_length > 1:
                streaks_found.append({'Player': current_player, 'Length': current_length})
            
            # ریست کردن برای نفر بعدی
            current_player = next_player
            current_length = 1
            
    # چک کردن آخرین نفر لیست (چون حلقه تمام می‌شود)
    if current_length > 1:
        streaks_found.append({'Player': current_player, 'Length': current_length})
        
    # 4. اگر هیچ قهرمانی متوالی‌ای پیدا نشد
    if not streaks_found:
        print("No consecutive championships found yet.")
        return pd.DataFrame(columns=['Player', 'Consecutive Titles', 'Count', 'Description'])

    # 5. تجمیع داده‌ها (Aggregation)
    # تبدیل به دیتافریم برای راحت‌تر شمردن
    temp_df = pd.DataFrame(streaks_found)
    
    # گروه‌بندی بر اساس نام بازیکن و طول توالی
    # مثال: مهدی، توالی ۲ تایی -> چند بار تکرار شده؟
    summary_df = temp_df.groupby(['Player', 'Length']).size().reset_index(name='Count')
    
    # تغییر نام ستون برای وضوح
    summary_df = summary_df.rename(columns={'Length': 'Consecutive Titles'})
    
    # ساخت ستون توضیحات متنی
    summary_df['Description'] = summary_df.apply(
        lambda x: f"{x['Count']} time(s): {x['Consecutive Titles']} seasons in a row", axis=1
    )
    
    # 6. مرتب‌سازی: اولویت با تعداد قهرمانی متوالی بیشتر (مثلاً هتریک بالاتر از دبل)
    summary_df = summary_df.sort_values(by=['Consecutive Titles', 'Count'], ascending=[False, False])
    
    # شروع ایندکس از ۱
    summary_df.index = range(1, len(summary_df) + 1)
    
    return summary_df

def get_podium_stats(df):
    """
    محاسبه تعداد دفعات کسب رتبه‌های اول تا چهارم توسط هر بازیکن.
    """
    # لیست تمام بازیکنان
    all_players = list(set(df['p1_name'].unique()) | set(df['p2_name'].unique()))
    
    # ساخت دیکشنری اولیه برای ذخیره آمار
    # ساختار: {'Mehdi': {1: 0, 2: 0, 3: 0, 4: 0}, ...}
    stats = {p: {1: 0, 2: 0, 3: 0, 4: 0} for p in all_players}
    
    seasons = sorted(df['season_id'].unique())
    
    for s in seasons:
        # دریافت جدول رده‌بندی آن فصل
        table = get_season_table(df, s)
        
        # پیمایش جدول (ایندکس جدول رده‌بندی همان رتبه است)
        for rank, row in table.iterrows():
            player = row['Player']
            
            # فقط رتبه‌های ۱ تا ۴ را می‌شماریم
            if rank <= 4:
                stats[player][rank] += 1
                
    # تبدیل دیکشنری به دیتافریم
    # orient='index' یعنی کلیدهای دیکشنری (اسم بازیکنان) بشوند ردیف‌ها
    result_df = pd.DataFrame.from_dict(stats, orient='index')
    
    # تغییر نام ستون‌ها
    result_df.columns = ['1st Place', '2nd Place', '3rd Place', '4th Place']
    
    # مرتب‌سازی: اول بر اساس تعداد قهرمانی، بعد نایب قهرمانی و ...
    result_df = result_df.sort_values(
        by=['1st Place', '2nd Place', '3rd Place', '4th Place'], 
        ascending=False
    )
    
    return result_df