import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import altair as alt
from fires_data import load_data

st.set_page_config(page_title="Global Fire Dashboard", layout="wide")

st.title("🔥 Global Fire Dashboard")
st.markdown("Data from NASA FIRMS (Near Real-Time Active Fire Detections)")

@st.cache_data(ttl=3600)
def get_data():
    return load_data()

df = get_data()

if df.empty or "acq_date" not in df.columns:
    st.error("No valid fire data returned. Check your MAP_KEY or API response.")
else:
    df.columns = df.columns.str.strip().str.lower()

    col1, col2, col3 = st.columns((1.5, 4.5, 2), gap="medium")

    # -------------------------------
    # Column 1: Confidence & Satellite summary
    # -------------------------------
    with col1:
        st.subheader("Confidence Breakdown (Donut)")

        # Confidence breakdown h/n/l per satellite
        conf_breakdown = (
            df.assign(
                conf_type=df["confidence"].astype(str).str.lower().map(
                    lambda x: "h" if x in ["h", "high"]
                    else "n" if x in ["n", "nominal"]
                    else "l"
                )
            )
            .groupby(["satellite", "conf_type"])
            .size()
            .reset_index(name="count")
        )

        # Compute percentages
        total_counts = conf_breakdown.groupby("satellite")["count"].transform("sum")
        conf_breakdown["pct"] = conf_breakdown["count"] / total_counts * 100

        # Donut chart with custom colors
        donut = alt.Chart(conf_breakdown).mark_arc(innerRadius=50).encode(
            theta="pct:Q",
            color=alt.Color(
                "conf_type:N",
                scale=alt.Scale(
                    domain=["h", "n", "l"],
                    range=["green", "orange", "red"]
                ),
                title="Confidence"
            ),
            tooltip=["satellite", "conf_type", "pct"]
        ).properties(width=250, height=250).configure_axis(grid=False)

        st.altair_chart(donut, use_container_width=True)

        st.subheader("Number of Fires by Satellite")

        conf_summary = (
            df.groupby("satellite")
              .size()
              .reset_index(name="total")
        )

        bar_sat = alt.Chart(conf_summary).mark_bar().encode(
            x=alt.X("satellite:N", title="Satellite"),
            y=alt.Y("total:Q", title="Number of Fires"),
            color="satellite:N",
            tooltip=["satellite", "total"]
        ).properties(width=250, height=250).configure_axis(grid=False)

        st.altair_chart(bar_sat, use_container_width=True)

    # -------------------------------
    # Column 2: Map + Brightness Histogram
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
                f"Day/Night: {row['daynight']}<br>"
                f"Brightness: {row.get('brightness', 'N/A')}"
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

        st.subheader("Brightness Distribution of Fires")

        if "brightness" in df.columns:
            hist = alt.Chart(df).mark_bar().encode(
                x=alt.X("brightness:Q", bin=alt.Bin(maxbins=40), title="Brightness"),
                y=alt.Y("count()", title="Number of Fires"),
                tooltip=["count()"]
            ).properties(width=900, height=300).configure_axis(grid=False)

            st.altair_chart(hist, use_container_width=True)
        else:
            st.info("Brightness data not available in this dataset.")

    # -------------------------------
    # Column 3: Time trends
    # -------------------------------
    with col3:
        st.subheader("Total Fires by Date")
        fires_by_date = df.groupby(df["acq_date"].dt.date).size().reset_index(name="count")
        line = alt.Chart(fires_by_date).mark_line(point=True).encode(
            x=alt.X("acq_date:T", title="Date"),
            y=alt.Y("count:Q", title="Number of Fires"),
            tooltip=["acq_date", "count"]
        ).properties(width=300, height=250).configure_axis(grid=False)
        st.altair_chart(line, use_container_width=True)

        st.subheader("Day vs Night Fires")
        daynight_counts = df["daynight"].value_counts().reset_index()
        daynight_counts.columns = ["daynight", "count"]

        bar_dn = alt.Chart(daynight_counts).mark_bar().encode(
            x=alt.X("daynight:N", title="Day/Night"),
            y=alt.Y("count:Q", title="Number of Fires"),
            color=alt.Color(
                "daynight:N",
                scale=alt.Scale(domain=["D", "N"], range=["orange", "blue"]),
                title="Day/Night"
            ),
            tooltip=["daynight", "count"]
        ).properties(width=300, height=250).configure_axis(grid=False)

        st.altair_chart(bar_dn, use_container_width=True)