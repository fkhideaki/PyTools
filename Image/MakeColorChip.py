'''
# MakeColorChip

## 概要
- カラーチップ状の画像ファイルを作成する機能
- 指定画像が1色のみの画像の前提で、その色の正方形の画像に変換して上書きする

## 使い方
- python MakeColorChip.py [画像]
'''


import sys
from pathlib import Path
from PIL import Image
import numpy as np


def make_square(img, sz):
    '''指定画像の(0, 0)の色の正方形の画像を生成'''
    col = img.getpixel((0, 0))
    ary_dst = np.zeros((sz, sz, 4), dtype=np.uint8)
    ary_dst[:, :, :3] = col[:3]
    ary_dst[:, :, 3] = 255
    return Image.fromarray(ary_dst)

def exec_img(img: Path):
    src = Image.open(img)
    coltip = make_square(src, 100)
    coltip.save(img)
    print(f"Saved {img}")

def main():
    for img in sys.argv[1:]:
        exec_img(Path(img))

if __name__ == "__main__":
    main()
