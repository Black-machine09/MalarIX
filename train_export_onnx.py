import os
import random
from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass(frozen=True)
class TrainConfig:
    data_dir: Path
    output_onnx_path: Path
    input_size: int = 224
    val_split: float = 0.2
    seed: int = 42
    epochs: int = 3
    batch_size: int = 16
    lr: float = 1e-4
    num_workers: int = 0


def _collect_image_paths(data_dir: Path) -> list[tuple[Path, int]]:
    # Expects:
    #   data_dir/Parasitized/*.png -> label 1
    #   data_dir/Uninfected/*.png -> label 0
    class_to_label = {"Uninfected": 0, "Parasitized": 1}
    items: list[tuple[Path, int]] = []
    for class_name, label in class_to_label.items():
        class_dir = data_dir / class_name
        if not class_dir.exists():
            continue
        for p in class_dir.rglob("*.png"):
            items.append((p, label))
    return items


def main():
    cfg = TrainConfig(
        data_dir=Path("cell_images"),
        output_onnx_path=Path("model/malaria_resnet18.onnx"),
        val_split=0.2,
        seed=42,
        epochs=3,
        batch_size=16,
        lr=1e-4,
    )

    # Import torch lazily so this script fails with a helpful message if deps are missing.
    try:
        import torch
        import torch.nn as nn
        import torch.optim as optim
        from torch.utils.data import Dataset, DataLoader
        from torchvision import models, transforms
    except Exception as e:
        raise SystemExit(
            "Training requires PyTorch + torchvision. Install with:\n"
            "  pip install torch torchvision\n"
            "Then rerun this script.\n\nOriginal error: "
            + str(e)
        )

    random.seed(cfg.seed)
    np.random.seed(cfg.seed)
    torch.manual_seed(cfg.seed)

    # Smoke-test export: generate an ONNX so the API can load the model.
    # This avoids training and does not require cell_images to be present.

    device = torch.device("cpu")

    # ResNet18 binary classifier head (untrained; for endpoint validation only).
    model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    model.fc = nn.Linear(model.fc.in_features, 2)
    model.to(device)

    cfg.output_onnx_path.parent.mkdir(parents=True, exist_ok=True)

    model.eval()


    # Export expects output compatible with ml/inference.py: it supports [1,2] softmax/logits style.
    dummy = torch.randn(1, 3, cfg.input_size, cfg.input_size, device=device)

    # Dynamic axes not required; keep static for simplicity.
    torch.onnx.export(
        model,
        dummy,
        str(cfg.output_onnx_path),
        input_names=["input"],
        output_names=["output"],
        opset_version=17,
        do_constant_folding=True,
    )

    if not cfg.output_onnx_path.exists():
        raise SystemExit("ONNX export failed: output file not created")

    print(f"Exported: {cfg.output_onnx_path}")


if __name__ == "__main__":
    main()

