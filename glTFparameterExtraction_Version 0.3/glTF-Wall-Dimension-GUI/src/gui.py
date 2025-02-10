import os
import tkinter as tk
from tkinter import filedialog, messagebox
from main import process_multiple_gltf_files

def select_gltf_files():
    root = tk.Tk()
    root.withdraw()
    file_paths = filedialog.askopenfilenames(title="Select GLTF Files", filetypes=[("GLTF files", "*.gltf")])
    return file_paths

def main():
    try:
        gltf_files = select_gltf_files()
        if not gltf_files:
            messagebox.showinfo("No Files", "No GLTF files selected!")
            return

        output_file = filedialog.asksaveasfilename(
            title="Save IFC File As",
            defaultextension=".ifc",
            filetypes=[("IFC files", "*.ifc")]
        )
        if not output_file:
            messagebox.showinfo("No Output", "No output path selected!")
            return

        process_multiple_gltf_files(gltf_files, output_file)
        messagebox.showinfo("Success", f"IFC file created successfully at {output_file}")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

if __name__ == "__main__":
    main()
