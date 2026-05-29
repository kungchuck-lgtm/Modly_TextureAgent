# setup.py - Modly runs this when installing the extension
import subprocess
import sys
import os
from pathlib import Path
import urllib.request
import time

def setup():
    """Called by Modly to install all dependencies."""
    extension_dir = Path(__file__).parent
    hunyuan_dir = extension_dir / "Hunyuan3D-2.1"
    
    print("Installing Hunyuan3D-Paint Texture extension...")
    
    # Upgrade pip first
    print("[0/6] Upgrading pip...")
    subprocess.check_call([
        sys.executable, "-m", "pip", "install", "--upgrade", "pip"
    ])
    
    # 1. Install PyTorch first (required by other packages)
    print("[1/6] Installing PyTorch...")
    subprocess.check_call([
        sys.executable, "-m", "pip", "install",
        "torch==2.5.1", "torchvision==0.20.1", "torchaudio==2.5.1",
        "--index-url", "https://download.pytorch.org/whl/cu124",
        "--timeout", "300"
    ])
    
    # 2. Install core dependencies in batches with retries
    print("[2/6] Installing Python packages...")
    
    # Split packages into smaller batches to avoid timeouts
    batches = [
        # Core ML packages
        ["ninja==1.11.1.1", "pybind11==2.13.4", "transformers==4.46.0", 
         "diffusers==0.30.0", "accelerate==1.1.1", "huggingface-hub==0.30.2"],
        
        # Scientific computing
        ["numpy==1.24.4", "scipy==1.14.1", "einops==0.8.0", "pandas==2.2.2",
         "scikit-image==0.24.0", "imageio==2.36.0"],
        
        # Computer vision
        ["opencv-python==4.10.0.84", "rembg==2.0.65", "realesrgan==0.3.0",
         "basicsr==1.4.2", "safetensors==0.4.4"],
        
        # 3D processing
        ["trimesh==4.4.7", "pygltflib==1.16.3", "xatlas==0.0.9",
         "pymeshlab==2022.2.post3", "open3d==0.18.0"],
        
        # Web and utilities
        ["gradio==5.33.0", "fastapi==0.115.12", "uvicorn==0.34.3",
         "tqdm==4.66.5", "psutil==6.0.0"],
        
        # ML utilities (pytorch-lightning needs to be separate)
        ["pytorch-lightning==1.9.5", "torchmetrics==1.6.0", "torchdiffeq"],
        
        # Configuration and CUDA
        ["omegaconf==2.3.0", "pyyaml==6.0.2", "configargparse==1.7",
         "cupy-cuda12x==13.4.1", "onnxruntime==1.16.3", "pydantic==2.10.6"],
        
        # Others (timm and pythreejs are special)
        ["setuptools==69.5.1", "timm", "pythreejs"]
    ]
    
    for i, batch in enumerate(batches, 1):
        print(f"  Installing batch {i}/{len(batches)}...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "--timeout", "300",
                "--retries", "5"
            ] + batch)
        except subprocess.CalledProcessError as e:
            print(f"  Warning: Batch {i} failed, retrying with individual packages...")
            # Try installing each package individually
            for pkg in batch:
                try:
                    subprocess.check_call([
                        sys.executable, "-m", "pip", "install",
                        "--timeout", "300", "--retries", "3", pkg
                    ])
                except subprocess.CalledProcessError:
                    print(f"  Warning: Could not install {pkg}, continuing...")
    
    # 3. Clone Hunyuan3D-2.1 if not exists
    print("[3/6] Setting up Hunyuan3D-2.1...")
    if not hunyuan_dir.exists():
        print("  Cloning Hunyuan3D-2.1...")
        subprocess.check_call([
            "git", "clone",
            "--depth", "1",  # Shallow clone to save time
            "https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1.git",
            str(hunyuan_dir)
        ])
    else:
        print("  Hunyuan3D-2.1 already exists, skipping clone...")
    
    # 4. Build custom rasterizer if needed
    print("[4/6] Setting up custom rasterizer...")
    rasterizer_dir = hunyuan_dir / "hy3dpaint" / "custom_rasterizer"
    if rasterizer_dir.exists():
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-e",
                str(rasterizer_dir)
            ])
        except subprocess.CalledProcessError as e:
            print(f"  Warning: Rasterizer installation failed: {e}")
            print("  Texture generation may not work without this!")
    else:
        print("  Warning: Rasterizer directory not found!")
    
    # 5. Download RealESRGAN model
    print("[5/6] Downloading RealESRGAN model...")
    ckpt_dir = hunyuan_dir / "hy3dpaint" / "ckpt"
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    esrgan_path = ckpt_dir / "RealESRGAN_x4plus.pth"
    if not esrgan_path.exists():
        url = "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth"
        try:
            urllib.request.urlretrieve(url, esrgan_path)
            print("  RealESRGAN model downloaded successfully!")
        except Exception as e:
            print(f"  Warning: Could not download RealESRGAN model: {e}")
    else:
        print("  RealESRGAN model already exists...")
    
    # 6. Create a setup marker file
    print("[6/6] Finalizing setup...")
    marker_file = extension_dir / ".installed"
    marker_file.write_text("setup completed\n")
    
    # Set environment variable for generator.py
    os.environ['HUNYUAN3D_ROOT'] = str(hunyuan_dir)
    
    print("\n✅ Hunyuan3D-Paint Texture extension installed successfully!")
    print(f"   Models directory: {hunyuan_dir}")
    print("\n⚠️  Note: If some packages failed to install, check the warnings above.")
    print("   You may need to install them manually if they're required.")

if __name__ == "__main__":
    setup()
