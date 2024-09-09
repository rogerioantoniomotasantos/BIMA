import os
import tkinter as tk
from tkinter import filedialog
from main import process_gltf_file  # Import the main processing function

def select_gltf_file():
    # Create a file dialog to select a GLTF file
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename(
        title="Select GLTF File", 
        filetypes=[("GLTF files", "*.gltf")])
    return file_path

def main():
    # Select the GLTF file
    file_path = select_gltf_file()

    if file_path:
        print(f"Selected GLTF file: {file_path}")

        # Process the selected GLTF file using the existing code
        project_root = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(project_root, '..', 'output')

        process_gltf_file(file_path, output_dir)
    else:
        print("No file selected!")

if __name__ == "__main__":
    main()
