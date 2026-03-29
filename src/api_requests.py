import pandas as pd
import geopandas as gpd
import requests
import json

def execute_process(origin:str, destination:str, search_radius: int, detour_ratio:float = 1.2, knn_plateau:int = 400, beta:float = 0.001):

  url = "http://host.docker.internal:5000/api/model/processes/betweeness_calculation/execution"

  payload = json.dumps({
    "inputs": {
      "origin": origin,
      "destination": destination,
      "search_radius": search_radius,
      "detour_ratio":detour_ratio,
      "knn_plateau": knn_plateau,
      "beta": beta
      
    },
    "outputs": {},
    "response": "raw",
    "subscriber": {}
  })
  headers = {
    'Content-Type': 'application/json'
  }

  response = requests.request("POST", url, headers=headers, data=payload)
  job_id = response.json().get( 'job_id')
  return job_id

def get_results(job_id):
    
    url = f"http://host.docker.internal:5000/api/model/jobs/{job_id}/results"

    payload={}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    gdf = gpd.GeoDataFrame.from_features(data['result']['features'])
    return gdf
