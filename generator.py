# generator.py - Main texture generation logic
import os
import sys
import traceback
from pathlib import Path

# Set up paths properly
EXTENSION_DIR = Path(__file__).parent
HUNYUAN_ROOT = Path(os.environ.get('HUNYUAN3D_ROOT', str(EXTENSION_DIR / "Hunyuan3D-2.1")))

# Add to Python path
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
        self.models_dir = Path(models_dir) if models_dir else EXTENSION_DIR / "models"
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
            return {
                "status": "error",
                "error": "mesh_path not provided. Please provide an existing mesh to texture."
            }
        
        if not os.path.exists(mesh_path):
            return {
                "status": "error",
                "error": f"Mesh file not found: {mesh_path}"
            }
        
        if not os.path.exists(image_path):
            return {
                "status": "error",
                "error": f"Reference image not found: {image_path}"
            }
        
        # Check if Hunyuan3D is installed
        if not HUNYUAN_ROOT.exists():
            return {
                "status": "error",
                "error": f"Hunyuan3D not found at {HUNYUAN_ROOT}. Please run setup first."
            }
        
        try:
            # Import the pipeline
            try:
                from textureGenPipeline import Hunyuan3DPaintPipeline, Hunyuan3DPaintConfig
            except ImportError as e:
                return {
                    "status": "error",
                    "error": f"Failed to import Hunyuan3D modules: {str(e)}\nMake sure setup.py completed successfully."
                }
            
            # Configure based on variant
            if variant_id == "paint-ultra":
                params = {"max_num_view": 9, "resolution": 768}
            else:  # paint-quality or default
                params = {"max_num_view": 6, "resolution": 512}
            
            print(f"Generating texture with params: {params}")
            print(f"Mesh: {mesh_path}")
            print(f"Reference image: {image_path}")
            print(f"Output path: {output_path}")
            
            # Ensure output directory exists
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Create config and pipeline
            config = Hunyuan3DPaintConfig(**params)
            paint_pipeline = Hunyuan3DPaintPipeline(config)
            
            # Run texture generation
            final_mesh_path = paint_pipeline(
                mesh_path=mesh_path,
                image_path=image_path,
                output_mesh_path=output_path
            )
            
            # Return success
            return {
                "output_path": str(final_mesh_path),
                "status": "success",
                "message": f"Model textured and saved to {final_mesh_path}"
            }
            
        except Exception as e:
            # Return detailed error
            error_details = traceback.format_exc()
            print(f"Error during texture generation: {error_details}")
            
            return {
                "status": "error",
                "error": f"An error occurred during texture generation: {str(e)}",
                "traceback": error_details if os.environ.get('DEBUG') else None
            }
