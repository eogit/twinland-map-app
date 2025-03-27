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

    # Add polygons to the map
    polygon_layers = {}
   
    for idx, row in gdf.iterrows():
        layer = folium.GeoJson(
            row.geometry,
            name=f"Polygon {idx}",
            style_function=lambda x: {"fillColor": "blue", "color": "black", "weight": 2}
        )
        layer.add_to(m)
        polygon_layers[f"Polygon {idx}"] = layer

    #for _, row in gdf.iterrows():
    #    folium.GeoJson(row.geometry, name=row['id']).add_to(m)

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

    # Highlight clicked polygon
    if st_data.get("last_clicked"):
        lat, lon = st_data["last_clicked"]["lat"], st_data["last_clicked"]["lng"]

        # Find the polygon containing the clicked point
        clicked_point = gpd.GeoDataFrame(geometry=[gpd.points_from_xy([lon], [lat])[0]], crs=gdf.crs)
        selected_polygon = gdf[gdf.contains(clicked_point.geometry.iloc[0])]

        if not selected_polygon.empty:
            # Highlight the selected polygon
            m = folium.Map(
                location=[gdf.geometry.centroid.y.mean(), gdf.geometry.centroid.x.mean()],
                zoom_start=12
            )
           
            for idx, row in gdf.iterrows():
                color = "yellow" if row.geometry == selected_polygon.geometry.iloc[0] else "blue"
                folium.GeoJson(
                    row.geometry,
                    style_function=lambda x, color=color: {
                        "fillColor": color,
                        "color": "black",
                        "weight": 3
                    }
                ).add_to(m)

            # Redisplay the map with highlighting
            st_folium(m, width=700, height=500)
        
            '''
            response = requests.post("https://your-api-url.com", json=payload)
            st.write("API Response:", response.json())
            '''
        
        else:
            st.write("Please select a polygon on the map.")

# Then to deploy it, type:
# streamlit run twinland-app.py
# and open the browser at the provided Local URL