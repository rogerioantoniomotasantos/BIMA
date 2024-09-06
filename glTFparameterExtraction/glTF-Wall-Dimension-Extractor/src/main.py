import pandas as pd
import ast
import ifcopenshell
from ifcopenshell.api import run
from utils import load_config, extract_extras_from_gltf, save_extras_to_excel, calculate_distances, save_distances_to_excel
from WallDimensions import calculate_wall_dimensions, format_dimensions

# Load Configuration
config = load_config()

# Extract and save extras from GLTF
extras = extract_extras_from_gltf(config['gltf_file_path'])
save_extras_to_excel(extras, config['extras_output_path'])

# Load extras data and process the bounding box
df = pd.read_excel(config['extras_output_path'])
bounding_box_string = df.loc[df['Property'] == 'Bounding Box', 'Value'].values[0]
points = ast.literal_eval(bounding_box_string)


# Calculate distances and save
distances = calculate_distances(points)
save_distances_to_excel(distances, config['distances_output_path'])

# Process the distances to get wall dimensions
distances_df = pd.read_excel(config['distances_output_path'])
sorted_distances = distances_df.sort_values(by='Distance')

thickness = sorted_distances.iloc[0]['Distance']
length = sorted_distances.iloc[-1]['Distance']
height = sorted_distances.iloc[len(sorted_distances) // 2]['Distance']

print(f"Potential Wall Dimensions:\nThickness: {thickness}\nHeight: {height}\nLength: {length}")

# Create IFC File
def create_ifc_wall(length, height, thickness, ifc_output_path):
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
    representation = run("geometry.add_wall_representation", model, context=body, length=length, height=height, thickness=thickness)
    run("geometry.assign_representation", model, product=wall, representation=representation)

    run("spatial.assign_container", model, relating_structure=storey, product=wall)

    origin = model.createIfcAxis2Placement3D(
        model.createIfcCartesianPoint((0.0, 0.0, 10.0)),
        model.createIfcDirection((0.0, 0.0, 1.0)),
        model.createIfcDirection((1.0, 0.0, 0.0)),
    )
    placement = model.createIfcLocalPlacement(None, origin)
    wall.ObjectPlacement = placement

    model.write(ifc_output_path)
    print(f"IFC file created at {ifc_output_path}")


# After you read the distances from the Excel file
distances_df = pd.read_excel(config['distances_output_path'])

# Calculate dimensions
thickness, height, length = calculate_wall_dimensions(distances_df)

# Print or log the wall dimensions
print(format_dimensions(thickness, height, length))

# Create the IFC wall file using the calculated dimensions
create_ifc_wall(float(length), float(height), float(thickness), config['ifc_output_path'])
