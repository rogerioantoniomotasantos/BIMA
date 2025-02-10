import os
import json
import ifcopenshell
from ifcopenshell.api import run
import pandas as pd
import numpy as np

# Object type to IFC class mapping
catalog = {
    "wall": "IfcWall",
    "table": "IfcFurniture",
    "chair": "IfcFurniture",
    "cabinet": "IfcFurniture",
    "monitor": "IfcFurniture",
    "floor": "IfcSlab",
    "ceiling": "IfcSlab",
}

def extract_extras_from_gltf(file_path):
    with open(file_path, 'r') as f:
        gltf_data = json.load(f)
    return gltf_data.get('extras', {})

def calculate_center_point(bounding_box):
    """Calculates the center point from a bounding box."""
    if isinstance(bounding_box, dict) and 'min' in bounding_box and 'max' in bounding_box:
        min_coords = np.array(bounding_box['min'])
        max_coords = np.array(bounding_box['max'])
        return ((min_coords + max_coords) / 2).tolist()

    # If bounding box is an array of points, calculate the average
    x_coords = [point[0] for point in bounding_box]
    y_coords = [point[1] for point in bounding_box]
    z_coords = [point[2] for point in bounding_box]

    center_x = sum(x_coords) / len(x_coords)
    center_y = sum(y_coords) / len(y_coords)
    center_z = sum(z_coords) / len(z_coords)

    return [center_x, center_y, center_z]

def create_ifc_project_structure(model):
    project = run("root.create_entity", model, ifc_class="IfcProject", name="Multi_Object_Project")
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

def adjust_base_point(center_point, dimensions):
    """Adjusts the base point to place the object correctly in the IFC model."""
    width, length, height = dimensions
    return [
        center_point[0] - width / 2,
        center_point[1] - length / 2,
        center_point[2]
    ]

def create_ifc_entity(model, context, storey, base_point, dimensions, object_name, ifc_class):
    """Creates a generic IFC entity with basic geometry."""
    entity = run("root.create_entity", model, ifc_class=ifc_class, name=object_name)

    origin = model.createIfcAxis2Placement3D(
        model.createIfcCartesianPoint(base_point),
        model.createIfcDirection((0.0, 0.0, 1.0)),  # Z-axis as up direction
        model.createIfcDirection((1.0, 0.0, 0.0)),  # X-axis direction
    )
    entity.ObjectPlacement = model.createIfcLocalPlacement(None, origin)

    width, length, height = dimensions

    # Create a simple rectangular profile for extrusion
    base_profile = model.createIfcArbitraryClosedProfileDef(
        "AREA",
        None,
        model.createIfcPolyline([
            model.createIfcCartesianPoint((0.0, 0.0)),
            model.createIfcCartesianPoint((width, 0.0)),
            model.createIfcCartesianPoint((width, length)),
            model.createIfcCartesianPoint((0.0, length)),
            model.createIfcCartesianPoint((0.0, 0.0)),  # Close the loop
        ]),
    )

    extrusion_direction = model.createIfcDirection((0.0, 0.0, 1.0))

    solid_geometry = model.createIfcExtrudedAreaSolid(
        SweptArea=base_profile,
        ExtrudedDirection=extrusion_direction,
        Depth=height,
    )

    shape_representation = model.createIfcShapeRepresentation(
        context,
        "Body",
        "SweptSolid",
        [solid_geometry],
    )
    entity.Representation = model.createIfcProductDefinitionShape(None, None, [shape_representation])

    run("spatial.assign_container", model, relating_structure=storey, products=[entity])

def process_multiple_gltf_files(gltf_files, output_ifc_path):
    model = ifcopenshell.file(schema="IFC4")
    project, context, body, storey = create_ifc_project_structure(model)

    parameters = []

    for idx, gltf_file in enumerate(gltf_files):
        gltf_extras = extract_extras_from_gltf(gltf_file)

        object_type = gltf_extras.get("object_type", "unknown").lower()
        ifc_class = catalog.get(object_type)
        if not ifc_class:
            print(f"Warning: No mapping found for object type '{object_type}' in {gltf_file}. Skipping.")
            continue

        dimensions = gltf_extras.get("bounding_box_size", [1.0, 1.0, 1.0])
        dimensions = (dimensions + [1.0] * 3)[:3]  # Ensure 3 values
        dimensions = [max(d, 0.1) for d in dimensions]  # Avoid zero dimensions

        bounding_box = gltf_extras.get("bounding_box", [])
        if not bounding_box:
            print(f"Warning: No bounding_box found for {gltf_file}. Skipping.")
            continue

        center_point = calculate_center_point(bounding_box)
        base_point = adjust_base_point(center_point, dimensions)

        create_ifc_entity(model, body, storey, base_point, dimensions, f"{object_type}_{idx+1}", ifc_class)

        parameters.append({
            "Entity": f"{object_type}_{idx+1}",
            "Class": ifc_class,
            "Dimensions": dimensions,
            "Center Point": center_point,
        })

    model.write(output_ifc_path)
    print(f"IFC file saved to {output_ifc_path}")

    output_excel_path = os.path.splitext(output_ifc_path)[0] + "_parameters.xlsx"
    save_parameters_to_excel(parameters, output_excel_path)

def save_parameters_to_excel(parameters, output_excel_path):
    df = pd.DataFrame(parameters)
    df.to_excel(output_excel_path, index=False)
    print(f"Parameters saved to {output_excel_path}")

def main():
    from tkinter import filedialog
    from tkinter import Tk

    Tk().withdraw()
    gltf_files = filedialog.askopenfilenames(title="Select GLTF Files", filetypes=[("GLTF files", "*.gltf")])

    if not gltf_files:
        print("No GLTF files selected.")
        return

    output_ifc_path = filedialog.asksaveasfilename(title="Save IFC File As", defaultextension=".ifc",
                                                   filetypes=[("IFC files", "*.ifc")])

    if not output_ifc_path:
        print("No output path provided.")
        return

    process_multiple_gltf_files(gltf_files, output_ifc_path)

if __name__ == "__main__":
    main()
