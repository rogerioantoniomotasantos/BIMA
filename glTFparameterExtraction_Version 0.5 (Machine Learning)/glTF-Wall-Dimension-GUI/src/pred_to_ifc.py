
import numpy as np
import ifcopenshell
from ifcopenshell.api import run
import os

def load_cluster_and_labels(cluster_path, label_path):
    points = np.loadtxt(cluster_path)
    labels = np.loadtxt(label_path, dtype=int)
    if len(points) != len(labels):
        raise ValueError("Number of points and labels do not match.")
    return points, labels

def calculate_bbox(points):
    min_pt = points.min(axis=0)
    max_pt = points.max(axis=0)
    center = (min_pt + max_pt) / 2
    size = max_pt - min_pt
    return center.tolist(), size.tolist()

def create_ifc_model():
    model = ifcopenshell.file(schema="IFC4")
    project = run("root.create_entity", model, ifc_class="IfcProject", name="Labeled Model")
    run("unit.assign_unit", model, length={"is_metric": True, "raw": "METERS"})
    context = run("context.add_context", model, context_type="Model")
    site = run("root.create_entity", model, ifc_class="IfcSite", name="Site")
    building = run("root.create_entity", model, ifc_class="IfcBuilding", name="Building")
    storey = run("root.create_entity", model, ifc_class="IfcBuildingStorey", name="Ground Floor")
    run("aggregate.assign_object", model, relating_object=project, products=[site])
    run("aggregate.assign_object", model, relating_object=site, products=[building])
    run("aggregate.assign_object", model, relating_object=building, products=[storey])
    return model, context, storey

def create_ifc_entity(model, context, storey, base_point, dimensions, label, idx):
    label_map = {
        0: "IfcWall",
        1: "IfcSlab",
        2: "IfcFurniture",
        3: "IfcBuildingElementProxy",
        4: "IfcFurnishingElement"
    }
    ifc_class = label_map.get(label, "IfcBuildingElementProxy")
    name = f"{ifc_class}_{idx}"

    entity = run("root.create_entity", model, ifc_class=ifc_class, name=name)
    origin = model.createIfcAxis2Placement3D(
        model.createIfcCartesianPoint(tuple(map(float, base_point))),
        model.createIfcDirection([0.0, 0.0, 1.0]),
        model.createIfcDirection([1.0, 0.0, 0.0])
    )
    entity.ObjectPlacement = model.createIfcLocalPlacement(None, origin)

    width, length, height = dimensions
    profile = model.createIfcArbitraryClosedProfileDef(
        "AREA", None,
        model.createIfcPolyline([
            model.createIfcCartesianPoint([0.0, 0.0]),
            model.createIfcCartesianPoint([width, 0.0]),
            model.createIfcCartesianPoint([width, length]),
            model.createIfcCartesianPoint([0.0, length]),
            model.createIfcCartesianPoint([0.0, 0.0])
        ])
    )
    solid = model.createIfcExtrudedAreaSolid(
        SweptArea=profile,
        ExtrudedDirection=model.createIfcDirection([0.0, 0.0, 1.0]),
        Depth=height
    )
    shape = model.createIfcShapeRepresentation(context, "Body", "SweptSolid", [solid])
    entity.Representation = model.createIfcProductDefinitionShape(None, None, [shape])
    run("spatial.assign_container", model, relating_structure=storey, products=[entity])
    return entity

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cluster_file = os.path.join(base_dir, "output", "pointnet_ready", "cluster_0.txt")
    label_file = os.path.join(base_dir, "output", "pointnet_ready", "cluster_0_pred.txt")

    points, labels = load_cluster_and_labels(cluster_file, label_file)

    model, context, storey = create_ifc_model()
    unique_labels = np.unique(labels)

    for idx, label in enumerate(unique_labels):
        mask = labels == label
        sub_points = points[mask]
        if len(sub_points) < 5:
            continue
        center, size = calculate_bbox(sub_points)
        base = [center[i] - size[i] / 2 for i in range(3)]
        size = [max(float(s), 0.1) for s in size]
        create_ifc_entity(model, context, storey, base, size, label, idx)

    out_path = os.path.join(base_dir, "output", "labeled_output.ifc")
    model.write(out_path)
    print(f"✅ IFC saved to {out_path}")

if __name__ == "__main__":
    main()
