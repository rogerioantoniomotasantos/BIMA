import os
import tkinter as tk
from tkinter import filedialog, messagebox
from process_e57 import process_segmented_e57_to_ifc

def select_e57_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title="Select E57 File", filetypes=[("E57 files", "*.e57")])
    return file_path

print("🚀 GUI is launching...")


def main():
    try:
        e57_file = select_e57_file()
        if not e57_file:
            messagebox.showinfo("No File", "No E57 file selected!")
            return

        output_file = filedialog.asksaveasfilename(
            title="Save IFC File As",
            defaultextension=".ifc",
            filetypes=[("IFC files", "*.ifc")]
        )
        if not output_file:
            messagebox.showinfo("No Output", "No output path selected!")
            return

        process_segmented_e57_to_ifc(e57_file, output_file)
        messagebox.showinfo("Success", f"IFC file created successfully at {output_file}")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

if __name__ == "__main__":
    main()
