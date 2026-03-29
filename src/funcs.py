import madina as md
import madina.una.tools as una
import pandas as pd
import geopandas as gpd
import numpy as np
from shapely import Point, MultiPoint, LineString, Polygon

berlin = md.Zonal()

berlin.load_layer(
    name='sidewalks',
    source='/workspaces/exp_sidewalk_planning/data/berlin/sidewalks_pseudo.geojson'
)

berlin.load_layer('buildings', '/workspaces/exp_sidewalk_planning/data/berlin/buildings_pseudo.geojson')
berlin.load_layer('kitas', '/workspaces/exp_sidewalk_planning/data/berlin/kitas_pseudo.geojson')
berlin.describe()

berlin.create_street_network(source_layer="sidewalks", node_snapping_tolerance=0.1)

berlin.insert_node(label='origin', layer_name="kitas")
berlin.insert_node(label='destination', layer_name="buildings")

berlin.create_graph()

df = gpd.read_file('data/berlin/perceptions/berlin_perceptions_lor.geojson')


def betweeness(origin:str, destination:str, job_id:int, between_radius: int, detour_ratio:float=1.2, beta:float = 0.001) -> list:
    
    berlin.clear_nodes()
    berlin.insert_node(layer_name=origin, label='origin')
    berlin.insert_node(layer_name=destination, label='destination')
    berlin.create_graph()

    una.betweenness(
        berlin,
        search_radius = between_radius,
        detour_ratio=detour_ratio,
        decay=True,
        decay_method="exponent",
        beta=beta,
        turn_penalty=True,
        closest_destination=False,
        elastic_weight = True,
        knn_weight = [0.5, 0.25, 0.25],
        knn_plateau = 400,
        save_betweenness_as="betweenness",
        num_cores=8
    )
    
    gdf = berlin['sidewalks'].gdf
    cols = ['strassenna','bezirk', 'geometry', 'weight', 'betweenness']
    gdf = gdf[cols]
    #gdf = gdf.to_crs(epsg=4326)
       
    return gdf
