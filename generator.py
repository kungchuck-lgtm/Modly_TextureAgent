# generator.py - Main texture generation logic
import os
import sys
import json
import traceback
from pathlib import Path

EXTENSION_DIR = Path(__file__).parent
HUNYUAN_ROOT = Path(os.environ.get('HUNYUAN3D_ROOT', str(EXTENSION_DIR / "Hunyuan3D-2.1")))
MODELS_DIR = Path(os.environ.get('HUNYUAN_MODELS_DIR', str(EXTENSION_DIR / "models")))

# Load config if exists
config_file = EXTENSION_DIR / "config.json"
if config_file.exists():
    with open(config_file, "r") as f:
        config = json.load(f)
        HUNYUAN_ROOT = Path(config.get("hunyuan_root", HUNYUAN_ROOT))
        MODELS_DIR = Path(config.get("models_dir", MODELS_DIR))

# Add Hunyuan3D to Python path
if HUNYUAN_ROOT.exists():
    sys.path.insert(0, str(HUNYUAN_ROOT))
    sys.path.insert(0, str(HUNYUAN_ROOT / 'hy3dpaint'))
else:
    print(f"Warning: Hunyuan3D directory not found at {HUNYUAN_ROOT}")

class HunyuanTextureGenerator:
    """
    Modly generator class for Hunyuan3D-Paint texture generation.
    """
    
    def __init__(self, models_dir: str = None):
        """
        Initialize the generator.
        
        Args:
            models_dir: Directory for cached models (provided by Modly)
        """
        self.models_dir = Path(models_dir) if models_dir else MODELS_DIR
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
    def generate(self, image_path: str, output_path: str, variant_id: str, **kwargs) -> dict:
        """
        Generate texture for a mesh using reference image.
        
        Args:
            image_path: Path to the reference image
            output_path: Where to save the textured mesh
            variant_id: Which quality variant to use ('paint-quality' or 'paint-ultra')
            **kwargs: Additional arguments including 'mesh_path'
        
        Returns:
            dict with 'output_path' and 'status' keys
        """
        mesh_path = kwargs.get('mesh_path')
        
        # Validate inputs
        if not mesh_path:
            return {"status": "error", "error": "mesh_path not provided"}
        if not os.path.exists(mesh_path):
            return {"status": "error", "error": f"Mesh not found: {mesh_path}"}
        if not os.path.exists(image_path):
            return {"status": "error", "error": f"Image not found: {image_path}"}
        if not HUNYUAN_ROOT.exists():
            return {"status": "error", "error": f"Hunyuan3D not found at {HUNYUAN_ROOT}"}
        
        # Check if model weights exist
        # Look for typical checkpoint files (adjust pattern as needed)
        model_files = list(self.models_dir.glob("*.safetensors")) + \
                      list(self.models_dir.glob("*.bin")) + \
                      list(self.models_dir.glob("*.pth"))
        if not model_files:
            return {
                "status": "error",
                "error": f"No model weights found in {self.models_dir}. Please run setup.py or download models manually."
            }
        
        try:
            # Import pipeline
            from textureGenPipeline import Hunyuan3DPaintPipeline, Hunyuan3DPaintConfig
            
            # Set up configuration - override model paths if needed
            if variant_id == "paint-ultra":
                params = {"max_num_view": 9, "resolution": 768}
            else:
                params = {"max_num_view": 6, "resolution": 512}
            
            # Important: Point the pipeline to the downloaded model directory
            # This depends on how the pipeline expects models; you may need to set env var or pass argument
            os.environ['HUNYUAN3D_WEIGHTS'] = str(self.models_dir)
            
            config = Hunyuan3DPaintConfig(**params)
            paint_pipeline = Hunyuan3DPaintPipeline(config)
            
            # Ensure output directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Run generation
            final_mesh_path = paint_pipeline(
                mesh_path=mesh_path,
                image_path=image_path,
                output_mesh_path=output_path
            )
            
            return {
                "output_path": str(final_mesh_path),
                "status": "success",
                "message": f"Textured mesh saved to {final_mesh_path}"
            }
            
        except Exception as e:
            error_details = traceback.format_exc()
            print(f"Error: {error_details}")
            return {
                "status": "error",
                "error": str(e),
                "traceback": error_details if os.environ.get('DEBUG') else None
            }
