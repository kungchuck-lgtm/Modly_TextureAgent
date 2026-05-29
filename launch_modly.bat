@echo off
REM Point to your Hunyuan3D-2.1 installation
set HUNYUAN3D_ROOT=J:\Project\ModlyHunyuanPaintAgent\Hunyuan3D-2.1

REM Activate the venv with bpy and all packages
call J:\Project\ModlyHunyuanPaintAgent\Hunyuan3D-2.1\venv\Scripts\activate.bat

REM Launch Modly (adjust this to Modly's actual executable)
start "" "J:\Modly\Modly.exe"