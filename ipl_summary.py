# Project: IPL Playoff Analyzer
# Developed by: Krishna Arora
# Year: 2025
# Description: IPL Playoff Simulation and Prediction System based on team performance, points, and net run rate
# GitHub: https://github.com/ErKrishnaarora
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

st.set_page_config(layout="wide")
st.title("IPL Playoff Probability Analyzer")

# -----------------------------
# File and Teams
# -----------------------------
FILE = "ipl_data.csv"
teams = ["CSK","MI","RCB","KKR","SRH","DC","RR","PBKS","GT","LSG"]
team_colors = {
    "CSK":"#FFD700", "MI":"#004BA0", "RCB":"#DA1818", "KKR":"#3A225D",
    "SRH":"#FF822A","DC":"#0078BC","RR":"#EA1A85","PBKS":"#ED1C24",
    "GT":"#1B2133","LSG":"#00AEEF"
}

# -----------------------------
# Session state
# -----------------------------
for var in ['winner_sf1','loser_sf1','winner_elim','winner_sf2','finalists_prob','semi_probs']:
    if var not in st.session_state:
        st.session_state[var] = None

# -----------------------------
# Load or create CSV
# -----------------------------
if not os.path.exists(FILE):
    df = pd.DataFrame({
        "Team": teams,
        "Matches Played": [0]*10,
        "Points": [0]*10,
        "Runs Scored": [0]*10,
        "Runs Conceded": [0]*10,
        "NRR":[0]*10
    })
    df.to_csv(FILE,index=False)
else:
    df = pd.read_csv(FILE)
    for col in ["Matches Played","Points","Runs Scored","Runs Conceded","NRR"]:
        if col not in df.columns:
            df[col] = 0

# -----------------------------
# Clear All Data
# -----------------------------
if st.button(" Clear All Data"):
    df[["Matches Played","Points","Runs Scored","Runs Conceded","NRR"]] = 0
    df.to_csv(FILE,index=False)
    for var in ['winner_sf1','loser_sf1','winner_elim','winner_sf2','finalists_prob','semi_probs']:
        st.session_state[var] = None
    st.success("All data cleared!")
    st.experimental_rerun()

# -----------------------------
# League Stage Input
# -----------------------------
st.header("League Stage: Enter Matches, Runs, Points")
league_inputs = []
for i in range(len(df)):
    col1,col2,col3,col4 = st.columns(4)
    with col1:
        mp = st.number_input(f"{df.at[i,'Team']} Matches Played", 0, 14, int(df.at[i,"Matches Played"]), key=f"mp{i}")
    with col2:
        rs = st.number_input(f"{df.at[i,'Team']} Runs Scored", 0, 5000, int(df.at[i,"Runs Scored"]), key=f"rs{i}")
    with col3:
        rc = st.number_input(f"{df.at[i,'Team']} Runs Conceded", 0, 5000, int(df.at[i,"Runs Conceded"]), key=f"rc{i}")
    with col4:
        pts = st.number_input(f"{df.at[i,'Team']} Points", 0, 30, int(df.at[i,"Points"]), key=f"pts{i}")
    league_inputs.append((mp, rs, rc, pts))

if st.button(" Submit League Data"):
    for i,vals in enumerate(league_inputs):
        mp, rs, rc, pts = vals
        df.at[i,"Matches Played"]=mp
        df.at[i,"Runs Scored"]=rs
        df.at[i,"Runs Conceded"]=rc
        df.at[i,"Points"]=pts
        df.at[i,"NRR"] = (rs/(mp*20) - rc/(mp*20)) if mp>0 else 0
    df = df.sort_values(by=["Points","NRR"], ascending=[False,False]).reset_index(drop=True)
    df["Rank"] = df.index+1
    df.to_csv(FILE,index=False)
    st.success("League data submitted successfully!")

# -----------------------------
# Show League Table & Graph
# -----------------------------
if df["Matches Played"].max()>0:
    st.subheader(" League Table")
    st.dataframe(df[["Rank","Team","Matches Played","Points","Runs Scored","Runs Conceded","NRR"]])

    st.subheader(" Points Leadership Bar Graph")
    fig,ax=plt.subplots(figsize=(12,6))
    ax.barh(df["Team"],df["Points"],color=[team_colors[t] for t in df["Team"]])
    for i,(p,nrr) in enumerate(zip(df["Points"],df["NRR"])):
        ax.text(p+0.1,i,f"P:{p} | NRR:{nrr:.2f}",color="white",va='center',fontsize=9)
    ax.invert_yaxis()
    st.pyplot(fig)

# -----------------------------
# Semi-Finals Probability before playoffs
# -----------------------------
if df["Matches Played"].max()>0:
    top4 = df.head(4)
    sf1_prob = top4.iloc[0:2][["Team","Points","NRR"]].copy()
    elim_prob = top4.iloc[2:4][["Team","Points","NRR"]].copy()

    # Simple league points+NRR based probability
    sf1_prob["Probability"] = ((sf1_prob["Points"]+sf1_prob["NRR"]*2)/((sf1_prob["Points"]+sf1_prob["NRR"]*2).sum())*100).round(2)
    elim_prob["Probability"] = ((elim_prob["Points"]+elim_prob["NRR"]*2)/((elim_prob["Points"]+elim_prob["NRR"]*2).sum())*100).round(2)

    st.session_state['semi_probs'] = {"SF1":sf1_prob,"Eliminator":elim_prob}

    st.subheader(" Predicted Probabilities before Playoffs")
    st.write("Semi-Final 1 (1st vs 2nd)")
    st.dataframe(sf1_prob)
    st.write("Eliminator (3rd vs 4th)")
    st.dataframe(elim_prob)

