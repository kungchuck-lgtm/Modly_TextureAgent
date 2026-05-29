import os
import sys
import json
import traceback
from pathlib import Path

# Debug: print when module loads
print("generator.py loaded", file=sys.stderr)

class HunyuanTextureGenerator:
    """
    Universal constructor accepts any number of arguments.
    """
    def __init__(self, *args, **kwargs):
        # Log to help debug
        print(f"HunyuanTextureGenerator.__init__ called with args={args}, kwargs={kwargs}", file=sys.stderr)
        
        self.extension_dir = Path(__file__).parent
        
        # Try to extract models_dir from any argument
        self.provided_models_dir = None
        if 'models_dir' in kwargs:
            self.provided_models_dir = kwargs['models_dir']
        elif len(args) >= 1:
            self.provided_models_dir = args[0]
        # Also accept a second positional argument if given (ignore)
        # No error regardless of how many args

    def generate(self, image_path, output_path, variant_id, **kwargs):
        mesh_path = kwargs.get('mesh_path')
        if not mesh_path:
            return {"status": "error", "error": "mesh_path missing"}

        try:
            # Configuration
            config_file = self.extension_dir / "config.json"
            if config_file.exists():
                with open(config_file) as f:
                    cfg = json.load(f)
                    hunyuan_root = Path(cfg.get("hunyuan_root", self.extension_dir / "Hunyuan3D-2.1"))
                    models_dir = Path(cfg.get("models_dir", self.extension_dir / "models"))
            else:
                hunyuan_root = self.extension_dir / "Hunyuan3D-2.1"
                models_dir = self.extension_dir / "models"

            if self.provided_models_dir:
                models_dir = Path(self.provided_models_dir)

            models_dir.mkdir(parents=True, exist_ok=True)

            # Validate inputs
            for p in [mesh_path, image_path]:
                if not os.path.exists(p):
                    return {"status": "error", "error": f"File not found: {p}"}

            if not hunyuan_root.exists():
                return {"status": "error", "error": f"Hunyuan3D repo missing at {hunyuan_root}. Run setup."}

            # Check for model weights
            weight_files = list(models_dir.glob("*.safetensors")) + list(models_dir.glob("*.bin")) + list(models_dir.glob("*.pth"))
            if not weight_files:
                return {"status": "error", "error": f"No model weights in {models_dir}. Download them first."}

            # Lazy imports
            sys.path.insert(0, str(hunyuan_root))
            sys.path.insert(0, str(hunyuan_root / 'hy3dpaint'))
            from textureGenPipeline import Hunyuan3DPaintPipeline, Hunyuan3DPaintConfig

            # Variant
            if variant_id == "paint-ultra":
                params = {"max_num_view": 9, "resolution": 768}
            else:
                params = {"max_num_view": 6, "resolution": 512}

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
