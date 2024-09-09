import os
import json
import pandas as pd
import ast
from itertools import combinations
from math import sqrt
import ifcopenshell
from ifcopenshell.api import run
from WallDimensions import *

def extract_extras_from_gltf(file_path):
    # Load the GLTF file
    with open(file_path, 'r') as f:
        gltf_data = json.load(f)
    
    # Extract the "extras" field
    extras = gltf_data.get('extras', None)
    return extras

def save_extras_to_excel(extras, output_path):
    if extras:
        # Organize data into a dictionary of lists for DataFrame
        data = {
            'Property': ['Bounding Box', 'Object ID', 'Object Name', 'Object Type'],
            'Value': [
                str(extras.get('bounding_box', [])),
                extras.get('object_id', ''),
                extras.get('object_name', ''),
                extras.get('object_type', '')
            ]
        }
        
        # Create a DataFrame
        df = pd.DataFrame(data)
        
        # Save DataFrame to Excel file
        df.to_excel(output_path, index=False)
        print(f"Extras data saved to {output_path}")
    else:
        print("No extras field found to save.")


def process_gltf_file(file_path, output_dir=None):
    # Set project root based on the location of this script
    project_root = os.path.dirname(os.path.abspath(__file__))

    # Set default output directory if not provided
    if output_dir is None:
        output_dir = os.path.join(project_root, '..', 'output')
    
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Load and process the GLTF file
    extras = extract_extras_from_gltf(file_path)
    output_path = os.path.join(output_dir, 'extras_data.xlsx')
    save_extras_to_excel(extras, output_path)

    # Load the Excel file and extract bounding box
    df = pd.read_excel(output_path)
    bounding_box_string = df.loc[df['Property'] == 'Bounding Box', 'Value'].values[0]
    points = ast.literal_eval(bounding_box_string)

    # Calculate distances between points
    def euclidean_distance(point1, point2):
        return sqrt(sum((a - b) ** 2 for a, b in zip(point1, point2)))

    distances = {}
    for (i, p1), (j, p2) in combinations(enumerate(points), 2):
        dist = euclidean_distance(p1, p2)
        distances[f"Point {i+1} to Point {j+1}"] = dist

    for points_pair, distance in distances.items():
        print(f"Distance from {points_pair}: {distance}")

    # Save distances to Excel
    distances_df = pd.DataFrame(list(distances.items()), columns=['Points Pair', 'Distance'])
    distances_output_path = os.path.join(output_dir, 'distances_data.xlsx')
    distances_df.to_excel(distances_output_path, index=False)

    # Calculate wall dimensions
    distances_df = pd.read_excel(distances_output_path)
    sorted_distances = distances_df.sort_values(by='Distance')

    thickness = sorted_distances.iloc[0]['Distance']
    length = sorted_distances.iloc[-1]['Distance']
    height = sorted_distances.iloc[len(sorted_distances) // 2]['Distance']

    print(f"Potential Wall Dimensions:\nThickness: {thickness}\nHeight: {height}\nLength: {length}")

    # Create IFC wall
    filename = "Dimensions2IfcWall.ifc"
    file_path = os.path.join(output_dir, filename)

    model = ifcopenshell.file()
    project = run("root.create_entity", model, ifc_class="IfcProject", name="DeepDive_Wall")
    run("unit.assign_unit", model, length={"is_metric": True, "raw": "METERS"})
    context = run("context.add_context", model, context_type="Model")
    body = run("context.add_context", model, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW")

    site = run("root.create_entity", model, ifc_class="IfcSite", name="My Site")
    building = run("root.create_entity", model, ifc_class="IfcBuilding", name="Building A")
    storey = run("root.create_entity", model, ifc_class="IfcBuildingStorey", name="Ground Floor")

    run("aggregate.assign_object", model, relating_object=project, product=site)
    run("aggregate.assign_object", model, relating_object=site, product=building)
    run("aggregate.assign_object", model, relating_object=building, product=storey)

    wall = run("root.create_entity", model, ifc_class="IfcWall")
    representation = run("geometry.add_wall_representation", model, context=body, length=float(length), height=float(height), thickness=float(thickness))
    run("geometry.assign_representation", model, product=wall, representation=representation)
    run("spatial.assign_container", model, relating_structure=storey, product=wall)

    origin = model.createIfcAxis2Placement3D(
        model.createIfcCartesianPoint((0.0, 0.0, 10.0)),
        model.createIfcDirection((0.0, 0.0, 1.0)),
        model.createIfcDirection((1.0, 0.0, 0.0)),
    )
    placement = model.createIfcLocalPlacement(None, origin)
    wall.ObjectPlacement = placement

    model.write(file_path)
    print(f"IFC file saved to {file_path}")

if __name__ == "__main__":
    # If running directly, you can pass a sample file path and output directory
    sample_gltf_path = "path/to/sample.gltf"  # Replace with an actual path
    process_gltf_file(sample_gltf_path)
