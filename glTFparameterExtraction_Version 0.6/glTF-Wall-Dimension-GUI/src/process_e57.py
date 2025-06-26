import os
import numpy as np
import open3d as o3d
import pandas as pd
import pye57
import ifcopenshell
from ifcopenshell.api import run

color_map = {
    (255, 0, 0): "IfcWall",
    (0, 255, 0): "IfcDoor",
    (0, 0, 255): "IfcFurniture",
    (128, 128, 128): "IfcSlab",
}

def extract_clusters_from_e57(e57_path):
    e57 = pye57.E57(e57_path)
    data = e57.read_scan(0, colors=True, ignore_missing_fields=True)
    points = np.vstack((data["cartesianX"], data["cartesianY"], data["cartesianZ"])).T
    colors = np.vstack((data["colorRed"], data["colorGreen"], data["colorBlue"])).T

    unique_colors = np.unique(colors, axis=0)
    clusters = []

    for color in unique_colors:
        mask = np.all(colors == color, axis=1)
        cluster_points = points[mask]
        if len(cluster_points) >= 30:
            clusters.append((tuple(color.tolist()), cluster_points))

    return clusters

def reconstruct_mesh(cluster_points, name="mesh"):
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(cluster_points)

    pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.05, max_nn=30))
    pcd.orient_normals_consistent_tangent_plane(50)

    # Alpha shape surface reconstruction
    alpha = 0.05
    mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_alpha_shape(pcd, alpha)
    mesh.compute_vertex_normals()

    # Save mesh for visual debugging
    o3d.io.write_triangle_mesh(f"mesh_debug_{name}.ply", mesh)

    return mesh

def create_ifc_project_structure(model):
    project = run("root.create_entity", model, ifc_class="IfcProject", name="E57_Project")
    run("unit.assign_unit", model, length={"is_metric": True, "raw": "METERS"})
    context = run("context.add_context", model, context_type="Model")
    body = run("context.add_context", model, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW")
    site = run("root.create_entity", model, ifc_class="IfcSite", name="Site")
    building = run("root.create_entity", model, ifc_class="IfcBuilding", name="Building A")
    storey = run("root.create_entity", model, ifc_class="IfcBuildingStorey", name="Ground Floor")
    run("aggregate.assign_object", model, relating_object=project, products=[site])
    run("aggregate.assign_object", model, relating_object=site, products=[building])
    run("aggregate.assign_object", model, relating_object=building, products=[storey])
    return model, context, storey

def create_ifc_mesh_entity(model, context, storey, mesh, name, ifc_class):
    if len(mesh.triangles) == 0 or len(mesh.vertices) == 0:
        print(f"⚠️ Skipping empty mesh: {name}")
        return

    entity = run("root.create_entity", model, ifc_class=ifc_class, name=name)
    vertices = np.asarray(mesh.vertices)
    triangles = np.asarray(mesh.triangles)

    coord_list = model.createIfcCartesianPointList3D(vertices.tolist())

    face_set = model.createIfcTriangulatedFaceSet(
        Coordinates=coord_list,
        CoordIndex=[tuple(tri.tolist()) for tri in triangles],
        Closed=True
    )

    shape_representation = model.createIfcShapeRepresentation(
        context,
        "Body",
        "Tessellation",
        [face_set],
    )
    entity.Representation = model.createIfcProductDefinitionShape(None, None, [shape_representation])
    run("spatial.assign_container", model, relating_structure=storey, products=[entity])

def process_segmented_e57_to_ifc(e57_path, output_ifc_path):
    print(f"\n🔍 Reading: {e57_path}")
    clusters = extract_clusters_from_e57(e57_path)
    print(f"📦 Found {len(clusters)} clusters")

    model = ifcopenshell.file(schema="IFC4")
    model, context, storey = create_ifc_project_structure(model)

    parameters = []

    for idx, (color, points) in enumerate(clusters):
        print(f"🛠️ Reconstructing object {idx+1} with {len(points)} points and color {color}")
        ifc_class = color_map.get(color, "IfcBuildingElementProxy")
        name = f"object_{idx+1}"
        mesh = reconstruct_mesh(points, name)
        create_ifc_mesh_entity(model, context, storey, mesh, name, ifc_class)
        parameters.append({"Entity": name, "Class": ifc_class, "Points": len(points)})

    model.write(output_ifc_path)
    print(f"✅ IFC file saved to: {output_ifc_path}")

    output_excel_path = os.path.splitext(output_ifc_path)[0] + "_parameters.xlsx"
    pd.DataFrame(parameters).to_excel(output_excel_path, index=False)
    print(f"🧾 Parameters saved to: {output_excel_path}")
