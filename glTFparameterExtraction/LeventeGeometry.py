import pygltflib

# Load the GLTF file
gltf = pygltflib.GLTF2().load(r"C:\Users\motasan\Desktop\htw-berlin\glTFparameterExtraction\monitor-triangles_added_extras.gltf")


# Extract "extras" from the root level
extras = gltf.extras
print("Extras:", extras)


# Storing numerical values in variables
x_length = extras["x_length"]
y_length = extras["y_length"]
z_length = extras["z_length"]

print("x_length:", x_length)
print("y_length:", y_length)
print("z_length:", z_length)