# -----------------------------
# Playoffs Input
# -----------------------------
if df["Matches Played"].max()>0 and st.session_state.get('semi_probs'):
    # SF1 Input
    st.header(" Semi-Final 1 (1st vs 2nd)")
    sf1_teams = df.head(2)["Team"].tolist()
    col1,col2 = st.columns(2)
    with col1:
        rs1 = st.number_input(f"{sf1_teams[0]} Runs Scored (SF1)", min_value=0, key="sf1_rs1")
        rc1 = st.number_input(f"{sf1_teams[0]} Runs Conceded (SF1)", min_value=0, key="sf1_rc1")
    with col2:
        rs2 = st.number_input(f"{sf1_teams[1]} Runs Scored (SF1)", min_value=0, key="sf1_rs2")
        rc2 = st.number_input(f"{sf1_teams[1]} Runs Conceded (SF1)", min_value=0, key="sf1_rc2")

    if st.button(" Submit SF1 Result"):
        st.session_state['winner_sf1'] = sf1_teams[0] if rs1>rs2 else sf1_teams[1]
        st.session_state['loser_sf1'] = sf1_teams[1] if st.session_state['winner_sf1']==sf1_teams[0] else sf1_teams[0]
        st.success(f"Winner SF1: {st.session_state['winner_sf1']} (Direct to Final)")

    # Eliminator Input
    st.header(" Eliminator (3rd vs 4th)")
    elim_teams = df.iloc[2:4]["Team"].tolist()
    col1,col2 = st.columns(2)
    with col1:
        rs3 = st.number_input(f"{elim_teams[0]} Runs Scored (Eliminator)", min_value=0, key="elim_rs1")
        rc3 = st.number_input(f"{elim_teams[0]} Runs Conceded (Eliminator)", min_value=0, key="elim_rc1")
    with col2:
        rs4 = st.number_input(f"{elim_teams[1]} Runs Scored (Eliminator)", min_value=0, key="elim_rs2")
        rc4 = st.number_input(f"{elim_teams[1]} Runs Conceded (Eliminator)", min_value=0, key="elim_rc2")

    if st.button(" Submit Eliminator Result"):
        st.session_state['winner_elim'] = elim_teams[0] if rs3>rs4 else elim_teams[1]
        st.success(f"Winner Eliminator: {st.session_state['winner_elim']} (Goes to SF2)")

    # SF2 Input
    if st.session_state.get('winner_elim') and st.session_state.get('loser_sf1'):
        st.header(" Semi-Final 2")
        sf2_teams = [st.session_state['loser_sf1'],st.session_state['winner_elim']]
        col1,col2 = st.columns(2)
        with col1:
            rs5 = st.number_input(f"{sf2_teams[0]} Runs Scored (SF2)", min_value=0, key="sf2_rs1")
            rc5 = st.number_input(f"{sf2_teams[0]} Runs Conceded (SF2)", min_value=0, key="sf2_rc1")
        with col2:
            rs6 = st.number_input(f"{sf2_teams[1]} Runs Scored (SF2)", min_value=0, key="sf2_rs2")
            rc6 = st.number_input(f"{sf2_teams[1]} Runs Conceded (SF2)", min_value=0, key="sf2_rc2")

        if st.button(" Submit SF2 Result"):
            st.session_state['winner_sf2'] = sf2_teams[0] if rs5>rs6 else sf2_teams[1]
            st.success(f"Winner SF2: {st.session_state['winner_sf2']} (Finalist 2)")

# -----------------------------
# Final Probability Prediction
# -----------------------------
if st.session_state.get('winner_sf1') and st.session_state.get('winner_sf2'):
    st.header(" Final Prediction Probabilities")
    finalists = [st.session_state['winner_sf1'],st.session_state['winner_sf2']]
    finalist_data = df[df["Team"].isin(finalists)].copy()
    finalist_data["SF_Points"] = [rs1+rs2 if t==finalists[0] else rs5+rs6 for t in finalists]
    total_score = finalist_data["Points"].sum()+finalist_data["SF_Points"].sum()
    finalist_data["Probability"] = ((finalist_data["Points"] + finalist_data["SF_Points"])/total_score*100).round(2)
    st.session_state['finalists_prob'] = finalist_data

    st.subheader(" Finalists Probability Table")
    st.dataframe(finalist_data[["Team","Points","SF_Points","Probability"]])

    st.subheader(" Probability Pie Chart")
    fig,ax=plt.subplots()
    ax.pie(finalist_data["Probability"], labels=finalist_data["Team"],
           colors=[team_colors[t] for t in finalists], autopct="%1.1f%%", startangle=90)
    st.pyplot(fig)

    st.subheader(" Probability Line Chart")
    fig2,ax2=plt.subplots()
    ax2.plot(finalist_data["Team"], finalist_data["Probability"], marker='o', color='green')
    ax2.set_ylabel("Winning Probability (%)")
    ax2.set_title("Final Match Winning Probability")
    st.pyplot(fig2)

st.success(" Simulation Complete!")