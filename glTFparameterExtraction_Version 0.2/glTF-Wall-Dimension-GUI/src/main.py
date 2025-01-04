import os
import json
import ifcopenshell
from ifcopenshell.api import run
import pandas as pd

def extract_extras_from_gltf(file_path):
    # Load the GLTF file
    with open(file_path, 'r') as f:
        gltf_data = json.load(f)
    return gltf_data.get('extras', {})

def create_ifc_project_structure(model):
    project = run("root.create_entity", model, ifc_class="IfcProject", name="Multi_Element_Project")
    run("unit.assign_unit", model, length={"is_metric": True, "raw": "METERS"})

    context = run("context.add_context", model, context_type="Model")
    body = run("context.add_context", model, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW")

    site = run("root.create_entity", model, ifc_class="IfcSite", name="Site")
    building = run("root.create_entity", model, ifc_class="IfcBuilding", name="Building A")
    storey = run("root.create_entity", model, ifc_class="IfcBuildingStorey", name="Ground Floor")

    run("aggregate.assign_object", model, relating_object=project, product=site)
    run("aggregate.assign_object", model, relating_object=site, product=building)
    run("aggregate.assign_object", model, relating_object=building, product=storey)

    return project, context, body, storey

def save_entity_parameters_to_excel(parameters, output_path):
    # Create a DataFrame from parameters dictionary
    df = pd.DataFrame(parameters)
    # Save DataFrame to Excel
    df.to_excel(output_path, index=False)
    print(f"Entity parameters saved to {output_path}")

def create_wall_with_features(model, body, storey, base_point, orientation, gltf_extras):
    parameters = []

    # Extract dimensions from GLTF extras with default values if missing
    wall_dims = gltf_extras.get("bounding_box_size_wall", [1.0, 1.0, 1.0])
    heater_dims = gltf_extras.get("bounding_box_size_heater", [1.0, 1.0, 1.0])
    window_dims = gltf_extras.get("bounding_box_size_window", [1.0, 1.0, 1.0])

    # Ensure dimensions are exactly three elements long
    wall_dims = (wall_dims + [1.0] * 3)[:3]
    heater_dims = (heater_dims + [1.0] * 3)[:3]
    window_dims = (window_dims + [1.0] * 3)[:3]

    # Create wall
    wall = run("root.create_entity", model, ifc_class="IfcWall", name="Wall")
    wall_origin = model.createIfcAxis2Placement3D(
        model.createIfcCartesianPoint(base_point),
        model.createIfcDirection((0.0, 0.0, 1.0)),
        model.createIfcDirection(orientation),
    )
    wall.ObjectPlacement = model.createIfcLocalPlacement(None, wall_origin)
    wall_representation = run("geometry.add_wall_representation", model, context=body,
                              length=float(wall_dims[2]), height=float(wall_dims[1]), thickness=float(wall_dims[0]))
    run("geometry.assign_representation", model, product=wall, representation=wall_representation)
    run("spatial.assign_container", model, relating_structure=storey, product=wall)
    
    # Save wall parameters
    parameters.append({
        'Entity': 'Wall',
        'Length': wall_dims[2],
        'Height': wall_dims[1],
        'Thickness': wall_dims[0]
    })

    # Create heater
    heater = run("root.create_entity", model, ifc_class="IfcSpaceHeater", name="Heater")
    heater_origin = model.createIfcAxis2Placement3D(
        model.createIfcCartesianPoint((0.5, 0.0, 0.0)),  # Adjust position if needed
        model.createIfcDirection((0.0, 0.0, 1.0)),
        model.createIfcDirection((1.0, 0.0, 0.0)),
    )
    heater.ObjectPlacement = model.createIfcLocalPlacement(wall.ObjectPlacement, heater_origin)
    heater_representation = run("geometry.add_wall_representation", model, context=body,
                                length=float(heater_dims[2]), height=float(heater_dims[1]), thickness=float(heater_dims[0]))
    run("geometry.assign_representation", model, product=heater, representation=heater_representation)
    run("spatial.assign_container", model, relating_structure=storey, product=heater)
    
    # Save heater parameters
    parameters.append({
        'Entity': 'Heater',
        'Length': heater_dims[2],
        'Height': heater_dims[1],
        'Thickness': heater_dims[0]
    })

    # Create window
    window = run("root.create_entity", model, ifc_class="IfcWindow", name="Window")
    window_origin = model.createIfcAxis2Placement3D(
        model.createIfcCartesianPoint((wall_dims[2]/2, 0.0, 1.0)),  # Adjust position if needed
        model.createIfcDirection((0.0, 0.0, 1.0)),
        model.createIfcDirection((1.0, 0.0, 0.0)),
    )
    window.ObjectPlacement = model.createIfcLocalPlacement(wall.ObjectPlacement, window_origin)
    window_representation = run("geometry.add_wall_representation", model, context=body,
                                length=float(window_dims[2]), height=float(window_dims[1]), thickness=float(window_dims[0]))
    run("geometry.assign_representation", model, product=window, representation=window_representation)
    run("spatial.assign_container", model, relating_structure=storey, product=window)
    
    # Save window parameters
    parameters.append({
        'Entity': 'Window',
        'Length': window_dims[2],
        'Height': window_dims[1],
        'Thickness': window_dims[0]
    })

    return parameters

def process_gltf_file(gltf_file_path, output_dir="output"):
    model = ifcopenshell.file(schema="IFC4")
    project, context, body, storey = create_ifc_project_structure(model)

    gltf_extras = extract_extras_from_gltf(gltf_file_path)
    base_point = (0.0, 0.0, 0.0)
    orientation = (1.0, 0.0, 0.0)
    parameters = create_wall_with_features(model, body, storey, base_point, orientation, gltf_extras)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Save the IFC file
    output_ifc_path = os.path.join(output_dir, "MultiElementIfc.ifc")
    model.write(output_ifc_path)
    print(f"IFC file saved to {output_ifc_path}")

    # Save the parameters to Excel
    output_excel_path = os.path.join(output_dir, "assigned_parameters.xlsx")
    save_entity_parameters_to_excel(parameters, output_excel_path)

if __name__ == "__main__":
    sample_gltf_path = "path/to/sample.gltf"  # Replace with actual GLTF path
    process_gltf_file(sample_gltf_path)
