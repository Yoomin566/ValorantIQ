import sys
sys.stdout.reconfigure(encoding='utf-8')
import streamlit as st
import requests
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
HENRIK_KEY = os.getenv("HENRIK_API_KEY") or "HDEV-2a59985a-9737-4ca2-af68-cec7d0cf4742"

st.set_page_config(page_title="ValorantIQ — Compare", page_icon="⚔️", layout="wide")

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

st.markdown("<h1 style='text-align:center'>⚔️ PLAYER COMPARISON</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#aaaaaa; letter-spacing:3px'>WHO WINS?</p>", unsafe_allow_html=True)
st.divider()

col1, col2, col3 = st.columns([2, 1, 2])
with col1:
    st.markdown("<h3 style='color:#ff4655; text-align:center'>PLAYER 1</h3>", unsafe_allow_html=True)
    p1_username = st.text_input("Username", key="p1_username", placeholder="Enter username")
    p1_tag = st.text_input("Tag", key="p1_tag", placeholder="TAG")
with col2:
    st.markdown("<h3 style='color:#aaaaaa; text-align:center; margin-top:40px'>VS</h3>", unsafe_allow_html=True)
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    compare = st.button("COMPARE ⚔️")
with col3:
    st.markdown("<h3 style='color:#4488ff; text-align:center'>PLAYER 2</h3>", unsafe_allow_html=True)
    p2_username = st.text_input("Username", key="p2_username", placeholder="Enter username")
    p2_tag = st.text_input("Tag", key="p2_tag", placeholder="TAG")

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

def get_player_stats(username, tagline):
    matches = get_matches(username, tagline)
    mmr_data = get_mmr(username, tagline)

    if "data" not in matches:
        return None

    total_kills = 0
    total_deaths = 0
    total_assists = 0
    total_headshots = 0
    total_bodyshots = 0
    total_legshots = 0
    total_damage = 0
    agents = []
    match_results = []
    rank = "Unranked"
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
                agents.append(player["character"])
                if not rank or rank == "Unranked":
                    rank = player.get("currenttier_patched", "Unranked")
                    tier = player.get("currenttier", 0)
                    player_card_url = player["assets"]["card"]["wide"]
                    rank_icon_url = f"https://media.valorant-api.com/competitivetiers/03621f52-342b-cf4e-4f86-9350a49c6d04/{tier}/largeicon.png"
                total_shots = stats["headshots"] + stats["bodyshots"] + stats["legshots"]
                hs_pct = round((stats["headshots"] / max(total_shots, 1)) * 100, 1)
                match_results.append({
                    "kd": round(stats["kills"] / max(stats["deaths"], 1), 2),
                    "hs_pct": hs_pct,
                    "damage": player["damage_made"]
                })

    if not match_results:
        return None

    kd_ratio = round(total_kills / max(total_deaths, 1), 2)
    overall_hs_pct = round((total_headshots / max(total_headshots + total_bodyshots + total_legshots, 1)) * 100, 1)
    avg_damage = round(total_damage / max(len(match_results), 1))
    agent_counts = {}
    for a in agents:
        agent_counts[a] = agent_counts.get(a, 0) + 1
    top_agent = max(agent_counts, key=agent_counts.get)

    kd_score = min(kd_ratio / 2.0, 1.0) * 30
    hs_score = min(overall_hs_pct / 35.0, 1.0) * 25
    dmg_score = min(avg_damage / 250.0, 1.0) * 25
    kd_list = [m["kd"] for m in match_results]
    variance = max(kd_list) - min(kd_list)
    consistency_score = max(0, 1.0 - (variance / 3.0)) * 20
    iq_score = round(kd_score + hs_score + dmg_score + consistency_score, 1)

    if iq_score >= 80:
        grade, grade_color = "S", "#FFD700"
    elif iq_score >= 65:
        grade, grade_color = "A", "#00ff88"
    elif iq_score >= 50:
        grade, grade_color = "B", "#4488ff"
    elif iq_score >= 35:
        grade, grade_color = "C", "#ff8800"
    else:
        grade, grade_color = "D", "#ff4655"

    return {
        "username": username,
        "tagline": tagline,
        "rank": rank,
        "mmr": mmr,
        "mmr_rank": mmr_rank,
        "peak_rank": peak_rank,
        "rank_icon_url": rank_icon_url,
        "player_card_url": player_card_url,
        "kd_ratio": kd_ratio,
        "hs_pct": overall_hs_pct,
        "avg_damage": avg_damage,
        "total_kills": total_kills,
        "total_deaths": total_deaths,
        "total_assists": total_assists,
        "top_agent": top_agent,
        "iq_score": iq_score,
        "grade": grade,
        "grade_color": grade_color,
        "matches": len(match_results)
    }

