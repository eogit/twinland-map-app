import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import geopandas as gpd
import requests

st.title("Twinland map app")
st.write(
    "Deployed on [docs.streamlit.io](https://docs.streamlit.io/)."
)

vector_file = 'Polygons_small.shp'
if vector_file:
    # Read the vector file
    gdf = gpd.read_file(vector_file)
    
    # Display map with polygons
    m = folium.Map(location=[gdf.geometry.centroid.y.mean(), gdf.geometry.centroid.x.mean()], zoom_start=12)
    for _, row in gdf.iterrows():
        folium.GeoJson(row.geometry, name=row['id']).add_to(m)

    # Display the map in Streamlit
    st_data = st_folium(m, width=700, height=500)

    # Dropdown options
    option = st.selectbox("Select an option:", ["Option 1", "Option 2", "Option 3"])

    # API call button
    if st.button("Call API"):
        # Extract selected polygon coordinates
        selected = st_data.get("last_clicked", None)
        if selected:
            lat, lon = selected["lat"], selected["lng"]
            payload = {
                "lat": lat,
                "lon": lon,
                "option": option
            }
            response = requests.post("https://your-api-url.com", json=payload)
            st.write("API Response:", response.json())
        else:
            st.write("Please select a polygon on the map.")
