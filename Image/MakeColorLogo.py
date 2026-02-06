'''
# MakeColorLogo

## 概要
- ロゴ画像の色展開ツール
- 指定画像の形状維持で、カラーだけを指定色に変更したデータを出力する

## 使い方
- python MakeColorLogo.py [ロゴ画像] [色指定画像]
- 例
  - MakeColorLogo.py base.png c0.png
    - base.pngと同サイズ、アルファ値一致で、色が全ピクセルc0.pngの画像を  
      base_c0.pngという名称でファイルに出力する

## 入力画像について
- ロゴ画像
  - 透過情報を持つPNG画像を想定
- 色指定画像
  - 全ピクセルが同じ色のPNG画像を想定
  - 画像の(0, 0)の色を代表色として使用するため、サイズは問わない
'''


import sys
from pathlib import Path
from PIL import Image
import numpy as np


def make_logo(logo_path: Path, color_path: Path):
    color_img = Image.open(color_path)
    logo_img = Image.open(logo_path)

    ary_col = np.array(color_img)
    ary_a = np.array(logo_img)

    ary_dst = np.zeros_like(ary_a)
    ary_dst[:, :, :3] = ary_col[0, 0, :3]
    ary_dst[:, :, 3] = ary_a[:, :, 3]

    result_img = Image.fromarray(ary_dst)
    return result_img

def exec_img(logo_path: Path, color_path: Path):
    result_img = make_logo(logo_path, color_path)

    output_path = logo_path.parent / f"{logo_path.stem}_{color_path.stem}.png"
    result_img.save(output_path)
    print(f"Saved {output_path}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python MakeColorLogo.py [logo_image] [color_image]")
        return

    logo_path = Path(sys.argv[1])
    color_path = Path(sys.argv[2])
    exec_img(logo_path, color_path)

if __name__ == "__main__":
    main()
