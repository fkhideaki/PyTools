"""
GLB → OBJ 変換スクリプト
依存: pip install trimesh
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import trimesh


# glTF(Y-up) → Blender(Z-up) への変換行列
# X軸まわり +90° 回転
#   X' =  X
#   Y' = -Z
#   Z' =  Y
GLTF_TO_BLENDER = np.array([
    [1,  0,  0,  0],
    [0,  0, -1,  0],
    [0,  1,  0,  0],
    [0,  0,  0,  1],
], dtype=float)


def convert_glb_to_obj(
    input_path: str,
    output_path: str | None = None,
    blender_coords: bool = True,
) -> Path:
    """
    GLBファイルをOBJ形式に変換する。

    Args:
        input_path    : 入力GLBファイルのパス
        output_path   : 出力OBJファイルのパス（省略時は同名で拡張子を .obj に変更）
        blender_coords: True のとき glTF(Y-up) → Blender(Z-up) に座標変換する

    Returns:
        書き出したOBJファイルのPathオブジェクト
    """
    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"入力ファイルが見つかりません: {input_file}")

    output_file = Path(output_path) if output_path else input_file.with_suffix(".obj")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"読み込み中: {input_file}")
    scene = trimesh.load(str(input_file), force="scene")

    # シーン内の全メッシュを結合
    if isinstance(scene, trimesh.Scene):
        geometries = list(scene.geometry.values())
        if not geometries:
            raise ValueError("GLBファイルにメッシュが含まれていません。")
        mesh = trimesh.util.concatenate(geometries)
    elif isinstance(scene, trimesh.Trimesh):
        mesh = scene
    else:
        raise TypeError(f"非対応のオブジェクト型: {type(scene)}")

    # --- 座標系変換 ---
    if blender_coords:
        mesh.apply_transform(GLTF_TO_BLENDER)
        print("  座標系変換: glTF(Y-up) → Blender(Z-up)  [X軸 +90°]")
    else:
        print("  座標系変換: なし（glTF/OBJ標準 Y-up のまま出力）")

    print(f"  頂点数  : {len(mesh.vertices):,}")
    print(f"  面数    : {len(mesh.faces):,}")

    mesh.export(str(output_file))
    print(f"書き出し完了: {output_file}")

    return output_file


def main():
    parser = argparse.ArgumentParser(
        description="GLBファイルをOBJ形式に変換します。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # Blender座標系(Z-up)で出力（デフォルト）
  python glb_to_obj.py model.glb

  # glTF/OBJ標準座標系(Y-up)のまま出力
  python glb_to_obj.py model.glb --no-blender-coords

  # 出力先を指定
  python glb_to_obj.py model.glb -o output/model.obj
        """,
    )
    parser.add_argument("input", help="入力 GLB ファイルのパス")
    parser.add_argument("-o", "--output", default=None, help="出力 OBJ ファイルのパス（省略可）")
    parser.add_argument(
        "--no-blender-coords",
        dest="blender_coords",
        action="store_false",
        help="座標変換を行わず glTF(Y-up) のまま出力する",
    )
    parser.set_defaults(blender_coords=True)
    args = parser.parse_args()

    try:
        convert_glb_to_obj(args.input, args.output, args.blender_coords)
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
