import streamlit as st
import pandas as pd

st.title("🎈 Test app")
st.write(
    "Deployed on [docs.streamlit.io](https://docs.streamlit.io/)."
)

data = {
  "Field": [420, 380, 390, 243, 112, 545],
  "NEE": [-1.4, -0.6, 1.2, 1.5, 1.3, -0.1]
}

#load data into a DataFrame object:
df = pd.DataFrame(data)
st.bar_chart(df, x="Field", y="NEE")

number = st.slider("Raise water table to (cm below surface): ", 10, 150)
df = pd.DataFrame(data)
df["new_NEE"] = df["NEE"] * number/150
st.title("WTD Dashboard")
st.bar_chart(df, x="Field", y="new_NEE")

# Then exit() Python and type into the terminal:
# streamlit run /workspaces/twinland-map-app/streamlit_app.py
# and open the Local URL