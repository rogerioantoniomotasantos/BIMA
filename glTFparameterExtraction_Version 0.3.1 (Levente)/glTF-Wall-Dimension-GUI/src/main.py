import os
import json
import ifcopenshell
from ifcopenshell.api import run
import math
import pandas as pd
import numpy as np

def extract_extras_from_gltf(file_path):
    """Parses extras data from a GLTF file."""
    with open(file_path, 'r') as f:
        gltf_data = json.load(f)
    return gltf_data.get('extras', {})

def calculate_center_point(bounding_box):
    """Calculates the center point of a bounding box."""
    x_coords = [point[0] for point in bounding_box]
    y_coords = [point[1] for point in bounding_box]
    z_coords = [point[2] for point in bounding_box]

    center_x = sum(x_coords) / len(x_coords)
    center_y = sum(y_coords) / len(y_coords)
    center_z = sum(z_coords) / len(z_coords)

    return (center_x, center_y, center_z)

def calculate_wall_orientation(bounding_box):
    """Calculates the orientation of the wall based on the bounding box."""
    max_length = 0
    orientation_vector = (1.0, 0.0, 0.0)  # Default fallback orientation

    # Iterate through all pairs of vertices in the bounding box
    for i in range(len(bounding_box)):
        for j in range(i + 1, len(bounding_box)):
            vertex1 = bounding_box[i]
            vertex2 = bounding_box[j]

            # Calculate the direction vector in the X-Y plane
            direction_vector = (
                vertex2[0] - vertex1[0],  # X
                vertex2[1] - vertex1[1],  # Y
                0  # Ignore Z for orientation
            )
            length = math.sqrt(direction_vector[0]**2 + direction_vector[1]**2)

            # Update if this is the longest edge
            if length > max_length:
                max_length = length
                orientation_vector = (
                    direction_vector[0] / length,  # Normalize X
                    direction_vector[1] / length,  # Normalize Y
                    0.0  # Z always 0 for wall orientation
                )

    return orientation_vector

