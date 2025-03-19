import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime, timedelta
import pytz

# Function to fetch cyclone data
def fetch_cyclone_data(url):
    response = requests.get(url)
    data = response.json()
    
    # Parse the data
    cyclones = []
    for feature in data['features']:
        properties = feature['properties']
        geometry = feature['geometry']
        utc_time = pd.to_datetime(properties['time'], unit='ms')
        local_time = utc_time.tz_localize('UTC').tz_convert(pytz.timezone('Asia/Kolkata'))  # Convert to local timezone
        
        if utc_time >= datetime.utcnow() - timedelta(days=1):  # Filter for the last 24 hours
            cyclones.append({
                "name": properties.get('name', 'Unknown'),
                "wind_speed": properties.get('wind_speed', 'N/A'),
                "pressure": properties.get('pressure', 'N/A'),
                "time_utc": utc_time,
                "time_local": local_time,
                "latitude": geometry['coordinates'][1],
                "longitude": geometry['coordinates'][0]
            })
    
    return pd.DataFrame(cyclones)

# Fetch cyclone data (replace with a real API providing cyclone data)
cyclone_url = "https://api.example.com/cyclone-data"  # Replace with actual API endpoint
cyclone_data = fetch_cyclone_data(cyclone_url)

# Streamlit app layout
st.title("Real-Time Cyclone Monitoring Webapp")
st.markdown("This app visualizes real-time cyclone data from meteorological sources.")

# Filter by wind speed
min_wind_speed = st.slider("Minimum Wind Speed (km/h)", min_value=0, max_value=300, value=50, step=10)
filtered_cyclone_data = cyclone_data[cyclone_data["wind_speed"] >= min_wind_speed]

# Create a Plotly map for cyclones
fig_cyclone = px.scatter_mapbox(
    filtered_cyclone_data,
    lat="latitude",
    lon="longitude",
    size="wind_speed",
    color="wind_speed",
    hover_name="name",
    hover_data={"time_utc": True, "time_local": True, "wind_speed": True, "pressure": True},
    zoom=1,
    height=600,
    title="Cyclones in the Last 24 Hours"
)

fig_cyclone.update_layout(mapbox_style="open-street-map")

# Display the map
st.plotly_chart(fig_cyclone)

# Display the filtered raw data
st.subheader("Filtered Cyclone Data")
st.write(filtered_cyclone_data)

# Additional Information
st.sidebar.subheader("About This App")
st.sidebar.info(
    """
    This application fetches real-time cyclone data from a meteorological API and visualizes it on an interactive map.
    Use the slider to filter cyclones by wind speed. The times are displayed in both UTC and local time.
    """
)

