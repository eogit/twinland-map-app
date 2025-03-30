import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import geopandas as gpd
from shapely.geometry import Point, Polygon, shape
import requests

st.title("Twinland map app")
st.write(
    "Deployed on [docs.streamlit.io](https://docs.streamlit.io/)."
)

vector_file = 'Polygons_small.shp'

if vector_file:
    # Read the vector file
    gdf = gpd.read_file(vector_file)

    # Initialization

    #st.write("Session state:")
    #st.write(st.session_state)

    # Check if 'clicked_point' exists in session state
    if 'clicked_point' not in st.session_state:
        st.session_state['clicked_point'] = Point(0, 0)
        # Make sure c exists
        if 'c' not in locals() and 'c' not in globals():
            c = Point(0, 0)
    else:
        # Use the existing clicked point from session state
        c = st.session_state['clicked_point']
    
    # Check if the Point is contained in any of the polygons
    matches = gdf[gdf.geometry.contains(c)]
    st.write("Matches:", matches.geometry)
    if len(matches.geometry) > 0:
        st.write("Point is contained in polygon(s).")
    else:
        st.write("WARNING: Point not contained in polygons.")

    # Display map with polygons centred on the geodataframe or restored view from session state
    centroid = gdf.geometry.centroid
    # Check if 'zoom' and 'center' exist in session state
    if 'center' not in st.session_state:
        st.write("No center in session state.")
        st.session_state.center = {'lat': centroid.y.mean(), 'lng': centroid.x.mean()}
    if 'zoom' not in st.session_state:
        st.write("No zoom in session state.")
        st.session_state['zoom'] = 11

    m = folium.Map(location=[st.session_state.center['lat'], st.session_state.center['lng']], zoom_start=st.session_state['zoom'])

    # Add polygons to the map
    polygon_layers = {}
    for idx, row in gdf.iterrows():
        c = st.session_state['clicked_point']
        style_function=lambda feature: {
            "fillColor": "yellow" 
            if shape(feature["geometry"]).contains(c)
            else "green",
            "color": "black",
            "weight": 2,
            "fillOpacity": 0.8
        }

        # Create a GeoJson layer for each polygon
        layer = folium.GeoJson(
            row.geometry,
            name=f"Polygon {idx}",
            style_function=style_function
        )
        layer.add_to(m)
        #st.write("Layer:", layer.__dict__)

        polygon_layers[f"Polygon {idx}"] = layer

    # Display the map in Streamlit
    st_data = st_folium(m, width=700, height=500)

    # Dropdown options
    option = st.selectbox("Select an option:", ["Winter Wheat", "Spring Wheat", "Maize", "Barley", "Oats", "Rye", "Triticale", "Soybean", "Sunflower", "Rapeseed", "Potato", "Sugarbeet", "Pea", "Bean", "Lentil", "Chickpea", "Lupin", "Sorghum", "Millet", "Buckwheat", "Quinoa", "Canaryseed", "Flax", "Hemp", "Camelina", "Safflower", "Mustard", "Poppy", "Caraway", "Coriander", "Fennel", "Anise", "Cumin", "Ajwain", "Dill", "Parsley", "Celery", "Chervil", "Lovage", "Angelica", "Parsnip", "Carrot", "Beetroot", "Radish", "Turnip", "Rutabaga", "Cabbage", "Kale", "Brussels Sprout", "Cauliflower", "Broccoli", "Kohlrabi", "Chinese Cabbage", "Pak Choi", "Swede", "Spinach", "Lettuce", "Endive", "Chicory", "Radicchio", "Dandelion", "Sorrel", "Rocket", "Watercress", "Purslane", "Lamb's Lettuce", "Chard", "Beet Greens", "Amaranth", "Orache", "New Zealand Spinach", "Malabar Spinach", "Tatsoi", "Mizuna", "Mibuna", "Komatsuna", "Napa Cabbage", "Bok Choy", "Tatsoi", "Choy Sum", "Pak Choi", "Mustard Greens", "Collard Greens", "Kale", "Broccoli Raab", "Turnip Greens", "Rapini", "Cress", "Watercress", "Land Cress", "Winter Purslane", "Miner's Lettuce", "Claytonia", "Ice Plant", "Sea Beet", "Sea Kale", "Samphire", "Salicornia", "Beach Asparagus", "Beach Mustard", "Beach Spinach", "Beach Cabbage", "Beach Lettuce", "Beach Dock", "Beach Sorrel",])

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
            # payload is for handing over to the digital twin API
            st.write("Selected field:", payload)
            st.write("This is where the API of the DT is called.")
            #TODO: Call DT API here:
            #response = requests.post("https://your-api-url.com", json=payload)
            #st.write("API Response:", response.json())
        else:
            st.write("Select a polygon first.")

    # Highlight clicked polygon
    if st_data.get("last_clicked"):
        # Extract selected polygon coordinates
        selected = st_data.get("last_clicked", None)
        if selected:
            lat, lon = selected["lat"], selected["lng"]

        # Find the polygon containing the clicked point
        clicked_point = gpd.GeoDataFrame(geometry=[gpd.points_from_xy([lon], [lat])[0]], crs=gdf.crs)
        st.session_state['clicked_point'] = {
            "lon:" lon, 
            "lat": lat
            }
        c = Point(lon,lat)
        st.write("Selected coordinates:", st.session_state['clicked_point'])
        #selected_polygon = gdf[gdf.contains(clicked_point.geometry.iloc[0])]
    else:
        clicked_point = None
        #selected_polygon = None

    # Hack into the session state to get the map's zoom and center and preserve them
    #st.write("Session state after clicking:")
    #st.write(st.session_state)
    i=0
    for key, value in st.session_state.items():
        i+=1
        if i==3:
            st.write(f"{key}: {value}")
            zoom = [v for k,v in value.items() if k == 'zoom'][0]
            #TODO: center is a dict with lat and lng in the first map but then it is set to a Point object
            center = [v for k,v in value.items() if k == 'center'][0]
            st.write("Zoom:", zoom)
            st.write("Center:", center)
            st.session_state['zoom'] = zoom
            st.session_state['center'] = center
    #TODO: Refresh the map in Streamlit



# Then to deploy it, type:
# streamlit run twinland-app.py
# or
# streamlit run twinland-app.py --server.enableCORS false --server.enableXsrfProtection false
# and open the browser at the provided Local URL


#TODO: multiple columns
#col1, col2 = st.columns(2)
#with col1:

