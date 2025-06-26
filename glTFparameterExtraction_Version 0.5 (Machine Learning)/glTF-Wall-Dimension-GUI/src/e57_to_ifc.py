
from pye57 import E57
import open3d as o3d
import numpy as np
import os

def export_clusters_for_ml(pcd, eps=0.1, min_points=10):
    labels = np.array(pcd.cluster_dbscan(eps=eps, min_points=min_points, print_progress=True))
    max_label = labels.max()
    print(f"🟢 Found {max_label + 1} clusters")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(base_dir, "output", "ml_clusters")
    os.makedirs(out_dir, exist_ok=True)

    for i in range(max_label + 1):
        indices = np.where(labels == i)[0]
        cluster = pcd.select_by_index(indices)
        filename = os.path.join(out_dir, f"cluster_{i}.ply")
        o3d.io.write_point_cloud(filename, cluster)
        print(f"📦 Saved cluster_{i}.ply with {len(cluster.points)} points")

def convert_e57_to_ifc(file_path, output_ifc_path=None):
    e57 = E57(file_path)
    scan = e57.read_scan(0, ignore_missing_fields=True)
    points = np.vstack((scan["cartesianX"], scan["cartesianY"], scan["cartesianZ"])).T
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    pcd = pcd.voxel_down_sample(voxel_size=0.05)
    export_clusters_for_ml(pcd)
    print("✅ Clusters ready for ML.")
