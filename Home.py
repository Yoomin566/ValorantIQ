import sys
sys.stdout.reconfigure(encoding='utf-8')
import streamlit as st
import requests
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
HENRIK_KEY = os.getenv("HENRIK_API_KEY") or "paste-your-henrik-key-here"

st.set_page_config(page_title="ValorantIQ", page_icon="🎯", layout="wide")

st.markdown("""
    <style>
    body { background-color: #0f1923; }
    .main { background-color: #0f1923; }
    h1 { color: #ff4655; font-family: 'Arial Black'; letter-spacing: 4px; }
    h2, h3 { color: #ffffff; }
    .stButton>button {
        background-color: #ff4655;
        color: white;
        border: none;
        padding: 10px 30px;
        font-weight: bold;
        letter-spacing: 2px;
        width: 100%;
    }
    .stButton>button:hover { background-color: #ff2233; }
    .stTextInput>div>div>input {
        background-color: #1f2d3a;
        color: white;
        border: 1px solid #ff4655;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center'>⟨ VALORANT IQ ⟩</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#aaaaaa; letter-spacing:3px'>VALORANT PERFORMANCE TRACKER</p>", unsafe_allow_html=True)
st.divider()

col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
with col1:
    username = st.text_input("RIOT USERNAME", value="", placeholder="Enter username")
with col2:
    tagline = st.text_input("TAG", value="", placeholder="TAG")
with col3:
    num_matches = st.selectbox("MATCHES", [5, 10], index=1)
with col4:
    region = st.selectbox("REGION", ["ap", "na", "eu", "kr"], index=0)
with col5:
    st.markdown("<br>", unsafe_allow_html=True)
    search = st.button("ANALYZE ▶")

def get_matches(username, tagline, region="ap", size=10):
    url = f"https://api.henrikdev.xyz/valorant/v3/matches/{region}/{username}/{tagline}?size={size}"
    headers = {"Authorization": HENRIK_KEY}
    response = requests.get(url, headers=headers)
    return response.json()

def get_mmr(username, tagline, region="ap"):
    url = f"https://api.henrikdev.xyz/valorant/v1/mmr/{region}/{username}/{tagline}"
    headers = {"Authorization": HENRIK_KEY}
    response = requests.get(url, headers=headers)
    return response.json()

def calculate_iq_score(kd_ratio, overall_hs_pct, avg_damage, match_results):
    kd_score = min(kd_ratio / 2.0, 1.0) * 30
    hs_score = min(overall_hs_pct / 35.0, 1.0) * 25
    dmg_score = min(avg_damage / 250.0, 1.0) * 25
    kd_list = [m["kd"] for m in match_results]
    variance = max(kd_list) - min(kd_list)
    consistency_score = max(0, 1.0 - (variance / 3.0)) * 20
    total = round(kd_score + hs_score + dmg_score + consistency_score, 1)
    if total >= 80:
        grade, color = "S", "#FFD700"
    elif total >= 65:
        grade, color = "A", "#00ff88"
    elif total >= 50:
        grade, color = "B", "#4488ff"
    elif total >= 35:
        grade, color = "C", "#ff8800"
    else:
        grade, color = "D", "#ff4655"
    return total, grade, color

def generate_coaching(kd_ratio, overall_hs_pct, avg_damage, match_results, agent_counts):
    tips = []
    if kd_ratio >= 1.5:
        tips.append("🔥 Your K/D is excellent! Focus on consistency across all maps.")
    elif kd_ratio >= 1.0:
        tips.append("✅ Solid K/D ratio. Work on closing out rounds to push it higher.")
    else:
        tips.append("⚠️ K/D below 1.0 — focus on survival first, picks second.")
    if overall_hs_pct >= 25:
        tips.append("🎯 Great headshot rate! You have strong aim fundamentals.")
    elif overall_hs_pct >= 15:
        tips.append("🎯 Decent headshots. Try Aim Lab or Kovaak's to push above 25%.")
    else:
        tips.append("🎯 Low headshot %. Aim higher — crosshair placement should be at neck level always.")
    if avg_damage >= 200:
        tips.append("💥 High damage output — you're carrying your team economically.")
    elif avg_damage >= 150:
        tips.append("💥 Average damage is decent. Try to be more aggressive on winning rounds.")
    else:
        tips.append("💥 Low damage — you might be playing too passive. Take more duels.")
    top_agent = max(agent_counts, key=agent_counts.get)
    tips.append(f"🎮 You play {top_agent} the most — consider mastering their full ability kit.")
    kd_list = [m["kd"] for m in match_results]
    if max(kd_list) - min(kd_list) > 2:
        tips.append("📈 Your performance is inconsistent. Focus on mental consistency between matches.")
    else:
        tips.append("📈 Your performance is consistent across matches — great mental game!")
    if len(match_results) >= 3:
        recent_hs = sum([m["hs_pct"] for m in match_results[-3:]]) / 3
        early_hs = sum([m["hs_pct"] for m in match_results[:3]]) / 3
        if recent_hs < early_hs - 5:
            tips.append("📉 Your headshot % is dropping in recent matches — you might be fatigued. Take a break!")
        elif recent_hs > early_hs + 5:
            tips.append("📈 Your headshot % is improving across matches — you're warming up well!")
    high_games = [m for m in match_results if m["kd"] >= 2.0]
    low_games = [m for m in match_results if m["kd"] <= 0.7]
    if len(high_games) >= 2 and len(low_games) >= 2:
        tips.append("👀 You're popping off some games and inting others... are you smurfing or just inconsistent? (¬_¬)")
    elif len(high_games) >= 3:
        tips.append("🤨 Multiple games with KD above 2.0... are you smurfing bro? ( ͡° ͜ʖ ͡°)")
    elif len(low_games) >= 3:
        tips.append("💀 Bro you're inting multiple games in a row... log off and touch grass (╥_╥)")
    elif len(high_games) >= 1 and len(low_games) >= 1:
        tips.append("📊 One game you're a god, next game you're griefing. Pick a personality (ಠ_ಠ)")
    return tips

if search:
    if not username or not tagline:
        st.error("Please enter a username and tag!")
    else:
        with st.spinner("RETRIEVING MATCH DATA..."):
            matches = get_matches(username, tagline, region=region, size=num_matches)
            mmr_data = get_mmr(username, tagline, region=region)

        if "data" not in matches:
            st.error("Player not found or API error! Check username, tag and region.")
        else:
            total_kills = 0
            total_deaths = 0
            total_assists = 0
            total_headshots = 0
            total_bodyshots = 0
            total_legshots = 0
            total_damage = 0
            total_spent = 0
            match_kills = []
            match_deaths = []
            match_damage = []
            match_hs_pct = []
            agents = []
            maps = []
            match_results = []
            rank = ""
            tier = 0
            player_card_url = ""
            rank_icon_url = ""

            mmr = 0
            mmr_rank = "Unranked"
            peak_rank = "Unknown"
            if "data" in mmr_data:
                mmr = mmr_data["data"].get("elo", 0)
                mmr_rank = mmr_data["data"].get("currenttierpatched", "Unranked")
                peak_rank = mmr_data["data"].get("highest_rank", {}).get("patched_tier", "Unknown")

            for match in matches.get("data", []):
                if match.get("metadata", {}).get("mode", "").lower() == "deathmatch":
                    continue
                for player in match["players"]["all_players"]:
                    if player["name"].lower() == username.lower() and player["tag"].lower() == tagline.lower():
                        stats = player["stats"]
                        total_kills += stats["kills"]
                        total_deaths += stats["deaths"]
                        total_assists += stats["assists"]
                        total_headshots += stats["headshots"]
                        total_bodyshots += stats["bodyshots"]
                        total_legshots += stats["legshots"]
                        total_damage += player["damage_made"]
                        total_spent += player["economy"]["spent"]["overall"]
                        match_kills.append(stats["kills"])
                        match_deaths.append(stats["deaths"])
                        match_damage.append(player["damage_made"])
                        total_shots = stats["headshots"] + stats["bodyshots"] + stats["legshots"]
                        hs_pct = round((stats["headshots"] / max(total_shots, 1)) * 100, 1)
                        match_hs_pct.append(hs_pct)
                        agents.append(player["character"])
                        maps.append(match.get("metadata", {}).get("map", "Unknown"))
                        if not rank:
                            rank = player.get("currenttier_patched", "Unranked")
                            tier = player.get("currenttier", 0)
                            player_card_url = player["assets"]["card"]["wide"]
                            rank_icon_url = f"https://media.valorant-api.com/competitivetiers/03621f52-342b-cf4e-4f86-9350a49c6d04/{tier}/largeicon.png"
                        match_results.append({
                            "agent": player["character"],
                            "agent_img": player["assets"]["agent"]["small"],
                            "kills": stats["kills"],
                            "deaths": stats["deaths"],
                            "assists": stats["assists"],
                            "kd": round(stats["kills"] / max(stats["deaths"], 1), 2),
                            "hs_pct": hs_pct,
                            "damage": player["damage_made"],
                            "mode": match.get("metadata", {}).get("mode", "Unknown"),
                            "map": match.get("metadata", {}).get("map", "Unknown")
                        })

            if not match_results:
                st.warning("No valid matches found! Try increasing match count or changing region.")
            else:
                kd_ratio = round(total_kills / max(total_deaths, 1), 2)
                overall_hs_pct = round((total_headshots / max(total_headshots + total_bodyshots + total_legshots, 1)) * 100, 1)
                avg_damage = round(total_damage / max(len(match_results), 1))
                best_match = max(match_results, key=lambda x: x["kills"])
                agent_counts = {}
                for a in agents:
                    agent_counts[a] = agent_counts.get(a, 0) + 1
                map_counts = {}
                for m in maps:
                    map_counts[m] = map_counts.get(m, 0) + 1

                iq_score, grade, grade_color = calculate_iq_score(kd_ratio, overall_hs_pct, avg_damage, match_results)

                # --- PLAYER BANNER ---
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(f"""
                    <div style='display:flex; align-items:center; gap:24px; padding:20px 24px; background:linear-gradient(135deg, #1f2d3a, #0f1923); border:1px solid #ff4655; border-radius:12px; margin-top:10px; margin-bottom:24px'>
                        <img src="{player_card_url}" style='width:160px; height:90px; object-fit:cover; border-radius:8px; flex-shrink:0'/>
                        <div style='flex:1'>
                            <h2 style='color:white; margin:0; font-size:26px'>{username}<span style='color:#ff4655'>#{tagline}</span></h2>
                            <p style='color:#aaaaaa; font-size:13px; margin:4px 0'>MMR Rank: <span style='color:#ff4655'>{mmr_rank}</span> | Peak: <span style='color:#FFD700'>{peak_rank}</span> | MMR: <span style='color:#ffffff'>{mmr}</span></p>
                            <p style='color:#aaaaaa; font-size:13px; margin:0'>Analyzed {len(match_results)} matches</p>
                        </div>
                        <div style='display:flex; flex-direction:column; align-items:center; gap:6px; flex-shrink:0'>
                            <img src="{rank_icon_url}" style='width:72px; height:72px'/>
                            <p style='color:#ff4655; font-size:14px; margin:0; font-weight:bold'>{rank}</p>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                st.divider()

                # --- IQ SCORE ---
                st.markdown("<h3 style='color:#ff4655'>◆ VALORANT IQ SCORE</h3>", unsafe_allow_html=True)
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.markdown(f"""
                        <div style='background:#1f2d3a; border:2px solid {grade_color}; border-radius:16px; padding:30px; text-align:center'>
                            <p style='color:#aaaaaa; font-size:13px; margin:0; letter-spacing:2px'>VALORANT IQ</p>
                            <h1 style='color:{grade_color}; font-size:72px; margin:10px 0; font-family:Arial Black'>{iq_score}</h1>
                            <div style='background:{grade_color}; border-radius:8px; padding:6px 20px; display:inline-block'>
                                <span style='color:#0f1923; font-size:24px; font-weight:bold'>GRADE {grade}</span>
                            </div>
                            <p style='color:#aaaaaa; font-size:11px; margin-top:12px'>out of 100</p>
                        </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    kd_contribution = round(min(kd_ratio / 2.0, 1.0) * 30, 1)
                    hs_contribution = round(min(overall_hs_pct / 35.0, 1.0) * 25, 1)
                    dmg_contribution = round(min(avg_damage / 250.0, 1.0) * 25, 1)
                    kd_list = [m["kd"] for m in match_results]
                    variance = max(kd_list) - min(kd_list)
                    consistency_contribution = round(max(0, 1.0 - (variance / 3.0)) * 20, 1)
                    score_data = pd.DataFrame({
                        "Score": [kd_contribution, hs_contribution, dmg_contribution, consistency_contribution]
                    }, index=["K/D (30pts)", "Headshots (25pts)", "Damage (25pts)", "Consistency (20pts)"])
                    st.bar_chart(score_data, color=["#ff4655"])

                st.divider()

                # --- STATS ROW ---
                st.markdown("<h3 style='color:#ff4655'>◆ PERFORMANCE OVERVIEW</h3>", unsafe_allow_html=True)
                c1, c2, c3, c4, c5, c6 = st.columns(6)
                c1.metric("KILLS", total_kills)
                c2.metric("DEATHS", total_deaths)
                c3.metric("ASSISTS", total_assists)
                c4.metric("K/D RATIO", kd_ratio)
                c5.metric("HS %", f"{overall_hs_pct}%")
                c6.metric("AVG DMG", avg_damage)

                st.divider()

                # --- AI COACHING ---
                st.markdown("<h3 style='color:#ff4655'>◆ COACHING TIPS</h3>", unsafe_allow_html=True)
                tips = generate_coaching(kd_ratio, overall_hs_pct, avg_damage, match_results, agent_counts)
                for tip in tips:
                    st.markdown(f"""
                        <div style='background:#1f2d3a; border-left:3px solid #ff4655; padding:12px 16px; margin:8px 0; border-radius:4px; color:white'>
                            {tip}
                        </div>
                    """, unsafe_allow_html=True)

                st.divider()

                # --- SHOT DISTRIBUTION ---
                st.markdown("<h3 style='color:#ff4655'>◆ SHOT DISTRIBUTION</h3>", unsafe_allow_html=True)
                c1, c2, c3 = st.columns(3)
                c1.metric("🎯 Headshots", total_headshots)
                c2.metric("💪 Bodyshots", total_bodyshots)
                c3.metric("🦵 Legshots", total_legshots)
                shot_data = pd.DataFrame({
                    "Shots": [total_headshots, total_bodyshots, total_legshots]
                }, index=["Headshots", "Bodyshots", "Legshots"])
                st.bar_chart(shot_data, color=["#ff4655"])

                st.divider()

                # --- CHARTS ---
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("<h3 style='color:#ff4655'>◆ KILLS VS DEATHS</h3>", unsafe_allow_html=True)
                    chart_data = pd.DataFrame({
                        "Kills": match_kills,
                        "Deaths": match_deaths,
                    }, index=range(1, len(match_kills)+1))
                    st.bar_chart(chart_data, color=["#ff4655", "#4488ff"])
                with col2:
                    st.markdown("<h3 style='color:#ff4655'>◆ HEADSHOT % TREND</h3>", unsafe_allow_html=True)
                    hs_data = pd.DataFrame({
                        "HS %": match_hs_pct
                    }, index=range(1, len(match_hs_pct)+1))
                    st.line_chart(hs_data, color=["#ff4655"])

                st.divider()

                # --- DAMAGE ---
                st.markdown("<h3 style='color:#ff4655'>◆ DAMAGE PER MATCH</h3>", unsafe_allow_html=True)
                dmg_data = pd.DataFrame({
                    "Damage": match_damage
                }, index=range(1, len(match_damage)+1))
                st.bar_chart(dmg_data, color=["#ff4655"])

                st.divider()

                # --- MATCH HISTORY ---
                st.markdown("<h3 style='color:#ff4655'>◆ MATCH HISTORY</h3>", unsafe_allow_html=True)
                for i, m in enumerate(match_results):
                    kd_color = "🟢" if m["kd"] >= 1.0 else "🔴"
                    col1, col2 = st.columns([1, 8])
                    with col1:
                        st.image(m["agent_img"], width=40)
                    with col2:
                        st.markdown(f"{kd_color} **Match {i+1}** | {m['mode']} | {m['map']} | {m['agent']} | {m['kills']}K / {m['deaths']}D / {m['assists']}A | KD: {m['kd']} | HS: {m['hs_pct']}% | DMG: {m['damage']}")

                st.divider()

                # --- BEST MATCH ---
                st.markdown("<h3 style='color:#ff4655'>◆ BEST MATCH</h3>", unsafe_allow_html=True)
                st.success(f"🏆 Best performance: {best_match['kills']} kills as {best_match['agent']} | KD: {best_match['kd']} | HS%: {best_match['hs_pct']}%")

                st.divider()

                # --- AGENTS & MAPS ---
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("<h3 style='color:#ff4655'>◆ AGENTS PLAYED</h3>", unsafe_allow_html=True)
                    for agent, count in sorted(agent_counts.items(), key=lambda x: -x[1]):
                        st.markdown(f"🎮 **{agent}** — played {count} time{'s' if count > 1 else ''}")
                with col2:
                    st.markdown("<h3 style='color:#ff4655'>◆ MAPS PLAYED</h3>", unsafe_allow_html=True)
                    for map_name, count in sorted(map_counts.items(), key=lambda x: -x[1]):
                        st.markdown(f"🗺️ **{map_name}** — played {count} time{'s' if count > 1 else ''}")

                st.divider()

                # --- ECONOMY ---
                st.markdown("<h3 style='color:#ff4655'>◆ ECONOMY</h3>", unsafe_allow_html=True)
                avg_spent = round(total_spent / max(len(match_results), 1))
                st.metric("AVG CREDITS SPENT PER MATCH", avg_spent)