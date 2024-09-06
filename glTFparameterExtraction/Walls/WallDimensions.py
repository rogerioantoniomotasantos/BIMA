import pandas as pd

# Assuming 'distances_df' is the DataFrame with calculated distances
distances_df = pd.read_excel(r"C:\Users\motasan\Desktop\htw-berlin\glTFparameterExtraction\Walls\distances_data.xlsx")

# Sort distances to help categorize them
sorted_distances = distances_df.sort_values(by='Distance')

# Extract potential thickness (smallest distance), height (middle distances), and length (largest distances)
thickness = sorted_distances.iloc[0]['Distance']
length = sorted_distances.iloc[-1]['Distance']
height = sorted_distances.iloc[len(sorted_distances) // 2]['Distance']

print(f"Potential Wall Dimensions:\nThickness: {thickness}\nHeight: {height}\nLength: {length}")
