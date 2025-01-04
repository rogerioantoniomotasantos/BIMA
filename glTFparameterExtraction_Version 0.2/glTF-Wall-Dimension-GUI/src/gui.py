import os
import tkinter as tk
from tkinter import filedialog
from main import process_gltf_file

def select_gltf_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title="Select GLTF File", filetypes=[("GLTF files", "*.gltf")])
    return file_path

def main():

    print("Application started")

    file_path = select_gltf_file()
    if file_path:
        print(f"Selected GLTF file: {file_path}")
        project_root = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(project_root, 'output')
        process_gltf_file(file_path, output_dir)
    else:
        print("No file selected!")

if __name__ == "__main__":
    main()
