import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("IPL Playoff Probability Analyzer")

# Load data
df = pd.read_csv("ipl_points.csv")

st.subheader("IPL Points Table")
st.dataframe(df)

# Sort teams
df = df.sort_values(by="Points", ascending=False)

# Top 4 teams
top4 = df.head(4)

st.subheader("Top 4 Teams (Semi Final Chances)")
st.write(top4)

# Probability calculation
total_points = df["Points"].sum()
df["Semi Final Probability (%)"] = (df["Points"] / total_points) * 100

st.subheader("Semi Final Probability")
st.dataframe(df)

# Points graph
st.subheader("Team Points Comparison")

fig, ax = plt.subplots()
ax.bar(df["Team"], df["Points"])

ax.set_xlabel("Teams")
ax.set_ylabel("Points")
ax.set_title("IPL Points Table")

st.pyplot(fig)

# Semi-final probability graph
st.subheader("Semi Final Probability Graph")

fig2, ax2 = plt.subplots()

ax2.bar(df["Team"], df["Semi Final Probability (%)"])

ax2.set_xlabel("Teams")
ax2.set_ylabel("Probability (%)")
ax2.set_title("Chance of Reaching Semi Final")

st.pyplot(fig2)

# Final prediction
st.subheader("Predicted Finalists")

finalists = df.head(2)

st.write("Most likely teams to reach final:")

st.write(finalists[["Team","Points"]])