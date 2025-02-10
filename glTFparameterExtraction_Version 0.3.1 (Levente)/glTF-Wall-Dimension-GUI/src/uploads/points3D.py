import json
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import math
from tkinter import filedialog
from tkinter import Tk

Tk().withdraw()  # Hide the root Tkinter window
gltf_files = filedialog.askopenfilenames(
    title="Select GLTF Files",
    filetypes=[("GLTF files", "*.gltf")]
)

if not gltf_files:
    print("No files selected.")
    exit()

def extract_bounding_boxes(gltf_files):
    """Extracts bounding box coordinates from a list of GLTF files."""
    bounding_boxes = []
    for gltf_file in gltf_files:
        with open(gltf_file, 'r') as f:
            gltf_data = json.load(f)
        extras = gltf_data.get("extras", {})
        bounding_box = extras.get("bounding_box", [])
        if bounding_box:
            bounding_boxes.append(bounding_box)
    return bounding_boxes

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

def plot_3d_points_with_orientation(bounding_boxes, orientations, centers):
    """Plots bounding box points in 3D with orientation vectors."""
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    for idx, (bounding_box, orientation, center) in enumerate(zip(bounding_boxes, orientations, centers)):
        x = [point[0] for point in bounding_box]
        y = [point[1] for point in bounding_box]
        z = [point[2] for point in bounding_box]

        ax.scatter(x, y, z, label=f"Wall {idx+1}")

        # Connect vertices to show the box structure
        for i in range(len(bounding_box)):
            for j in range(i + 1, len(bounding_box)):
                ax.plot(
                    [bounding_box[i][0], bounding_box[j][0]],
                    [bounding_box[i][1], bounding_box[j][1]],
                    [bounding_box[i][2], bounding_box[j][2]],
                    color="gray",
                    alpha=0.5,
                )

        # Plot the center point
        ax.scatter(center[0], center[1], center[2], color="red", marker="x", s=100)

        # Plot the orientation vector as an arrow
        ax.quiver(
            center[0], center[1], center[2],  # Start at the center
            orientation[0], orientation[1], orientation[2],  # Direction
            length=1.0, color="blue", normalize=True
        )

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.legend()
    plt.show()

# Main Logic
bounding_boxes = extract_bounding_boxes(gltf_files)
centers = [calculate_center_point(box) for box in bounding_boxes]
orientations = [calculate_wall_orientation(box) for box in bounding_boxes]
plot_3d_points_with_orientation(bounding_boxes, orientations, centers)
