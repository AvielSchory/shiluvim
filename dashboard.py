import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from fires_data import load_data

st.set_page_config(page_title="Global Fire Dashboard", layout="wide")

st.title("🔥 Global Fire Dashboard")
st.markdown("Data from NASA FIRMS (Near Real-Time Active Fire Detections)")

# Load data
@st.cache_data(ttl=3600)
def get_data():
    return load_data()

df = get_data()

if df.empty or "acq_date" not in df.columns:
    st.error("No valid fire data returned. Check your MAP_KEY or API response.")
else:
    # Normalize column names
    df.columns = df.columns.str.strip().str.lower()

    # --- Create 3 columns layout ---
    col1, col2, col3 = st.columns((1.5, 4.5, 2), gap="medium")

    # -------------------------------
    # Column 1: Confidence & Satellite summary
    # -------------------------------
    with col1:
        st.subheader("Confidence by Satellite")

        # Calculate high confidence percentage per satellite
        conf_summary = (
            df.assign(high_conf=(df["confidence"].astype(str).str.lower().isin(["h", "high"])))
              .groupby("satellite")
              .agg(total=("confidence", "count"),
                   high=("high_conf", "sum"))
        )
        conf_summary["high_pct"] = conf_summary["high"] / conf_summary["total"] * 100

        st.bar_chart(conf_summary["high_pct"])

        st.subheader("Number of Fires by Satellite")
        st.bar_chart(conf_summary["total"])

    # -------------------------------
    # Column 2: Map + Top 10 states
    # -------------------------------
    with col2:
        st.subheader("World Map of Active Fires")

        m = folium.Map(location=[0, 0], zoom_start=2, tiles="CartoDB dark_matter")

        for _, row in df.iterrows():
            lat, lon = row["latitude"], row["longitude"]
            frp = row.get("frp", None)
            conf = row.get("confidence", None)
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
                color="red" if str(conf).lower() in ["h", "high"] else "orange",
                fill=True,
                fill_opacity=0.7,
                popup=popup_text,
            ).add_to(m)

        st_folium(m, width=900, height=600)

        st.subheader("Top 10 States by Fire Count")

        # Group by state if available (some FIRMS feeds include 'state' column)
        if "state" in df.columns:
            top_states = df.groupby("state").size().sort_values(ascending=False).head(10)
            st.table(top_states)
        else:
            st.info("State information not available in this dataset.")

    # -------------------------------
    # Column 3: Time trends
    # -------------------------------
    with col3:
        st.subheader("Total Fires by Date")

        fires_by_date = df.groupby(df["acq_date"].dt.date).size()
        st.line_chart(fires_by_date)

        st.subheader("Day vs Night Fires")

        daynight_counts = df["daynight"].value_counts()
        st.bar_chart(daynight_counts)