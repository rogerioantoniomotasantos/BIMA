import os
import tkinter as tk
from tkinter import filedialog
from main import process_multiple_gltf_files

def select_gltf_files():
    root = tk.Tk()
    root.withdraw()
    file_paths = filedialog.askopenfilenames(title="Select GLTF Files", filetypes=[("GLTF files", "*.gltf")])
    return file_paths

def main():
    print("Application started")

    gltf_files = select_gltf_files()
    if not gltf_files:
        print("No files selected!")
        return

    output_dir = filedialog.asksaveasfilename(title="Save IFC File As", defaultextension=".ifc", filetypes=[("IFC files", "*.ifc")])
    if not output_dir:
        print("No output path provided!")
        return

    print(f"Selected GLTF files: {gltf_files}")
    process_multiple_gltf_files(gltf_files, output_dir)
    print("Processing complete!")

if __name__ == "__main__":
    main()
