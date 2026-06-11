"""
GLB → OBJ 変換スクリプト
依存: pip install trimesh
"""

import argparse
import sys
from pathlib import Path

import trimesh


def convert_glb_to_obj(input_path: str, output_path: str | None = None) -> Path:
    """
    GLBファイルをOBJ形式に変換する。

    Args:
        input_path : 入力GLBファイルのパス
        output_path: 出力OBJファイルのパス（省略時は同名で拡張子を .obj に変更）

    Returns:
        書き出したOBJファイルのPathオブジェクト
    """
    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"入力ファイルが見つかりません: {input_file}")

    # 出力パスが省略されていれば、入力ファイルと同フォルダに .obj で作成
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

    print(f"  頂点数  : {len(mesh.vertices):,}")
    print(f"  面数    : {len(mesh.faces):,}")

    # OBJとして書き出し（同名の .mtl も自動生成される）
    mesh.export(str(output_file))
    print(f"書き出し完了: {output_file}")

    return output_file


def main():
    parser = argparse.ArgumentParser(
        description="GLBファイルをOBJ形式に変換します。"
    )
    parser.add_argument("input", help="入力 GLB ファイルのパス")
    parser.add_argument(
        "-o", "--output", default=None, help="出力 OBJ ファイルのパス（省略可）"
    )
    args = parser.parse_args()

    try:
        convert_glb_to_obj(args.input, args.output)
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