def winner_badge(val1, val2, reverse=False):
    if reverse:
        if val1 < val2:
            return "🏆", ""
        elif val2 < val1:
            return "", "🏆"
    else:
        if val1 > val2:
            return "🏆", ""
        elif val2 > val1:
            return "", "🏆"
    return "🤝", "🤝"

if compare:
    if not p1_username or not p1_tag or not p2_username or not p2_tag:
        st.error("Please fill in all fields!")
    else:
        col1, col2 = st.columns(2)
        with col1:
            with st.spinner(f"Fetching {p1_username}..."):
                p1 = get_player_stats(p1_username, p1_tag)
        with col2:
            with st.spinner(f"Fetching {p2_username}..."):
                p2 = get_player_stats(p2_username, p2_tag)

        if not p1:
            st.error(f"Could not find {p1_username}#{p1_tag}")
        elif not p2:
            st.error(f"Could not find {p2_username}#{p2_tag}")
        else:
            # --- PLAYER BANNERS ---
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                    <div style='display:flex; align-items:center; gap:16px; padding:16px; background:linear-gradient(135deg, #1f2d3a, #0f1923); border:2px solid #ff4655; border-radius:12px'>
                        <img src="{p1['player_card_url']}" style='width:120px; height:68px; object-fit:cover; border-radius:6px'/>
                        <div style='flex:1'>
                            <h3 style='color:white; margin:0'>{p1['username']}<span style='color:#ff4655'>#{p1['tagline']}</span></h3>
                            <p style='color:#aaaaaa; margin:2px 0; font-size:12px'>Rank: {p1['rank']}</p>
                            <p style='color:#aaaaaa; margin:2px 0; font-size:12px'>MMR: {p1['mmr_rank']} ({p1['mmr']}) | Peak: <span style='color:#FFD700'>{p1['peak_rank']}</span></p>
                        </div>
                        <img src="{p1['rank_icon_url']}" style='width:50px; height:50px'/>
                    </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                    <div style='display:flex; align-items:center; gap:16px; padding:16px; background:linear-gradient(135deg, #1f2d3a, #0f1923); border:2px solid #4488ff; border-radius:12px'>
                        <img src="{p2['player_card_url']}" style='width:120px; height:68px; object-fit:cover; border-radius:6px'/>
                        <div style='flex:1'>
                            <h3 style='color:white; margin:0'>{p2['username']}<span style='color:#4488ff'>#{p2['tagline']}</span></h3>
                            <p style='color:#aaaaaa; margin:2px 0; font-size:12px'>Rank: {p2['rank']}</p>
                            <p style='color:#aaaaaa; margin:2px 0; font-size:12px'>MMR: {p2['mmr_rank']} ({p2['mmr']}) | Peak: <span style='color:#FFD700'>{p2['peak_rank']}</span></p>
                        </div>
                        <img src="{p2['rank_icon_url']}" style='width:50px; height:50px'/>
                    </div>
                """, unsafe_allow_html=True)

            st.divider()

            # --- IQ SCORE ---
            st.markdown("<h3 style='color:#ff4655; text-align:center'>◆ VALORANT IQ SCORE</h3>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns([2, 1, 2])
            with col1:
                st.markdown(f"""
                    <div style='background:#1f2d3a; border:2px solid {p1['grade_color']}; border-radius:12px; padding:20px; text-align:center'>
                        <h1 style='color:{p1['grade_color']}; font-size:60px; margin:0'>{p1['iq_score']}</h1>
                        <div style='background:{p1['grade_color']}; border-radius:6px; padding:4px 16px; display:inline-block; margin-top:8px'>
                            <span style='color:#0f1923; font-weight:bold'>GRADE {p1['grade']}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            with col2:
                w1, w2 = winner_badge(p1['iq_score'], p2['iq_score'])
                overall_winner = p1['username'] if p1['iq_score'] > p2['iq_score'] else p2['username'] if p2['iq_score'] > p1['iq_score'] else "TIE"
                st.markdown(f"""
                    <div style='text-align:center; padding:20px'>
                        <p style='color:#aaaaaa; font-size:12px; margin:0'>WINNER</p>
                        <h2 style='color:#FFD700; margin:8px 0'>{overall_winner}</h2>
                        <p style='font-size:24px; margin:0'>{w1 or w2}</p>
                    </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                    <div style='background:#1f2d3a; border:2px solid {p2['grade_color']}; border-radius:12px; padding:20px; text-align:center'>
                        <h1 style='color:{p2['grade_color']}; font-size:60px; margin:0'>{p2['iq_score']}</h1>
                        <div style='background:{p2['grade_color']}; border-radius:6px; padding:4px 16px; display:inline-block; margin-top:8px'>
                            <span style='color:#0f1923; font-weight:bold'>GRADE {p2['grade']}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            st.divider()

            # --- STAT COMPARISON ---
            st.markdown("<h3 style='color:#ff4655; text-align:center'>◆ STAT BREAKDOWN</h3>", unsafe_allow_html=True)
            stats_to_compare = [
                ("K/D RATIO", p1['kd_ratio'], p2['kd_ratio'], False),
                ("HEADSHOT %", p1['hs_pct'], p2['hs_pct'], False),
                ("AVG DAMAGE", p1['avg_damage'], p2['avg_damage'], False),
                ("TOTAL KILLS", p1['total_kills'], p2['total_kills'], False),
                ("TOTAL DEATHS", p1['total_deaths'], p2['total_deaths'], True),
                ("MMR", p1['mmr'], p2['mmr'], False),
            ]

            for stat_name, val1, val2, reverse in stats_to_compare:
                w1, w2 = winner_badge(val1, val2, reverse)
                col1, col2, col3 = st.columns([2, 1, 2])
                with col1:
                    color1 = "#ff4655" if w1 == "🏆" else "#aaaaaa"
                    st.markdown(f"<div style='background:#1f2d3a; padding:12px 20px; border-radius:8px; border-left:3px solid {color1}'><span style='color:{color1}; font-size:20px; font-weight:bold'>{val1} {w1}</span></div>", unsafe_allow_html=True)
                with col2:
                    st.markdown(f"<div style='text-align:center; padding:12px'><span style='color:#aaaaaa; font-size:12px; letter-spacing:1px'>{stat_name}</span></div>", unsafe_allow_html=True)
                with col3:
                    color2 = "#4488ff" if w2 == "🏆" else "#aaaaaa"
                    st.markdown(f"<div style='background:#1f2d3a; padding:12px 20px; border-radius:8px; border-right:3px solid {color2}'><span style='color:{color2}; font-size:20px; font-weight:bold'>{w2} {val2}</span></div>", unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)

            st.divider()

            # --- CHART ---
            st.markdown("<h3 style='color:#ff4655; text-align:center'>◆ OVERVIEW CHART</h3>", unsafe_allow_html=True)
            chart_data = pd.DataFrame({
                p1['username']: [p1['kd_ratio'], p1['hs_pct'], p1['avg_damage']/10],
                p2['username']: [p2['kd_ratio'], p2['hs_pct'], p2['avg_damage']/10],
            }, index=["K/D", "HS%", "DMG/10"])
            st.bar_chart(chart_data, color=["#ff4655", "#4488ff"])

            st.divider()

            # --- TOP AGENTS ---
            st.markdown("<h3 style='color:#ff4655; text-align:center'>◆ FAVOURITE AGENT</h3>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"<div style='text-align:center; color:white; font-size:18px'>🎮 <b>{p1['top_agent']}</b></div>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<div style='text-align:center; color:white; font-size:18px'>🎮 <b>{p2['top_agent']}</b></div>", unsafe_allow_html=True)