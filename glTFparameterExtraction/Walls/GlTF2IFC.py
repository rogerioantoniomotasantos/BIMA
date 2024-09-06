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

# Example usage
file_path = r"C:\Users\motasan\Desktop\htw-berlin\glTFparameterExtraction\Walls\Wall_1 - E101.gltf"  # Replace with your actual GLTF file path
output_path = r"C:\Users\motasan\Desktop\htw-berlin\glTFparameterExtraction\Walls\extras_data.xlsx"  # Replace with your desired Excel file path

extras = extract_extras_from_gltf(file_path)
save_extras_to_excel(extras, output_path)

# Load the Excel file
df = pd.read_excel(output_path)  # Update with your actual file path

# Extract the bounding box string from the "Value" column where the "Property" is "Bounding Box"
bounding_box_string = df.loc[df['Property'] == 'Bounding Box', 'Value'].values[0]

# Convert the bounding box string into a list of points
points = ast.literal_eval(bounding_box_string)

# Function to calculate Euclidean distance between two points
def euclidean_distance(point1, point2):
    return sqrt(sum((a - b) ** 2 for a, b in zip(point1, point2)))

# Calculate distances between all pairs of points
distances = {}
for (i, p1), (j, p2) in combinations(enumerate(points), 2):
    dist = euclidean_distance(p1, p2)
    distances[f"Point {i+1} to Point {j+1}"] = dist

# Print the distances
for points_pair, distance in distances.items():
    print(f"Distance from {points_pair}: {distance}")

# Optionally, save the distances to a new Excel file
distances_df = pd.DataFrame(list(distances.items()), columns=['Points Pair', 'Distance'])
distances_df.to_excel(r"C:\Users\motasan\Desktop\htw-berlin\glTFparameterExtraction\Walls\distances_data.xlsx", index=False)


# Assuming 'distances_df' is the DataFrame with calculated distances
distances_df = pd.read_excel(r"C:\Users\motasan\Desktop\htw-berlin\glTFparameterExtraction\Walls\distances_data.xlsx")

# Sort distances to help categorize them
sorted_distances = distances_df.sort_values(by='Distance')

# Extract potential thickness (smallest distance), height (middle distances), and length (largest distances)
thickness = sorted_distances.iloc[0]['Distance']
length = sorted_distances.iloc[-1]['Distance']
height = sorted_distances.iloc[len(sorted_distances) // 2]['Distance']

print(f"Potential Wall Dimensions:\nThickness: {thickness}\nHeight: {height}\nLength: {length}")

filename = "\Dimnesions2IfcWall.ifc"
folder_path = r"C:\Users\motasan\Desktop\htw-berlin\glTFparameterExtraction\Walls"
length = float(length)
height = float(height)
thickness = float(thickness)

# Create a blank model
model = ifcopenshell.file()

# All projects must have one IFC Project element
project = run("root.create_entity", model, ifc_class="IfcProject", name="DeepDive_Wall")

# Geometry is optional in IFC, but because we want to use geometry in this example, let's define units
# Assigning without arguments defaults to metric units
run("unit.assign_unit", model, length = {"is_metric": True, "raw": "METERS"})

# Let's create a modeling geometry context, so we can store 3D geometry (note: IFC supports 2D too!)
context = run("context.add_context", model, context_type="Model")
# In particular, in this example we want to store the 3D "body" geometry of objects, i.e. the body shape
body = run(
    "context.add_context", model,
    context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", 
)

# Create a site, building, and storey. Many hierarchies are possible.
site = run("root.create_entity", model, ifc_class="IfcSite", name="My Site")
building = run("root.create_entity", model, ifc_class="IfcBuilding", name="Building A")
storey = run("root.create_entity", model, ifc_class="IfcBuildingStorey", name="Ground Floor")

# Since the site is our top level location, assign it to the project
# Then place our building on the site, and our storey in the building
run("aggregate.assign_object", model, relating_object=project, product=site)
run("aggregate.assign_object", model, relating_object=site, product=building)
run("aggregate.assign_object", model, relating_object=building, product=storey)

# Let's create a new wall
wall = run("root.create_entity", model, ifc_class="IfcWall")
# Add a new wall-like body geometry, 5 meters long, 3 meters high, and 200mm thick
representation = run("geometry.add_wall_representation", model, context=body, length=length, height=height, thickness=thickness)
# Assign our new body geometry back to our wall
run("geometry.assign_representation", model, product=wall, representation=representation)

# Place our wall in the ground floor
run("spatial.assign_container", model, relating_structure=storey, product=wall)

## how-to?
origin = model.createIfcAxis2Placement3D(
            model.createIfcCartesianPoint((0.0, 0.0, 10.0)),
            model.createIfcDirection((0.0, 0.0, 1.0)),
            model.createIfcDirection((1.0, 0.0, 0.0)),
        )
placement = model.createIfcLocalPlacement(None, origin)


wall.ObjectPlacement = placement

file_path = (folder_path + filename)
model.write(file_path)