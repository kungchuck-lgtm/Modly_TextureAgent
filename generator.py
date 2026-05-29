# generator.py
import pkg_resources
import os
import sys
from pathlib import Path

# Use Hunyuan3D-2.1 cloned by setup.py into the extension folder
EXTENSION_DIR = Path(__file__).parent
HUNYUAN_ROOT = Path(os.environ.get('HUNYUAN3D_ROOT', str(EXTENSION_DIR / "Hunyuan3D-2.1")))
sys.path.insert(0, str(HUNYUAN_ROOT / 'hy3dpaint'))

from textureGenPipeline import Hunyuan3DPaintPipeline, Hunyuan3DPaintConfig


class HunyuanTextureGenerator:
    """Modly extension class for Hunyuan3D-Paint texture generation."""
    
    def __init__(self):
        self.pipeline = None
        self.config = None
    
    def setup(self, variant_id: str = "paint-quality"):
        """Initialize the pipeline with the selected quality variant."""
        if variant_id == "paint-ultra":
            params = {"max_num_view": 9, "resolution": 768}
        else:
            params = {"max_num_view": 6, "resolution": 512}
        
        self.config = Hunyuan3DPaintConfig(**params)
        self.pipeline = Hunyuan3DPaintPipeline(self.config)
    
    def generate(self, image_path: str, output_path: str, variant_id: str, models_dir: str, **kwargs) -> dict:
        """Main entry point for Modly."""
        mesh_path = kwargs.get('mesh_path')
        if not mesh_path:
            return {"error": "mesh_path not provided. Please provide an existing mesh to texture."}
        
        try:
            # Initialize pipeline if not already done
            if self.pipeline is None:
                self.setup(variant_id)
            
            # Run texture generation
            final_mesh_path = self.pipeline(
                mesh_path=mesh_path,
                image_path=image_path,
                output_mesh_path=output_path
            )
            
            return {
                "output_path": final_mesh_path,
                "status": "success",
                "message": f"Model textured and saved to {final_mesh_path}"
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"An error occurred during texture generation: {str(e)}"
            }


# Modly looks for this exact class name
Generator = HunyuanTextureGenerator
