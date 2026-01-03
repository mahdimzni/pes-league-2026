import streamlit as st
import pandas as pd
import pes_engine as pes
import time

# تنظیمات صفحه (عنوان تب مرورگر و آیکون)
st.set_page_config(page_title="PES League Hub", page_icon="⚽", layout="wide")

# استایل‌دهی ساده
st.markdown("""
<style>
    .big-font { font-size:20px !important; }
    .stAlert { direction: ltr; }
</style>
""", unsafe_allow_html=True)

# عنوان اصلی سایت
st.title("⚽ PES 2026 Champions League Hub")
st.markdown("---")

# 1. بارگذاری داده‌ها از گوگل شیت
try:
    # کش کردن داده‌ها (همان تنظیماتی که دوست داشتید)
    @st.cache_data(ttl=60)  # زمان کش را روی 1 دقیقه گذاشتم که سریعتر هم باشد
    def load_data():
        # لینک اصلی گوگل شیت
        base_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRail3nDcqqJqeIQetw8qS0SO4rT4TH4atQ6rhUQW3aHrE64ERb9Np_FPQtil0kZw/pub?output=xlsx"
        
        # ترفند مهم: اضافه کردن یک عدد تصادفی به تهِ لینک برای دور زدن کش گوگل
        final_url = f"{base_url}&v={time.time()}"
        
        return pd.read_excel(final_url)
    
    df = load_data()
    
    # دکمه رفرش دستی در سایدبار
    if st.sidebar.button('🔄 Update Data'):
        st.cache_data.clear()
        st.rerun()
        
    st.sidebar.success("Database Connected (Online) ✅")
    
except Exception as e:
    st.error(f"Error loading data from Google Sheets: {e}")
    st.stop()

# 2. منوی کناری (Sidebar)
st.sidebar.header("Navigation")
menu_options = ["League Table", "All-Time Legends", "Stats & Streaks", "Head-to-Head", "Match Finder"]
choice = st.sidebar.radio("Go to:", menu_options)

# --- بخش اول: جدول لیگ ---
if choice == "League Table":
    st.header("🏆 Season Standings")
    
    # انتخاب فصل
    all_seasons = sorted(df['season_id'].unique())
    if all_seasons:
        # انتخاب آخرین فصل به صورت پیش‌فرض
        selected_season = st.selectbox("Select Season:", all_seasons, index=len(all_seasons)-1)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader(f"Table - Season {selected_season}")
            # فراخوانی جدول (با ستون جدید Matches)
            table = pes.get_season_table(df, selected_season)
            if not table.empty:
                st.dataframe(table, use_container_width=True)
            else:
                st.info("No matches played in this season yet.")
            
        with col2:
            st.subheader("Champion Status")
            champ = pes.get_champion(df, selected_season)
            
            # --- هماهنگ‌سازی با موتور جدید ---
            # اگر پیام نابرابری بازی‌ها یا نبود داده برگشت داده شد:
            if "there is no champion" in champ or champ == "No Data":
                st.warning(f"⚠️ {champ}")
                st.caption("All players must have equal matches to declare a champion.")
            else:
                # اگر قهرمان معتبر بود
                st.success(f"🥇 {champ}")
                st.balloons()
                
    else:
        st.warning("No seasons found in the database.")

# --- بخش دوم: تالار افتخارات ---
elif choice == "All-Time Legends":
    st.header("🌟 Hall of Fame")
    
    tab1, tab2 = st.tabs(["General Summary", "Podium Finishes"])
    
    with tab1:
        st.subheader("🌍 All-Time Table (Sorted by Point per Match)")
        summary = pes.get_all_time_summary(df)
        
        # نمایش جدول با هایلایت روی ستون جدید Point per Match
        st.dataframe(
            summary.style.background_gradient(subset=['Point per Match'], cmap="Greens"), 
            use_container_width=True, 
            height=600
        )
        st.info("💡 Note: Rankings are now based on 'Point per Match' (Average Points).")
        
    with tab2:
        st.subheader("🏅 Podium Finishes (1st - 4th)")
        st.dataframe(pes.get_podium_stats(df), use_container_width=True)

# --- بخش سوم: آمار و رکوردها ---
elif choice == "Stats & Streaks":
    st.header("📊 Deep Analytics")
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🔥 Winning Streaks")
        streaks = pes.get_winning_streaks(df)
        if not streaks.empty:
            st.table(streaks)
        else:
            st.info("No consecutive title streaks yet.")
        
    with c2:
        st.subheader("📈 League Records (Rates & Averages)")
        # این تابع الان مقادیر درصدی و میانگین را برمی‌گرداند
        st.table(pes.get_extreme_stats(df))

# --- بخش چهارم: بازی‌های رو در رو ---
elif choice == "Head-to-Head":
    st.header("⚔️ Head-to-Head Analysis")
    
    players = sorted(list(set(df['p1_name'].unique()) | set(df['p2_name'].unique())))
    
    if len(players) >= 2:
        col1, col2 = st.columns(2)
        p1 = col1.selectbox("Player 1", players, index=0)
        p2 = col2.selectbox("Player 2", players, index=1)
        
        if p1 != p2:
            st.markdown(f"### History: {p1} vs {p2}")
            history = pes.get_match_history(df, p1, p2)
            st.dataframe(history, use_container_width=True)
        else:
            st.warning("Please select two different players.")
    else:
        st.warning("Not enough players data yet.")

    st.markdown("---")
    st.markdown("### 🌐 All Matchups Matrix")
    h2h_df, _ = pes.get_detailed_h2h(df)
    st.dataframe(h2h_df, use_container_width=True)

# --- بخش پنجم: جستجوی بازی ---
elif choice == "Match Finder":
    st.header("🔎 Match Finder")
    st.write("Find specific games based on goals or difference.")
    
    col1, col2 = st.columns(2)
    diff_val = col1.slider("Minimum Goal Difference:", 0, 10, 4)
    goals_val = col2.slider("Minimum Goals Scored:", 0, 15, 0)
    
    g_val = goals_val if goals_val > 0 else None
    d_val = diff_val if diff_val > 0 else None
    
    if st.button("Search Matches"):
        results = pes.get_high_scores(df, min_goals=g_val, min_diff=d_val)
        if not results.empty:
            st.dataframe(results, use_container_width=True)
        else:
            st.warning("No matches found with these criteria.")

# فوتر سایت
st.markdown("---")
st.caption("PES 2026 League Engine | Live Data from Google Sheets")
