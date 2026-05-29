# setup.py - Modly runs this when installing the extension
import subprocess
import sys
import os
from pathlib import Path
import urllib.request
import json

def run_pip(*args, timeout=300):
    """Run pip install with retries and proper error handling."""
    cmd = [sys.executable, "-m", "pip", "install", "--timeout", str(timeout), "--retries", "5"] + list(args)
    try:
        subprocess.check_call(cmd)
        return True
    except subprocess.CalledProcessError as e:
        print(f"  Error: pip install failed with code {e.returncode}")
        return False

def setup():
    extension_dir = Path(__file__).parent
    hunyuan_dir = extension_dir / "Hunyuan3D-2.1"
    models_dir = extension_dir / "models"
    
    print("Installing Hunyuan3D-Paint Texture extension...")
    
    # Upgrade pip first
    print("[0/7] Upgrading pip...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    
    # 1. Install torch FIRST and verify
    print("[1/7] Installing PyTorch (this is critical)...")
    success = run_pip(
        "torch==2.5.1", "torchvision==0.20.1", "torchaudio==2.5.1",
        "--index-url", "https://download.pytorch.org/whl/cu124"
    )
    if not success:
        print("  ERROR: PyTorch installation failed. Extension cannot work without it.")
        sys.exit(1)
    
    # Verify torch is importable
    try:
        subprocess.check_call([sys.executable, "-c", "import torch; print(f'PyTorch {torch.__version__} installed')"])
    except:
        print("  ERROR: PyTorch installed but not importable. Check your Python environment.")
        sys.exit(1)
    
    # 2. Install huggingface_hub for model downloads
    print("[2/7] Installing huggingface_hub...")
    run_pip("huggingface-hub>=0.30.2")
    
    # 3. Install other core dependencies in batches
    print("[3/7] Installing Python packages...")
    batches = [
        ["ninja", "pybind11"],
        ["transformers==4.46.0", "diffusers==0.30.0", "accelerate==1.1.1", "safetensors==0.4.4"],
        ["numpy==1.24.4", "scipy==1.14.1", "einops==0.8.0", "pandas==2.2.2"],
        ["opencv-python==4.10.0.84", "imageio==2.36.0", "scikit-image==0.24.0"],
        ["rembg==2.0.65", "realesrgan==0.3.0", "basicsr==1.4.2"],
        ["trimesh==4.4.7", "pygltflib==1.16.3", "xatlas==0.0.9", "pymeshlab==2022.2.post3", "open3d==0.18.0"],
        ["gradio==5.33.0", "fastapi==0.115.12", "uvicorn==0.34.3"],
        ["pytorch-lightning==1.9.5", "torchmetrics==1.6.0", "torchdiffeq"],
        ["omegaconf==2.3.0", "pyyaml==6.0.2", "configargparse==1.7"],
        ["cupy-cuda12x==13.4.1", "onnxruntime==1.16.3", "pydantic==2.10.6"],
        ["setuptools==69.5.1", "timm", "pythreejs", "tqdm", "psutil"]
    ]
    for batch in batches:
        run_pip(*batch)
    
    # 4. Clone Hunyuan3D-2.1
    print("[4/7] Setting up Hunyuan3D-2.1 repository...")
    if not hunyuan_dir.exists():
        subprocess.check_call(["git", "clone", "--depth", "1",
                               "https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1.git",
                               str(hunyuan_dir)])
    else:
        print("  Already exists, skipping clone...")
    
    # 5. Build custom rasterizer (only after torch is confirmed!)
    print("[5/7] Building custom rasterizer...")
    rasterizer_dir = hunyuan_dir / "hy3dpaint" / "custom_rasterizer"
    if rasterizer_dir.exists():
        # Because torch is now available, this should work
        run_pip("-e", str(rasterizer_dir))
    else:
        print("  WARNING: Rasterizer directory not found. Installation incomplete.")
    
    # 6. Download model weights (optional but recommended)
    print("[6/7] Downloading model weights...")
    models_dir.mkdir(parents=True, exist_ok=True)
    try:
        from huggingface_hub import snapshot_download
        snapshot_download(
            repo_id="Tencent-Hunyuan/Hunyuan3D-2",
            local_dir=str(models_dir),
            allow_patterns=["*.bin", "*.safetensors", "*.pth", "*.ckpt", "config.json"],
            resume_download=True,
            ignore_patterns=["*.md", "*.txt"]
        )
        print("  Model weights downloaded.")
    except Exception as e:
        print(f"  WARNING: Could not download models: {e}")
        print("  You can download manually from https://huggingface.co/Tencent-Hunyuan/Hunyuan3D-2")
        print(f"  and place them in {models_dir}")
    
    # Download RealESRGAN model
    esrgan_path = models_dir / "RealESRGAN_x4plus.pth"
    if not esrgan_path.exists():
        url = "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth"
        try:
            urllib.request.urlretrieve(url, esrgan_path)
        except:
            pass
    
    # 7. Write config file
    print("[7/7] Finalizing setup...")
    config_file = extension_dir / "config.json"
    with open(config_file, "w") as f:
        json.dump({
            "hunyuan_root": str(hunyuan_dir),
            "models_dir": str(models_dir)
        }, f)
    
    # Environment variables for runtime
    os.environ['HUNYUAN3D_ROOT'] = str(hunyuan_dir)
    os.environ['HUNYUAN_MODELS_DIR'] = str(models_dir)
    
    # Marker file
    (extension_dir / ".installed").write_text("setup completed\n")
    
    # Use plain text to avoid Unicode errors on Windows
    print("\n[SUCCESS] Hunyuan3D-Paint Texture extension installed successfully!")
    print(f"  Repository: {hunyuan_dir}")
    print(f"  Model weights: {models_dir}")
    print("\nNOTE: If model download failed, you must manually place the weights in the models folder.")

if __name__ == "__main__":
    setup()
