import pandas as pd
import numpy as np
import logging
import streamlit as st
import folium
from folium.plugins import MarkerCluster, Draw
from branca.colormap import linear
from streamlit_folium import st_folium
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
import contextlib
import io


from src.funcs import betweeness
from src.api_requests import execute_process, get_results


logging.basicConfig(level=logging.INFO)

st.set_page_config(layout="wide")

logo = Image.open("data/external/Logo.jpg")

with st.container():

    filter_col, map_col= st.columns([1.3, 3])

    with filter_col:

        selected_origin = st.selectbox("Origin", ["Kindergarten", "Wohnhaus", "Café"])
        selected_destination = st.selectbox("Destination", ["Kindergarten", "Wohnhaus", "Café"])
        radius = st.slider("Search Radius (m)", min_value=200, max_value=600, value=400, step=100)
        detour_ratio = st.slider("Detour Ratio", min_value=1.0, max_value=2.0, value=1.3, step=0.1)
        beta = st.number_input("Beta (decay strength)", min_value=0.0001, max_value=1.0, value=0.1, step=0.01, format="%.4f")
    

    with st.form("location_selection"):
        szenario_button = st.form_submit_button(label="Run Scenario")
            
    if szenario_button:

        jop_id = execute_process(
            origin= selected_origin,
            destination= selected_destination,
            search_radius=radius,
            beta=beta,
            detour_ratio=detour_ratio
        )
        result_gdf = get_results(jop_id)
        result_gdf.set_crs("EPSG:3857", inplace=True)
        st.session_state["result_gdf"] = result_gdf


    with map_col:
        if "result_gdf" in st.session_state:
            result_gdf = st.session_state["result_gdf"]
            gdf_wgs = result_gdf.to_crs(epsg=4326)
            center = gdf_wgs.unary_union.centroid
            home_location = [center.y, center.x]

            colormap = linear.Reds_09.scale(
                result_gdf['betweenness'].min(),
                result_gdf['betweenness'].max()
            )
            colormap.caption = 'Pedestrian Activity'

            def style_function(feature):
                value = feature['properties']['betweenness']
                return {
                    'color': colormap(value),
                    'weight': 3,
                    'opacity': 1
                }

            map_0 = folium.Map(location=home_location, zoom_start=15, tiles="cartodb positron")
            Draw(draw_options={'polyline': False, 'marker': False, 'circlemarker': False}).add_to(map_0)
            MarkerCluster().add_to(map_0)

            folium.GeoJson(
                gdf_wgs,
                name='Betweenness',
                style_function=style_function,
                tooltip=folium.GeoJsonTooltip(fields=["strassenna", "bezirk", "betweenness"]),
            ).add_to(map_0)

            colormap.add_to(map_0)

            st_folium(map_0, height=400, use_container_width=True)
        else:
            # Empty map placeholder
            map_0 = folium.Map(location=[52.491642, 13.396304], zoom_start=13, tiles="cartodb positron")
            Draw(draw_options={'polyline': False, 'marker': False, 'circlemarker': False}).add_to(map_0)
            MarkerCluster().add_to(map_0)
            st_folium(map_0, height=500, use_container_width=True)
            

footer1, footer2 = st.columns([5, 1])
#with footer1:
    #st.write("#### DKSR City Intelligence")
with footer2:
    st.image(logo, width=150)
    

