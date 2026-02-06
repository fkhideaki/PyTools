'''
# AlphaSeparate

## 概要
- 指定されたpng画像のアルファとカラーを分離する

## 使い方
- python AlphaSeparate.py [画像]
- 例
  - MakeColorLogo.py test.png
    - test_c.pngに、test.pngから抽出した色で、アルファ値255の画像を出力する
    - test_a.pngに、test.pngのアルファ値を黒～白のグレイスケールで、アルファ値255の画像を出力する
'''


import sys
from pathlib import Path
from PIL import Image
import numpy as np


def separate_alpha(img: Image):
    arr = np.array(img)
    
    color_arr = arr.copy()
    color_arr[:, :, 3] = 255
    color_img = Image.fromarray(color_arr)
    
    alpha_arr = np.zeros_like(arr)
    alpha_arr[:, :, :3] = arr[:, :, 3:4]
    alpha_arr[:, :, 3] = 255
    alpha_img = Image.fromarray(alpha_arr)

    return color_img, alpha_img

def exec_img(img_path: Path):
    img = Image.open(img_path).convert("RGBA")

    color_img, alpha_img = separate_alpha(img)

    base = img_path.parent / img_path.stem
    color_img.save(f"{base}_c.png")
    alpha_img.save(f"{base}_a.png")


def main():
    for a in sys.argv[1:]:
        img_path = Path(a)
        exec_img(img_path)

if __name__ == "__main__":
    main()
