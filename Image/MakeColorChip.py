'''
# MakeColorChip

## 概要
- カラーチップ状の画像ファイルを作成する機能
- 指定画像から代表色を1色取得して、その色の正方形の画像を出力する
- もしくは指定されたRGB値の正方形の画像を作成する

## 使い方
- python MakeColorChip.py [画像]
  - 指定画像の代表色の正方形を、元ファイル名+_out.pngという形式で出力する
- python MakeColorChip.py --rgb:[r],[g],[b]
  - --rgb:255,0,100 のように指定された色の正方形の画像を出力する
  - ファイル名は"rgb(255,0,100).png"の形式となる
'''


import sys
from pathlib import Path
from PIL import Image
import numpy as np


def get_base_col(img):
    '''指定画像の(0, 0)の色を取得'''
    return img.getpixel((0, 0))

def make_square(sz, col):
    '''指定色の正方形の画像を生成'''
    ary_dst = np.zeros((sz, sz, 4), dtype=np.uint8)
    ary_dst[:, :, :3] = col[:3]
    ary_dst[:, :, 3] = 255
    return Image.fromarray(ary_dst)

def exec_img(img: Path):
    src = Image.open(img)
    col = get_base_col(src)
    coltip = make_square(100, col)
    out_file = img.stem + "_out.png"
    coltip.save(out_file)
    print(f"Saved {out_file}")

def exec_rgb(rgb):
    col = tuple(map(int, rgb.split(",")))
    coltip = make_square(100, col)
    out_file = f"rgb({col[0]},{col[1]},{col[2]}).png"
    coltip.save(out_file)
    print(f"Saved {out_file}")

def main():
    for img in sys.argv[1:]:
        if img.startswith("--rgb:"):
            exec_rgb(img[6:])
        else:
            exec_img(Path(img))

if __name__ == "__main__":
    main()
