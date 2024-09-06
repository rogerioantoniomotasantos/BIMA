import json
import pandas as pd

def extract_extras_from_gltf(file_path):
    # Load the GLTF file
    with open(file_path, 'r') as f:
        gltf_data = json.load(f)
    
    # Extract the "extras" field
    extras = gltf_data.get('extras', None)
    return extras

def save_extras_to_excel(extras, output_path):
    if extras:
        # Organize data into a dictionary of lists for DataFrame
        data = {
            'Property': ['Bounding Box', 'Object ID', 'Object Name', 'Object Type'],
            'Value': [
                str(extras.get('bounding_box', [])),
                extras.get('object_id', ''),
                extras.get('object_name', ''),
                extras.get('object_type', '')
            ]
        }
        
        # Create a DataFrame
        df = pd.DataFrame(data)
        
        # Save DataFrame to Excel file
        df.to_excel(output_path, index=False)
        print(f"Extras data saved to {output_path}")
    else:
        print("No extras field found to save.")

# Example usage
file_path = r"C:\Users\motasan\Desktop\htw-berlin\glTFparameterExtraction\Walls\Wall_1 - E101.gltf"  # Replace with your actual GLTF file path
output_path = r"C:\Users\motasan\Desktop\htw-berlin\glTFparameterExtraction\Walls\extras_data.xlsx"  # Replace with your desired Excel file path

extras = extract_extras_from_gltf(file_path)
save_extras_to_excel(extras, output_path)
