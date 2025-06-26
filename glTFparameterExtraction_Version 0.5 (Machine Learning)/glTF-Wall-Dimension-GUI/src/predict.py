
import numpy as np
import torch
import torch.nn as nn
import os

# Dummy model for testing — replace later with a real PointNet++
class DummyPointNet(nn.Module):
    def __init__(self, num_classes=10):
        super().__init__()
        self.mlp = nn.Sequential(
            nn.Linear(3, 64),
            nn.ReLU(),
            nn.Linear(64, 128),
            nn.ReLU(),
            nn.Linear(128, num_classes)
        )

    def forward(self, x):
        return self.mlp(x)

def load_point_cloud_txt(file_path):
    points = np.loadtxt(file_path)
    if points.shape[0] == 0:
        raise ValueError("Empty point cloud")
    if points.shape[1] != 3:
        raise ValueError("Expected Nx3 input format")
    return points

def run_inference(model, point_cloud):
    model.eval()
    with torch.no_grad():
        input_tensor = torch.tensor(point_cloud, dtype=torch.float32)
        logits = model(input_tensor)
        predictions = torch.argmax(logits, dim=1)
        return predictions.numpy()

def main():
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(base_dir, "output", "pointnet_ready", "cluster_0.txt")

    output_file = os.path.join(base_dir, "output", "pointnet_ready", "cluster_0_pred.txt")


    if not os.path.exists(input_file):
        print(f"❌ File not found: {input_file}")
        return

    print("📦 Loading point cloud...")
    points = load_point_cloud_txt(input_file)

    print("🧠 Loading dummy model...")
    model = DummyPointNet(num_classes=5)

    print("🔮 Running inference...")
    predictions = run_inference(model, points)

    print("💾 Saving predictions...")
    np.savetxt(output_file, predictions, fmt='%d')
    print(f"✅ Predictions saved to: {output_file}")

if __name__ == "__main__":
    main()
