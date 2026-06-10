import argparse
from pathlib import Path

import torch
import torch.nn as nn
from torchvision import models


def _resolve_checkpoint(path: Path) -> Path:
    if path.exists():
        return path
    # Try default name
    alt = Path("model.pth")
    if alt.exists():
        return alt
    # Search for any .pth in project root
    candidates = list(Path(".").glob("*.pth"))
    if candidates:
        return candidates[0]
    raise SystemExit(
        f"Checkpoint not found at {path.resolve()}. "
        "Download model.pth from Google Drive first."
    )


def main():
    parser = argparse.ArgumentParser(
        description="Export a trained .pth checkpoint to a self-contained ONNX file."
    )
    parser.add_argument(
        "--checkpoint",
        type=str,
        default="model.pth",
        help="Path to the PyTorch state_dict .pth file",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="model/malaria_resnet18.onnx",
        help="Output ONNX file path",
    )
    parser.add_argument(
        "--input-size",
        type=int,
        default=224,
        help="Model input size (width and height)",
    )
    args = parser.parse_args()

    ckpt_path = _resolve_checkpoint(Path(args.checkpoint))
    output_path = Path(args.output)

    device = torch.device("cpu")
    print(f"Loading checkpoint: {ckpt_path}")

    model = models.resnet18(weights=None)
    model.fc = nn.Linear(model.fc.in_features, 2)
    model.load_state_dict(torch.load(str(ckpt_path), map_location=device, weights_only=True))
    model.eval()

    dummy = torch.randn(1, 3, args.input_size, args.input_size)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    torch.onnx.export(
        model,
        dummy,
        str(output_path),
        input_names=["input"],
        output_names=["output"],
        opset_version=18,
        do_constant_folding=True,
        external_data=False,
    )

    if output_path.exists():
        file_size = output_path.stat().st_size
        print(f"ONNX exported successfully: {output_path} ({file_size / 1024 / 1024:.2f} MB)")
        print("The weights are embedded inside the file (no external .data file needed).")
    else:
        raise SystemExit("Export failed: output file not created")


if __name__ == "__main__":
    main()
