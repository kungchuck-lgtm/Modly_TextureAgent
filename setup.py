# setup.py - Modly runs this when installing the extension
import subprocess
import sys
import os
from pathlib import Path
import urllib.request
import time
import json
from huggingface_hub import snapshot_download  # we'll install this first

def setup():
    """Called by Modly to install all dependencies and download models."""
    extension_dir = Path(__file__).parent
    hunyuan_dir = extension_dir / "Hunyuan3D-2.1"
    models_dir = extension_dir / "models"  # where model weights will be stored
    
    print("Installing Hunyuan3D-Paint Texture extension...")
    
    # Upgrade pip first
    print("[0/7] Upgrading pip...")
    subprocess.check_call([
        sys.executable, "-m", "pip", "install", "--upgrade", "pip"
    ])
    
    # Install huggingface_hub early so we can download models
    print("[1/7] Installing huggingface_hub...")
    subprocess.check_call([
        sys.executable, "-m", "pip", "install", "huggingface-hub>=0.30.2"
    ])
    
    # 2. Install PyTorch first (required by other packages)
    print("[2/7] Installing PyTorch...")
    subprocess.check_call([
        sys.executable, "-m", "pip", "install",
        "torch==2.5.1", "torchvision==0.20.1", "torchaudio==2.5.1",
        "--index-url", "https://download.pytorch.org/whl/cu124",
        "--timeout", "300"
    ])
    
    # 3. Install core dependencies in batches
    print("[3/7] Installing Python packages...")
    
    batches = [
        ["ninja==1.11.1.1", "pybind11==2.13.4", "transformers==4.46.0", 
         "diffusers==0.30.0", "accelerate==1.1.1", "safetensors==0.4.4"],
        ["numpy==1.24.4", "scipy==1.14.1", "einops==0.8.0", "pandas==2.2.2",
         "scikit-image==0.24.0", "imageio==2.36.0"],
        ["opencv-python==4.10.0.84", "rembg==2.0.65", "realesrgan==0.3.0",
         "basicsr==1.4.2", "tqdm==4.66.5", "psutil==6.0.0"],
        ["trimesh==4.4.7", "pygltflib==1.16.3", "xatlas==0.0.9",
         "pymeshlab==2022.2.post3", "open3d==0.18.0"],
        ["gradio==5.33.0", "fastapi==0.115.12", "uvicorn==0.34.3"],
        ["pytorch-lightning==1.9.5", "torchmetrics==1.6.0", "torchdiffeq"],
        ["omegaconf==2.3.0", "pyyaml==6.0.2", "configargparse==1.7",
         "cupy-cuda12x==13.4.1", "onnxruntime==1.16.3", "pydantic==2.10.6"],
        ["setuptools==69.5.1", "timm", "pythreejs"]
    ]
    
    for i, batch in enumerate(batches, 1):
        print(f"  Installing batch {i}/{len(batches)}...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "--timeout", "300",
                "--retries", "5"
            ] + batch)
        except subprocess.CalledProcessError:
            print(f"  Warning: Batch {i} failed, retrying individually...")
            for pkg in batch:
                try:
                    subprocess.check_call([
                        sys.executable, "-m", "pip", "install",
                        "--timeout", "300", "--retries", "3", pkg
                    ])
                except subprocess.CalledProcessError:
                    print(f"    Warning: Could not install {pkg}")
    
    # 4. Clone Hunyuan3D-2.1 if not exists
    print("[4/7] Setting up Hunyuan3D-2.1 repository...")
    if not hunyuan_dir.exists():
        print("  Cloning Hunyuan3D-2.1...")
        subprocess.check_call([
            "git", "clone",
            "--depth", "1",
            "https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1.git",
            str(hunyuan_dir)
        ])
    else:
        print("  Hunyuan3D-2.1 already exists, skipping clone...")
    
    # 5. Build custom rasterizer
    print("[5/7] Building custom rasterizer...")
    rasterizer_dir = hunyuan_dir / "hy3dpaint" / "custom_rasterizer"
    if rasterizer_dir.exists():
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-e",
                str(rasterizer_dir)
            ])
        except subprocess.CalledProcessError as e:
            print(f"  Warning: Rasterizer installation failed: {e}")
    else:
        print("  Warning: Rasterizer directory not found!")
    
    # 6. Download Hunyuan3D-Paint model weights (CRITICAL STEP)
    print("[6/7] Downloading Hunyuan3D-Paint model weights...")
    models_dir.mkdir(parents=True, exist_ok=True)
    
    # The model is hosted on Hugging Face - adjust the repo ID as needed
    # Official Hunyuan3D-2.1 models: https://huggingface.co/Tencent-Hunyuan/Hunyuan3D-2
    # For the Paint texture model, we need the specific checkpoint
    model_repo_id = "Tencent-Hunyuan/Hunyuan3D-2"  # or the exact paint model repo
    paint_subfolder = "hy3dpaint"  # subfolder inside the repo containing paint weights
    
    print(f"  Downloading model from Hugging Face: {model_repo_id}")
    print("  This may take a while (several GB)...")
    
    try:
        from huggingface_hub import snapshot_download
        snapshot_download(
            repo_id=model_repo_id,
            local_dir=str(models_dir),
            allow_patterns=["*.bin", "*.safetensors", "*.pth", "*.ckpt", "config.json"],
            resume_download=True,
            ignore_patterns=["*.md", "*.txt"]
        )
        print("  Model weights downloaded successfully!")
    except Exception as e:
        print(f"  Warning: Failed to download model from HF: {e}")
        print("  You may need to download manually from https://huggingface.co/Tencent-Hunyuan/Hunyuan3D-2")
        print("  and place the contents in:", models_dir)
    
    # Also download RealESRGAN upscaler if not already present
    print("  Downloading RealESRGAN upscaler...")
    esrgan_dir = models_dir / "realesrgan"
    esrgan_dir.mkdir(parents=True, exist_ok=True)
    esrgan_path = esrgan_dir / "RealESRGAN_x4plus.pth"
    if not esrgan_path.exists():
        url = "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth"
        try:
            urllib.request.urlretrieve(url, esrgan_path)
            print("    RealESRGAN downloaded.")
        except Exception as e:
            print(f"    Warning: Could not download RealESRGAN: {e}")
    
    # 7. Create setup marker and environment config
    print("[7/7] Finalizing setup...")
    marker_file = extension_dir / ".installed"
    marker_file.write_text("setup completed\n")
    
    # Write a config file so generator knows where models are
    config_file = extension_dir / "config.json"
    with open(config_file, "w") as f:
        json.dump({
            "hunyuan_root": str(hunyuan_dir),
            "models_dir": str(models_dir),
            "variant_default": "paint-quality"
        }, f, indent=2)
    
    # Set environment variable for generator.py
    os.environ['HUNYUAN3D_ROOT'] = str(hunyuan_dir)
    os.environ['HUNYUAN_MODELS_DIR'] = str(models_dir)
    
    print("\n✅ Hunyuan3D-Paint Texture extension installed successfully!")
    print(f"   Repository: {hunyuan_dir}")
    print(f"   Model weights: {models_dir}")
    print("\n⚠️  If model download failed, you must manually download the weights.")
    print("   Place them in the 'models' folder inside the extension directory.")

if __name__ == "__main__":
    setup()
