# setup.py - Modly runs this when installing the extension
import subprocess
import sys
import os
from pathlib import Path
import urllib.request


def setup():
    """Called by Modly to install all dependencies."""
    extension_dir = Path(__file__).parent
    hunyuan_dir = extension_dir / "Hunyuan3D-2.1"
    
    print("Installing Hunyuan3D-Paint Texture extension...")
    
    # 1. Install PyTorch first (required by other packages)
    print("[1/5] Installing PyTorch...")
    subprocess.check_call([
        sys.executable, "-m", "pip", "install",
        "torch==2.5.1", "torchvision==0.20.1", "torchaudio==2.5.1",
        "--index-url", "https://download.pytorch.org/whl/cu124"
    ])
    
    # 2. Install core dependencies
    print("[2/5] Installing Python packages...")
    packages = [
        "ninja==1.11.1.1", "pybind11==2.13.4",
        "transformers==4.46.0", "diffusers==0.30.0", "accelerate==1.1.1",
        "pytorch-lightning==1.9.5", "huggingface-hub==0.30.2", "safetensors==0.4.4",
        "numpy==1.24.4", "scipy==1.14.1", "einops==0.8.0", "pandas==2.2.2",
        "opencv-python==4.10.0.84", "imageio==2.36.0", "scikit-image==0.24.0",
        "rembg==2.0.65", "realesrgan==0.3.0", "tb_nightly==2.18.0a20240726",
        "basicsr==1.4.2", "trimesh==4.4.7", "pymeshlab==2022.2.post3",
        "pygltflib==1.16.3", "xatlas==0.0.9", "open3d==0.18.0",
        "omegaconf==2.3.0", "pyyaml==6.0.2", "configargparse==1.7",
        "gradio==5.33.0", "fastapi==0.115.12", "uvicorn==0.34.3",
        "tqdm==4.66.5", "psutil==6.0.0", "cupy-cuda12x==13.4.1",
        "onnxruntime==1.16.3", "torchmetrics==1.6.0", "pydantic==2.10.6",
        "timm", "pythreejs", "torchdiffeq", "setuptools==69.5.1"
    ]
    subprocess.check_call([sys.executable, "-m", "pip", "install"] + packages)
    
    # 3. Clone Hunyuan3D-2.1
    print("[3/5] Cloning Hunyuan3D-2.1...")
    if not hunyuan_dir.exists():
        subprocess.check_call([
            "git", "clone",
            "https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1.git",
            str(hunyuan_dir)
        ])
    
    # 4. Build custom rasterizer
    print("[4/5] Building custom rasterizer...")
    subprocess.check_call([
        sys.executable, "-m", "pip", "install", "-e",
        str(hunyuan_dir / "hy3dpaint" / "custom_rasterizer")
    ])
    
    # 5. Download RealESRGAN model
    print("[5/5] Downloading RealESRGAN model...")
    ckpt_dir = hunyuan_dir / "hy3dpaint" / "ckpt"
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    esrgan_path = ckpt_dir / "RealESRGAN_x4plus.pth"
    if not esrgan_path.exists():
        url = "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth"
        urllib.request.urlretrieve(url, esrgan_path)
    
    # Set environment variable for generator.py
    os.environ['HUNYUAN3D_ROOT'] = str(hunyuan_dir)
    
    print("✅ Hunyuan3D-Paint Texture extension installed successfully!")
    print(f"   Models directory: {hunyuan_dir}")


if __name__ == "__main__":
    setup()