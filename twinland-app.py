import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import geopandas as gpd
from shapely.geometry import Point, Polygon, shape
import requests

# initialise session state
#if 'key' not in st.session_state:
#    st.session_state['key'] = 'value'

def get_session_state(session_state):     
    zoom = 11
    center = {}
    clicked_point = Point(0, 0)
    # step 1: Get the current session state ID (longer than 60 characters)
    for key, value in session_state.items():
        if len(key)>60:
            #st.write(f"{key}: {value}")
            #st.write("Session state key:", key)
            # step 2: Get the session state values from within the current session
            if value is not None:
                #st.write("Inside this key:")
                for k,v in value.items():
                    #st.write(k, ": ", v)
                    if k == 'zoom':
                        zoom = v
                        #st.write("zoom: ", zoom)
                    if k=="center":
                        center = v
                        #st.write("center: ", center)
                    if k=="clicked_point":
                        clicked_point = v
                        #st.write("Clicked Point: ", clicked_point)
    return(zoom, center, clicked_point)


st.title("Twinland map app")
st.write("Deployed on [docs.streamlit.io](https://docs.streamlit.io/).")

vector_file = 'Polygons_small.shp'

# multiple columns
#col1, col2 = st.columns((4,1))

if vector_file:
    # Read the vector file
    gdf = gpd.read_file(vector_file)

    # Initialization
    #st.write("Session state:")
    #st.write(st.session_state)

    # Get session state values for the current session
    zoom, center, clicked_point = get_session_state(st.session_state)

    # Check if 'clicked_point' exists in session state
    #if 'clicked_point' not in st.session_state:
    #    c = Point(0, 0)
    #    st.session_state.clicked_point = c
    #    #if 'c' not in locals() and 'c' not in globals():
    #else:
    #    # Use the existing clicked point from session state
    #    #st.write("Clicked point from session state:", st.session_state.clicked_point)
    #    c = st.session_state.clicked_point
    
    # Check if the Point is contained in any of the polygons
    st.write("Clicked point:", clicked_point)
    matches = gdf[gdf.geometry.contains(clicked_point)]
    st.write("Matches:", matches.geometry)
    if len(matches.geometry) > 0:
        st.write("Point is contained in polygon(s).")
    else:
        st.write("WARNING: Point not contained in polygons.")

    # Display map with polygons centred on the geodataframe or restored view from session state
    centroid = gdf.geometry.centroid
    lat = centroid.y.mean()
    lon = centroid.x.mean()

    # Check if 'zoom' and 'center' exist in session state
    #if center == {}:
    #    st.session_state["center"] = {
    #        'lat': centroid.y.mean(), 
    #        'lng': centroid.x.mean()
    #        }
    #if zoom == 0:
    #    st.session_state['zoom'] = 11

    st.write("Session state before making map:")
    st.write(st.session_state)

    #m = folium.Map(location=[st.session_state.center['lat'], st.session_state.center['lng']], zoom_start=st.session_state['zoom'])
    m = folium.Map(location=[lat, lon], zoom_start=zoom)
    # Add polygons to the map
    polygon_layers = {}
    for idx, row in gdf.iterrows():
        style_function=lambda feature: {
            "fillColor": "yellow" 
            if shape(feature["geometry"]).contains(clicked_point)
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

    # Highlight clicked polygon
    if st_data.get("last_clicked"):
        # Extract selected polygon coordinates
        selected = st_data.get("last_clicked", None)
        if selected:
            lat, lon = selected["lat"], selected["lng"]

            # Update session state with the clicked point
            st.session_state['clicked_point'] = Point(lon, lat)
            clicked_point = Point(lon, lat)

            # Ensure the CRS of the clicked point matches the GeoDataFrame
            #clicked_point_gdf = gpd.GeoDataFrame(geometry=[clicked_point], crs=gdf.crs)

            # Find the polygon containing the clicked point
            selected_polygon = gdf[gdf.geometry.contains(clicked_point)]

            if not selected_polygon.empty:
                st.write("Selected polygon(s):", selected_polygon)

                # Add the highlighted polygon to the map
                for _, row in selected_polygon.iterrows():
                    folium.GeoJson(
                        row.geometry,
                        style_function=lambda x: {
                            'fillColor': 'yellow',
                            'color': 'black',
                            'weight': 2,
                            'fillOpacity': 0.7
                        },
                        tooltip=folium.features.GeoJsonTooltip(
                            fields=gdf.columns.tolist(),  # Use existing columns in GeoDataFrame
                            aliases=gdf.columns.tolist(),  # Use column names as aliases
                            sticky=True
                        ),
                    ).add_to(m)

                # Re-render the updated map in Streamlit
                st_data = st_folium(m, width=700, height=500)
            else:
                st.write("No polygon contains the selected point.")
        else:
            st.write("No point selected.")
        
    # Store session state values for the current session
    st.session_state['zoom'] = zoom
    st.session_state['center'] = center

# Then to deploy it, type:
# streamlit run twinland-app.py
# or
# streamlit run twinland-app.py --server.enableCORS false --server.enableXsrfProtection false
# and open the browser at the provided Local URL