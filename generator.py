# api/extensions/hunyuan-texture/generator.py

# Fix for pkg_resources issue with newer setuptools
import pkg_resources

import os
import sys
from pathlib import Path

# Add the path to your Hunyuan3D-2.1 repo to the system path
# Uses environment variable HUNYUAN3D_ROOT, with fallback to default path
HUNYUAN_ROOT = Path(os.environ.get('HUNYUAN3D_ROOT', 'J:/Project/ModlyHunyuanPaintAgent/Hunyuan3D-2.1'))
sys.path.insert(0, str(HUNYUAN_ROOT / 'hy3dpaint'))

from textureGenPipeline import Hunyuan3DPaintPipeline, Hunyuan3DPaintConfig


def generate(image_path: str, output_path: str, variant_id: str, models_dir: str, **kwargs) -> dict:
    """
    The main entry point for the Modly extension.
    
    Args:
        image_path: Path to the reference image
        output_path: Where to save the textured mesh
        variant_id: Which quality variant to use ('paint-quality' or 'paint-ultra')
        models_dir: Directory for cached models (provided by Modly)
        **kwargs: Additional arguments including 'mesh_path'
    
    Returns:
        dict with 'output_path' and 'status' keys
    """
    mesh_path = kwargs.get('mesh_path')
    if not mesh_path:
        return {"error": "mesh_path not provided. Please provide an existing mesh to texture."}

    try:
        # 1. Configure the pipeline based on the user's chosen variant
        if variant_id == "paint-ultra":
            params = {"max_num_view": 9, "resolution": 768}
        else:  # paint-quality or default
            params = {"max_num_view": 6, "resolution": 512}

        config = Hunyuan3DPaintConfig(**params)
        paint_pipeline = Hunyuan3DPaintPipeline(config)

        # 2. Run the texture generation
        final_mesh_path = paint_pipeline(
            mesh_path=mesh_path,
            image_path=image_path,
            output_mesh_path=output_path
        )

        # 3. Return success
        return {
            "output_path": final_mesh_path,
            "status": "success",
            "message": f"Model textured and saved to {final_mesh_path}"
        }

    except Exception as e:
        # 4. Return error details back to Modly
        return {
            "status": "error",
            "message": f"An error occurred during texture generation: {str(e)}"
        }