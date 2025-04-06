import bpy
import os
import sys


if __name__ == "__main__":
    argv = sys.argv

    input_path = argv[5]
    bpy.ops.wm.open_mainfile(filepath=input_path)

    format = argv[6]
    output_path = argv[7]  # strict argc==5 -> len=6 will be used as argument see Reformat_blender_to_obj.py

    # Export to the specified format
    if format == ".obj":
        bpy.ops.export_scene.obj(filepath=output_path)
    elif format == ".fbx":
        bpy.ops.export_scene.fbx(filepath=output_path)
    elif format == ".gltf":
        bpy.ops.export_scene.gltf(filepath=output_path, export_format='GLTF_SEPARATE')
    elif format == ".x3d":
        bpy.ops.export_scene.x3d(filepath=output_path)
    elif format == ".blend":
        bpy.ops.wm.save_as_mainfile(filepath=output_path)
    elif format == ".glb":
        bpy.ops.export_scene.gltf(filepath=output_path, export_format='GLB')
    else:
        bpy.ops.export_scene.obj(filepath=output_path)

    # Export to .glb format
    if format == ".glb":
        bpy.ops.export_scene.gltf(filepath=output_path, export_format='GLB')
    else:
        glb_output_path = os.path.splitext(output_path)[0] + ".glb"
        bpy.ops.export_scene.gltf(filepath=glb_output_path, export_format='GLB')


    # Must exit with 0 to avoid error!
    exit(0)