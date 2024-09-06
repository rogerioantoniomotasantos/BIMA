import ast
import pandas as pd
from itertools import combinations
from math import sqrt

# Load the Excel file
df = pd.read_excel(r"C:\Users\motasan\Desktop\htw-berlin\glTFparameterExtraction\Walls\extras_data.xlsx")  # Update with your actual file path

# Extract the bounding box string from the "Value" column where the "Property" is "Bounding Box"
bounding_box_string = df.loc[df['Property'] == 'Bounding Box', 'Value'].values[0]

# Convert the bounding box string into a list of points
points = ast.literal_eval(bounding_box_string)

# Function to calculate Euclidean distance between two points
def euclidean_distance(point1, point2):
    return sqrt(sum((a - b) ** 2 for a, b in zip(point1, point2)))

# Calculate distances between all pairs of points
distances = {}
for (i, p1), (j, p2) in combinations(enumerate(points), 2):
    dist = euclidean_distance(p1, p2)
    distances[f"Point {i+1} to Point {j+1}"] = dist

# Print the distances
for points_pair, distance in distances.items():
    print(f"Distance from {points_pair}: {distance}")

# Optionally, save the distances to a new Excel file
distances_df = pd.DataFrame(list(distances.items()), columns=['Points Pair', 'Distance'])
distances_df.to_excel(r"C:\Users\motasan\Desktop\htw-berlin\glTFparameterExtraction\Walls\distances_data.xlsx", index=False)
