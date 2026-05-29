# generator.py (unchanged except path handling)
import os
import sys
import json
import traceback
from pathlib import Path

EXTENSION_DIR = Path(__file__).parent
HUNYUAN_ROOT = Path(os.environ.get('HUNYUAN3D_ROOT', EXTENSION_DIR / "Hunyuan3D-2.1"))
MODELS_DIR = Path(os.environ.get('HUNYUAN_MODELS_DIR', EXTENSION_DIR / "models"))

# Load config if present
config_file = EXTENSION_DIR / "config.json"
if config_file.exists():
    with open(config_file) as f:
        cfg = json.load(f)
        HUNYUAN_ROOT = Path(cfg.get("hunyuan_root", HUNYUAN_ROOT))
        MODELS_DIR = Path(cfg.get("models_dir", MODELS_DIR))

sys.path.insert(0, str(HUNYUAN_ROOT))
sys.path.insert(0, str(HUNYUAN_ROOT / 'hy3dpaint'))

class HunyuanTextureGenerator:
    def __init__(self, models_dir=None):
        self.models_dir = Path(models_dir) if models_dir else MODELS_DIR
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
    def generate(self, image_path, output_path, variant_id, **kwargs):
        mesh_path = kwargs.get('mesh_path')
        if not mesh_path:
            return {"status": "error", "error": "mesh_path missing"}
        for p in [mesh_path, image_path]:
            if not os.path.exists(p):
                return {"status": "error", "error": f"File not found: {p}"}
        if not HUNYUAN_ROOT.exists():
            return {"status": "error", "error": f"Hunyuan3D not found at {HUNYUAN_ROOT}"}
        
        # Check for model weights
        if not any(self.models_dir.glob("*.safetensors")) and not any(self.models_dir.glob("*.bin")):
            return {"status": "error", "error": f"No model weights in {self.models_dir}. Please run setup or download manually."}
        
        try:
            from textureGenPipeline import Hunyuan3DPaintPipeline, Hunyuan3DPaintConfig
            params = {"max_num_view": 9, "resolution": 768} if variant_id == "paint-ultra" else {"max_num_view": 6, "resolution": 512}
            os.environ['HUNYUAN3D_WEIGHTS'] = str(self.models_dir)
            config = Hunyuan3DPaintConfig(**params)
            pipe = Hunyuan3DPaintPipeline(config)
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            final = pipe(mesh_path=mesh_path, image_path=image_path, output_mesh_path=output_path)
            return {"output_path": str(final), "status": "success"}
        except Exception as e:
            return {"status": "error", "error": str(e), "traceback": traceback.format_exc()}
