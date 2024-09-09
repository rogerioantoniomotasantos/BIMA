import os
import json
import pandas as pd
import ast
from itertools import combinations
from math import sqrt


def load_config(config_file="config.json"):
    config_path = os.path.join(os.path.dirname(__file__), config_file)
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"Configuration file not found at {config_path}")
        exit(1)



def extract_extras_from_gltf(file_path):
    try:
        with open(file_path, 'r') as f:
            gltf_data = json.load(f)
        extras = gltf_data.get('extras', None)
        return extras
    except FileNotFoundError:
        print(f"GLTF file not found at {file_path}")
        return None

def save_extras_to_excel(extras, output_path):
    if extras:
        data = {
            'Property': ['Bounding Box', 'Object ID', 'Object Name', 'Object Type'],
            'Value': [
                str(extras.get('bounding_box', [])),
                extras.get('object_id', ''),
                extras.get('object_name', ''),
                extras.get('object_type', '')
            ]
        }
        df = pd.DataFrame(data)
        df.to_excel(output_path, index=False)
        print(f"Extras data saved to {output_path}")
    else:
        print("No extras found to save.")

def calculate_distances(points):
    def euclidean_distance(point1, point2):
        return sqrt(sum((a - b) ** 2 for a, b in zip(point1, point2)))

    distances = {}
    for (i, p1), (j, p2) in combinations(enumerate(points), 2):
        dist = euclidean_distance(p1, p2)
        distances[f"Point {i+1} to Point {j+1}"] = dist
    return distances

def save_distances_to_excel(distances, output_path):
    df = pd.DataFrame(list(distances.items()), columns=['Points Pair', 'Distance'])
    df.to_excel(output_path, index=False)
    print(f"Distance data saved to {output_path}")
