import requests
import pandas as pd
from io import StringIO

MAP_KEY = "77c806abc404aa7361a523388ba72262"
DAY_RANGE = 10
# Example: VIIRS Suomi-NPP, worldwide, last 1 day
url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{MAP_KEY}/VIIRS_SNPP_NRT/world/{DAY_RANGE}"

def load_data():
    """Fetch FIRMS fire data and return as a DataFrame."""
    response = requests.get(url)
    df = pd.read_csv(StringIO(response.text))
    # Convert acq_date to datetime for filtering
    df["acq_date"] = pd.to_datetime(df["acq_date"])
    return df
