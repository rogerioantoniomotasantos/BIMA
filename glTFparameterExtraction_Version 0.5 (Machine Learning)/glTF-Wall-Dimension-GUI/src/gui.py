import os
import tkinter as tk
from tkinter import filedialog, messagebox
from main import process_multiple_gltf_files
from e57_to_ifc import convert_e57_to_ifc
import subprocess

def select_gltf_files():
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilenames(title="Select GLTF Files", filetypes=[("GLTF files", "*.gltf")])

def convert_gltf_gui():
    gltf_files = select_gltf_files()
    if not gltf_files:
        messagebox.showinfo("No Files", "No GLTF files selected!")
        return
    output_file = filedialog.asksaveasfilename(defaultextension=".ifc", filetypes=[("IFC files", "*.ifc")])
    if not output_file:
        return
    process_multiple_gltf_files(gltf_files, output_file)
    messagebox.showinfo("Success", f"IFC file created at {output_file}")

def convert_e57_gui():
    file_path = filedialog.askopenfilename(title="Select E57 File", filetypes=[("E57 files", "*.e57")])
    if not file_path:
        return
    convert_e57_to_ifc(file_path)
    messagebox.showinfo("Finished", "E57 processed: clusters saved for ML in output/ml_clusters")

def prepare_pointnet_gui():
    try:
        # Get current script directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(current_dir, "prepare_for_pointnet.py")
        subprocess.run(["python", script_path], check=True)
        messagebox.showinfo("Done", "PointNet++ files saved in output/pointnet_ready")
    except Exception as e:
        messagebox.showerror("Error", str(e))


def main():
    root = tk.Tk()
    root.title("LiDAR to IFC + ML Exporter")

    tk.Button(root, text="Convert GLTF to IFC", command=convert_gltf_gui).pack(pady=10)
    tk.Button(root, text="Convert E57 to Clusters", command=convert_e57_gui).pack(pady=10)
    tk.Button(root, text="Prepare PointNet++ Files", command=prepare_pointnet_gui).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
