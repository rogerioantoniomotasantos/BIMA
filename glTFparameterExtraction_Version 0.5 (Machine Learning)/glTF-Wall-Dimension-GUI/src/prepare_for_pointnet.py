
import open3d as o3d
import numpy as np
import os

def normalize_and_export_txt(ply_path, output_path, target_points=1024):
    pcd = o3d.io.read_point_cloud(ply_path)
    points = np.asarray(pcd.points)
    if len(points) == 0:
        print(f"❌ Empty point cloud in {ply_path}")
        return
    center = points.mean(axis=0)
    points -= center
    scale = np.max(np.linalg.norm(points, axis=1))
    points /= scale
    if len(points) > target_points:
        idx = np.random.choice(len(points), target_points, replace=False)
        points = points[idx]
    elif len(points) < target_points:
        pad = target_points - len(points)
        points = np.vstack([points, np.zeros((pad, 3))])
    np.savetxt(output_path, points, fmt="%.6f")
    print(f"✅ Saved {output_path}")

def batch_convert(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    for file in os.listdir(input_folder):
        if file.endswith(".ply"):
            ply_path = os.path.join(input_folder, file)
            txt_path = os.path.join(output_folder, file.replace(".ply", ".txt"))
            normalize_and_export_txt(ply_path, txt_path)

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_folder = os.path.join(base_dir, "output", "ml_clusters")
    output_folder = os.path.join(base_dir, "output", "pointnet_ready")
    batch_convert(input_folder, output_folder)
