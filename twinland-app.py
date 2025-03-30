import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import geopandas as gpd
from shapely.geometry import Point, Polygon, shape
import requests

st.title("Twinland map app")
st.write("Deployed on [docs.streamlit.io](https://docs.streamlit.io/).")

vector_file = 'Polygons_small.shp'

# multiple columns
col1, col2 = st.columns((2,1))

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
        #st.write("Clicked point from session state:", st.session_state.clicked_point)
        c = st.session_state.clicked_point
    
    # Check if the Point is contained in any of the polygons
    #st.write("Clicked point:", c)
    matches = gdf[gdf.geometry.contains(c)]
    with col2:
        st.write("Matches:", matches.geometry)
        if len(matches.geometry) > 0:
            st.write("Point is contained in polygon(s).")
        else:
            st.write("WARNING: Point not contained in polygons.")

    # Display map with polygons centred on the geodataframe or restored view from session state
    centroid = gdf.geometry.centroid
    #st.write("Centroid:", centroid.y.mean(), centroid.x.mean())

    # Check if 'zoom' and 'center' exist in session state
    if 'center' not in st.session_state or st.session_state["center"] == []:
        #st.write("No center in session state.")
        st.session_state["center"] = {
            'lat': centroid.y.mean(), 
            'lng': centroid.x.mean()
            }
    if 'zoom' not in st.session_state or st.session_state['zoom'] == []:
        #st.write("No zoom in session state.")
        st.session_state['zoom'] = 11

    with col2:
        st.write("Session state now:")
        st.write(st.session_state)
        #st.write("Session state center:")
        #st.write(st.session_state.center)
        #st.write("Session state zoom:")
        #st.write(st.session_state['zoom'])

    m = folium.Map(location=[st.session_state.center['lat'], st.session_state.center['lng']], zoom_start=st.session_state['zoom'])
    with col1:
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

            # Update session state with the clicked point
            st.session_state['clicked_point'] = Point(lon, lat)
            clicked_point = Point(lon, lat)

            # Ensure the CRS of the clicked point matches the GeoDataFrame
            clicked_point_gdf = gpd.GeoDataFrame(geometry=[clicked_point], crs=gdf.crs)

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
        
        '''
        # Highlight clicked polygon
        if st_data.get("last_clicked"):
            # Extract selected polygon coordinates
            selected = st_data.get("last_clicked", None)
            if selected:
                lat, lon = selected["lat"], selected["lng"]

            # Find the polygon containing the clicked point
            clicked_point = gpd.GeoDataFrame(geometry=[gpd.points_from_xy([lon], [lat])[0]], crs=gdf.crs)
            st.session_state['clicked_point'] = Point(lon,lat)
            c = Point(lon,lat)
            st.write("Selected coordinates:", st.session_state['clicked_point'])
            #selected_polygon = gdf[gdf.contains(clicked_point.geometry.iloc[0])]
        else:
            clicked_point = None
            #selected_polygon = None
        '''
        
    # Hack into the session state to get the map's zoom and center and preserve them
    #st.write("Session state after clicking:")
    #st.write(st.session_state)
    #st.write("Number of keys: ", len(st.session_state.items()))
    #for k,v in st.session_state.items():
    #    st.write(k, ": ", v)
    #st.write("Session context:")
    #st.write(st.context.cookies)
    #st.write(st.context.headers)

    for key, value in st.session_state.items():
        if len(key)>60:
            #st.write(f"{key}: {value}")
            #st.write("Session state key:", key)
            #st.write("Inside this key:")
            for k,v in value.items():
                #st.write(k, ": ", v)
                if k == 'zoom':
                    zoom = v
                    #st.write("Zoom: ", zoom)
                if k=="center":
                    center = v
                    #st.write("Center: ", center)
    st.session_state['zoom'] = zoom
    st.session_state['center'] = center

# Then to deploy it, type:
# streamlit run twinland-app.py
# or
# streamlit run twinland-app.py --server.enableCORS false --server.enableXsrfProtection false
# and open the browser at the provided Local URL