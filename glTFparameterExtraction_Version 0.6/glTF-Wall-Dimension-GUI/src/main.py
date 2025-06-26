import sys
from process_e57 import process_segmented_e57_to_ifc

def main():
    if len(sys.argv) != 3:
        print("Usage: python main.py <input.e57> <output.ifc>")
        sys.exit(1)

    e57_path = sys.argv[1]
    output_ifc_path = sys.argv[2]
    process_segmented_e57_to_ifc(e57_path, output_ifc_path)

if __name__ == "__main__":
    main()
