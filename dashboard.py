import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from fires_data import load_data

st.set_page_config(page_title="Global Fire Dashboard", layout="wide")

st.title("🔥 Global Fire Dashboard")
st.markdown("Data from NASA FIRMS (Near Real-Time Active Fire Detections)")

@st.cache_data(ttl=3600)
def get_data():
    return load_data()

df = get_data()

if not df.empty:
    # Date slider
    min_date = df["acq_date"].min().date()
    max_date = df["acq_date"].max().date()
    selected_date = st.slider(
        "Select date to view fires",
        min_value=min_date,
        max_value=max_date,
        value=max_date,
        format="YYYY-MM-DD"
    )

    # Filter by selected date
    filtered_df = df[df["acq_date"].dt.date == selected_date]

    st.subheader(f"Fire Detections on {selected_date}")
    st.dataframe(filtered_df.head(20))

    # Map
    m = folium.Map(location=[0, 0], zoom_start=2, tiles="CartoDB positron")

    for _, row in filtered_df.iterrows():
        lat, lon = row["latitude"], row["longitude"]
        frp = row["frp"]
        conf = row["confidence"]
        popup_text = (
            f"Date: {row['acq_date'].date()} {row['acq_time']} UTC<br>"
            f"Satellite: {row['satellite']} ({row['instrument']})<br>"
            f"Confidence: {conf}<br>"
            f"FRP: {frp} MW<br>"
            f"Day/Night: {row['daynight']}"
        )
        folium.CircleMarker(
            location=[lat, lon],
            radius=3,
            color="red" if conf in ["h", "high"] else "orange",
            fill=True,
            fill_opacity=0.7,
            popup=popup_text,
        ).add_to(m)

    st.subheader("World Map of Active Fires")
    st_folium(m, width=1200, height=600)
else:
    st.warning("No data available.")