import os
import json
import traceback
from pathlib import Path

class HunyuanTextureGenerator:
    """Lazy-loading generator – no heavy work until generate() is called."""
    
    def __init__(self, models_dir=None):
        # Store the extension directory, but do nothing else
        self.extension_dir = Path(__file__).parent
        self.provided_models_dir = models_dir

    def generate(self, image_path, output_path, variant_id, **kwargs):
        mesh_path = kwargs.get('mesh_path')
        if not mesh_path:
            return {"status": "error", "error": "mesh_path missing"}

        try:
            # ---------- 1. Load configuration (only once per generation) ----------
            config_file = self.extension_dir / "config.json"
            if config_file.exists():
                with open(config_file) as f:
                    cfg = json.load(f)
                    hunyuan_root = Path(cfg.get("hunyuan_root", self.extension_dir / "Hunyuan3D-2.1"))
                    models_dir = Path(cfg.get("models_dir", self.extension_dir / "models"))
            else:
                hunyuan_root = self.extension_dir / "Hunyuan3D-2.1"
                models_dir = self.extension_dir / "models"

            # Override if models_dir was passed to constructor
            if self.provided_models_dir:
                models_dir = Path(self.provided_models_dir)

            # Ensure models directory exists
            models_dir.mkdir(parents=True, exist_ok=True)

            # ---------- 2. Validate inputs ----------
            for p in [mesh_path, image_path]:
                if not os.path.exists(p):
                    return {"status": "error", "error": f"File not found: {p}"}

            if not hunyuan_root.exists():
                return {"status": "error", "error": f"Hunyuan3D repository not found at {hunyuan_root}. Please run setup."}

            # Check for at least one model weight file
            weight_files = list(models_dir.glob("*.safetensors")) + list(models_dir.glob("*.bin")) + list(models_dir.glob("*.pth"))
            if not weight_files:
                return {"status": "error", "error": f"No model weights found in {models_dir}. Please download them first."}

            # ---------- 3. Import heavy modules (only now) ----------
            import sys
            sys.path.insert(0, str(hunyuan_root))
            sys.path.insert(0, str(hunyuan_root / 'hy3dpaint'))
            from textureGenPipeline import Hunyuan3DPaintPipeline, Hunyuan3DPaintConfig

            # ---------- 4. Configure variant ----------
            if variant_id == "paint-ultra":
                params = {"max_num_view": 9, "resolution": 768}
            else:
                params = {"max_num_view": 6, "resolution": 512}

            # ---------- 5. Run texture generation ----------
            os.environ['HUNYUAN3D_WEIGHTS'] = str(models_dir)
            config = Hunyuan3DPaintConfig(**params)
            pipe = Hunyuan3DPaintPipeline(config)
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            final_path = pipe(
                mesh_path=mesh_path,
                image_path=image_path,
                output_mesh_path=output_path
            )

            return {
                "output_path": str(final_path),
                "status": "success",
                "message": f"Textured mesh saved to {final_path}"
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc()
            }
