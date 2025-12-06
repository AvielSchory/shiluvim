# Global Fire Dashboard

Purpose
- Small Python project that fetches NASA FIRMS near-real-time active fire detections and provides a Streamlit dashboard to visualize them.

What it does
- `fires_data.py` retrieves CSV data from NASA FIRMS (`https://firms.modaps.eosdis.nasa.gov/api/area`) and parses it into a `pandas.DataFrame`.
- `dashboard.py` is a Streamlit app that loads the fire data, filters by date, and renders a world map with detections using `folium` and `streamlit-folium`.

Live demo
- View the hosted app: https://shiluvim-zh4dbwqkatyqv3ovurfwek.streamlit.app/
