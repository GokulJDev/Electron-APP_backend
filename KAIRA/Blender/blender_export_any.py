import bpy
import os
import sys

if __name__ == "__main__":
    argv = sys.argv
    argv = argv[argv.index("--") + 1:]  # everything after '--'

    if len(argv) < 3:
        print("❌ Not enough arguments. Usage: <input.blend> <format> <output>")
        exit(1)

    input_path = argv[0]
    export_format = argv[1]
    output_path = argv[2]

    print(f"📂 Opening {input_path}")
    bpy.ops.wm.open_mainfile(filepath=input_path)

    if export_format == ".obj":
        bpy.ops.export_scene.obj(filepath=output_path)
    elif export_format == ".fbx":
        bpy.ops.export_scene.fbx(filepath=output_path)
    elif export_format == ".gltf":
        bpy.ops.export_scene.gltf(filepath=output_path, export_format='GLTF_SEPARATE')
    elif export_format == ".x3d":
        bpy.ops.export_scene.x3d(filepath=output_path)
    elif export_format == ".blend":
        bpy.ops.wm.save_as_mainfile(filepath=output_path)
    elif export_format == ".glb":
        bpy.ops.export_scene.gltf(filepath=output_path, export_format='GLB')
    else:
        print(f"⚠️ Unknown format '{export_format}', defaulting to OBJ.")
        bpy.ops.export_scene.obj(filepath=output_path)

    exit(0)
