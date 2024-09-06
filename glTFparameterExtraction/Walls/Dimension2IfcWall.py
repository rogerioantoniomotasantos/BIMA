import ifcopenshell
from ifcopenshell.api import run
from WallDimensions import *

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