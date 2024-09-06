import json

# Load the GLTF file as JSON
with open(r"C:\Users\motasan\Desktop\htw-berlin\glTFparameterExtraction\monitor-triangles_added_extras.gltf", "r") as f:
    gltf_json = json.load(f)

# Extract "extras" from the root level
extras = gltf_json.get("extras", {})
print("Extras:", extras)

# Storing numerical values in variables
x_length = extras["x_length"]
y_length = extras["y_length"]
z_length = extras["z_length"]

print("x_length:", x_length)
print("y_length:", y_length)
print("z_length:", z_length)
