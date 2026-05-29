@echo off
echo Installing Hunyuan3D-Paint Texture...
pip install -r requirements.txt
git clone https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1.git
cd Hunyuan3D-2.1
pip install torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cu124
pip install -e hy3dpaint/custom_rasterizer
mkdir hy3dpaint\ckpt
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth' -OutFile 'hy3dpaint\ckpt\RealESRGAN_x4plus.pth'"
echo Done!