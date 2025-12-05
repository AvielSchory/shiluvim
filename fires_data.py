import requests
import pandas as pd

# Replace with your own MAP_KEY from FIRMS
MAP_KEY = "77c806abc404aa7361a523388ba72262"

# Example: VIIRS Suomi-NPP, worldwide, last 1 day
url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{MAP_KEY}/VIIRS_SNPP_NRT/world/1"

# Send request
response = requests.get(url)

# Check status
if response.status_code == 200:
    # Load into pandas DataFrame
    from io import StringIO
    df = pd.read_csv(StringIO(response.text))
    
    print(df.head())
else:
    print("Error:", response.status_code, response.text)