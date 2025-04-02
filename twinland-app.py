# To deploy this app, type:
#   streamlit run twinland-app.py --server.enableCORS false --server.enableXsrfProtection false
# and open the browser at the provided Local URL
import streamlit as st
import os
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import geopandas as gpd
from shapely.geometry import Point, Polygon, shape
import requests

def get_session_state(session_state, verbose=False):     
    f = open("logfile.txt", "a")
    zoom = 11
    center = {}
    clicked_point = Point(0, 0)
    # step 1: Get the current session state ID (longer than 60 characters)
    f.write("_"*40 + "\n")
    for key, value in session_state.items():
        f.write(str(key) + ": " + str(value) + "\n")
        if len(key)>60:
            f.write(f"{key}: {value}")
            f.write("Session state key:" + str(key))
            if key == "last_clicked" and value is not None:
                clicked_point = value
                if verbose:
                    st.write("--> Clicked Point: ", clicked_point)
            # step 2: Get the session state values from within the current session
            if value is not None:
                if verbose:
                    f.write("Inside this key:\n")
                for k,v in value.items():
                    f.write(str(k)+ ": " + v + "\n")
                    if k == 'zoom':
                        zoom = v
                        if verbose:
                            st.write("--> zoom: ", zoom)
                    if k=="center":
                        center = v
                        if verbose:
                            st.write("--> center: ", center)
                    if k=="last_clicked" and v is not None:
                        clicked_point = Point(v.get("lng"), v.get("lat"))
                        if verbose:
                            st.write("--> Last Clicked: ", clicked_point)
    if verbose:
        st.write("Returning session state values:")
        st.write("Zoom:", zoom)
        st.write("Center:", center)
        st.write("Clicked Point:", clicked_point)
    f.close()
    return(zoom, center, clicked_point)


st.title("Twinland map app")
st.write("Deployed on [docs.streamlit.io](https://docs.streamlit.io/).")

vector_file = 'Polygons_small.shp'

if os.path.isfile(vector_file):
    if "gdf" not in locals() and "gdf" not in globals():
        # Read the vector file only once
        gdf = gpd.read_file(vector_file)
        # remove the bounding box polygon with id == 11 (specific to this dataset)
        gdf = gdf.drop(gdf[gdf.id==11].index)
    
    # Get session state values for the current session
    zoom, center, clicked_point = get_session_state(st.session_state)
    st.write("Clicked point from get_session_state:", clicked_point)

    # Check if the Point is contained in any of the polygons
    matches = gdf[gdf.geometry.contains(clicked_point)]
    if len(matches.geometry) > 0:
        st.write("Point is contained in polygon(s):")
        st.write(matches.geometry)
    else:
        st.write("WARNING: Point not contained in polygons.")

    # Display map with polygons centred on the geodataframe or restored view from session state
    if center == {}:
        centroid = gdf.geometry.centroid
        lat = centroid.y.mean()
        lon = centroid.x.mean()
    else:
        lat = center.get("lat")
        lon = center.get("lng")

    # show map with polygons
    if "m" not in locals() and "m" not in globals():
        # Create a folium map centered on the centroid of the polygons
        m = folium.Map(location=[lat, lon], zoom_start=zoom)
    polygon_layers = {}
    for idx, row in gdf.iterrows():
        # Create a GeoJson layer for each polygon
        layer = folium.GeoJson(
            row.geometry,
            name=f"Polygon {idx}",
            style_function=lambda feature: {
                "fillColor": "yellow" 
                if shape(feature["geometry"]).contains(clicked_point)
                else "green",
                "color": "black",
                "weight": 2,
                "fillOpacity": 0.8
            }).add_to(m)
        #st.write("Layer:", layer.__dict__)
        polygon_layers[f"Polygon {idx}"] = layer

    # Display the map in Streamlit
    if "st_data" not in locals() and "st_data" not in globals():
        st_data = st_folium(m, width=700, height=500)

    # Dropdown options
    croptype = st.selectbox("Select a crop:", ["Winter Wheat", "Spring Wheat", "Maize", "Barley", "Oats", "Rye", "Triticale", "Soybean", "Sunflower", "Rapeseed", "Potato", "Sugarbeet", "Pea", "Bean", "Lentil", "Chickpea", "Lupin", "Sorghum", "Millet", "Buckwheat", "Quinoa", "Canaryseed", "Flax", "Hemp", "Camelina", "Safflower", "Mustard", "Poppy", "Caraway", "Coriander", "Fennel", "Anise", "Cumin", "Ajwain", "Dill", "Parsley", "Celery", "Chervil", "Lovage", "Angelica", "Parsnip", "Carrot", "Beetroot", "Radish", "Turnip", "Rutabaga", "Cabbage", "Kale", "Brussels Sprout", "Cauliflower", "Broccoli", "Kohlrabi", "Chinese Cabbage", "Pak Choi", "Swede", "Spinach", "Lettuce", "Endive", "Chicory", "Radicchio", "Dandelion", "Sorrel", "Rocket", "Watercress", "Purslane", "Lamb's Lettuce", "Chard", "Beet Greens", "Amaranth", "Orache", "New Zealand Spinach", "Malabar Spinach", "Tatsoi", "Mizuna", "Mibuna", "Komatsuna", "Napa Cabbage", "Bok Choy", "Tatsoi", "Choy Sum", "Pak Choi", "Mustard Greens", "Collard Greens", "Kale", "Broccoli Raab", "Turnip Greens", "Rapini", "Cress", "Watercress", "Land Cress", "Winter Purslane", "Miner's Lettuce", "Claytonia", "Ice Plant", "Sea Beet", "Sea Kale", "Samphire", "Salicornia", "Beach Asparagus", "Beach Mustard", "Beach Spinach", "Beach Cabbage", "Beach Lettuce", "Beach Dock", "Beach Sorrel",])

    # API call button
    if st.button("Call API"):
        # Extract selected polygon coordinates
        selected = st_data.get("last_clicked", None)
        if selected:
            lat, lon = selected["lat"], selected["lng"]
            payload = {
                "lat": lat,
                "lon": lon,
                "croptype": croptype
            }
            # payload is for handing over to the digital twin API
            st.write("Selected field:", payload)
            st.write("This is where the API of the DT is called.")
            #TODO: Call DT API here:
            #response = requests.post("https://your-api-url.com", json=payload)
            #st.write("API Response:", response.json())
        else:
            st.write("Select a polygon first.")

    # Check if the user clicked on the map
    if st_data.get("last_clicked"):
        # Extract selected polygon coordinates
        selected = st_data.get("last_clicked")
        lat, lon = selected["lat"], selected["lng"]

        # Update session state with the clicked point
        clicked_point = Point(lon, lat)

        selected_polygon = gdf[gdf.geometry.contains(clicked_point)]
        if not selected_polygon.empty:
            st.write("Selected polygon(s):", selected_polygon)

        # Update session state with the clicked point and map view
        st.session_state.clicked_point = clicked_point
        st.session_state['zoom'] = zoom
        st.session_state['center'] = center