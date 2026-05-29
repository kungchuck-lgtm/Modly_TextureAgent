# install.py - Modly runs this when installing the extension
import subprocess
import sys
import os
from pathlib import Path

def install():
    """Called by Modly to set up the extension."""
    extension_dir = Path(__file__).parent
    
    # 1. Install pip dependencies
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", 
                          str(extension_dir / "requirements.txt")])
    
    # 2. Clone Hunyuan3D-2.1 if not present
    hunyuan_dir = extension_dir / "Hunyuan3D-2.1"
    if not hunyuan_dir.exists():
        subprocess.check_call(["git", "clone", 
                              "https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1.git",
                              str(hunyuan_dir)])
    
    # 3. Install PyTorch
    subprocess.check_call([sys.executable, "-m", "pip", "install",
                          "torch==2.5.1", "torchvision==0.20.1", "torchaudio==2.5.1",
                          "--index-url", "https://download.pytorch.org/whl/cu124"])
    
    # 4. Build custom rasterizer
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-e",
                          str(hunyuan_dir / "hy3dpaint" / "custom_rasterizer")])
    
    # 5. Download RealESRGAN model
    ckpt_dir = hunyuan_dir / "hy3dpaint" / "ckpt"
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    esrgan_path = ckpt_dir / "RealESRGAN_x4plus.pth"
    if not esrgan_path.exists():
        import urllib.request
        url = "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth"
        urllib.request.urlretrieve(url, esrgan_path)
    
    print("Hunyuan3D-Paint Texture extension installed successfully!")

if __name__ == "__main__":
    install()