def create_ifc_project_structure(model):
    """Creates the base project structure in an IFC file."""
    project = run("root.create_entity", model, ifc_class="IfcProject", name="Multi_Wall_Project")
    run("unit.assign_unit", model, length={"is_metric": True, "raw": "METERS"})

    context = run("context.add_context", model, context_type="Model")
    body = run("context.add_context", model, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW")

    site = run("root.create_entity", model, ifc_class="IfcSite", name="Site")
    building = run("root.create_entity", model, ifc_class="IfcBuilding", name="Building A")
    storey = run("root.create_entity", model, ifc_class="IfcBuildingStorey", name="Ground Floor")

    run("aggregate.assign_object", model, relating_object=project, products=[site])
    run("aggregate.assign_object", model, relating_object=site, products=[building])
    run("aggregate.assign_object", model, relating_object=building, products=[storey])

    return project, context, body, storey

def create_wall(model, body, storey, base_point, orientation,bounding_box, dimensions, wall_name):
    """Creates a wall in the IFC model."""
    wall = run("root.create_entity", model, ifc_class="IfcWall", name=wall_name)
    wall_origin = model.createIfcAxis2Placement3D(
        model.createIfcCartesianPoint(base_point),
        model.createIfcDirection((0.0, 0.0, 1.0)),
        # model.createIfcDirection(orientation),
    )
    wall.ObjectPlacement = model.createIfcLocalPlacement(None, wall_origin)
    
    ## Technically possible
    # bbox_tuple = [tuple(b) for b in bounding_box]
    # vertices = [bbox_tuple]
    # faces = [[
    #         (1,3,0), 
    #         (1,6,3), 
    #         (2,0,3), 
    #         (3,5,2), 
    #         (0,2,1),
    #         (2,7,1),
    #         (5,4,2),
    #         (4,7,2),
    #         (7,1,0),
    #         (7,4,6),
    #         (7,6,1),
    #         (4,5,3),
    #         (3,6,4),
    #           ]]
    #wall_representation = run("geometry.add_mesh_representation", model, context=body, vertices=vertices, faces=faces)

    
    wall_representation = run("geometry.add_wall_representation", model, context=body,
                              length=dimensions[0], height=dimensions[2], thickness=dimensions[1])
    run("geometry.assign_representation", model, product=wall, representation=wall_representation)
    run("spatial.assign_container", model, relating_structure=storey, products=[wall])

def save_parameters_to_excel(parameters, output_excel_path):
    """Saves entity parameters to an Excel file."""
    df = pd.DataFrame(parameters)
    df.to_excel(output_excel_path, index=False)
    print(f"Parameters saved to {output_excel_path}")

def process_multiple_gltf_files(gltf_files, output_ifc_path):
    """Processes multiple GLTF files and writes them into a single IFC file."""
    model = ifcopenshell.file(schema="IFC4")
    project, context, body, storey = create_ifc_project_structure(model)

    parameters = []
    reference_center = None

    for idx, gltf_file in enumerate(gltf_files):
        gltf_extras = extract_extras_from_gltf(gltf_file)

        # Extract dimensions from bounding_box_size
        dimensions = gltf_extras.get("bounding_box_size", [1.0, 1.0, 1.0])
        dimensions = (dimensions + [1.0] * 3)[:3]
        #dimensions.sort()

        # Extract bounding box and calculate center point
        bounding_box = gltf_extras.get("bounding_box", [])
        if not bounding_box:  # Handle empty or missing bounding box
            print(f"Warning: No bounding_box found for {gltf_file}. Skipping this wall.")
            continue

        center_point = calculate_center_point(bounding_box)

        # Set reference center point for the first wall
        if reference_center is None:
            reference_center = center_point

        # Calculate relative position
        relative_position = (
            center_point[0] - reference_center[0],
            center_point[1] - reference_center[1],
            center_point[2] - reference_center[2]
        )

        # Calculate wall orientation
        orientation = calculate_wall_orientation(bounding_box)

        # Adjust base point (placement point)
        length = dimensions[2]  # Length of the wall
        offset = (
            orientation[0] * length / 2,
            orientation[1] * length / 2,
            orientation[2] * length / 2
        )
        adjusted_base_point = (
            relative_position[0] - offset[0],
            relative_position[1] - offset[1],
            relative_position[2] - offset[2]
        )

        
        x = dimensions[0]
        y = dimensions[1]
        z = dimensions[2]
        
        center_point = np.array(center_point)
        center_point = center_point - np.array([x/2, y/2, z/2])
        adjusted_base_point = center_point.tolist()
        
        # Create wall in IFC
        create_wall(model, body, storey, adjusted_base_point, orientation,bounding_box, dimensions, wall_name=f"Wall_{idx+1}")

        # Append parameters for the Excel sheet
        parameters.append({
            "Entity": f"Wall_{idx+1}",
            "Length": dimensions[2],
            "Height": dimensions[1],
            "Thickness": dimensions[0],
            "Center Point": center_point,
            "Orientation": orientation
        })

    # Save the IFC file
    model.write(output_ifc_path)
    print(f"IFC file saved to {output_ifc_path}")

    # Save parameters to an Excel file
    output_excel_path = os.path.splitext(output_ifc_path)[0] + "_parameters.xlsx"
    save_parameters_to_excel(parameters, output_excel_path)


def main():
    """Main function to handle multiple GLTF files."""
    from tkinter import filedialog
    from tkinter import Tk

    Tk().withdraw()  # Hide the root Tkinter window
    gltf_files = filedialog.askopenfilenames(
        title="Select GLTF Files",
        filetypes=[("GLTF files", "*.gltf")]
    )

    if not gltf_files:
        print("No GLTF files selected.")
        return

    output_ifc_path = filedialog.asksaveasfilename(
        title="Save IFC File As",
        defaultextension=".ifc",
        filetypes=[("IFC files", "*.ifc")]
    )

    if not output_ifc_path:
        print("No output path provided.")
        return

    process_multiple_gltf_files(gltf_files, output_ifc_path)

if __name__ == "__main__":
    main()