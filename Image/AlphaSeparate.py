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

from lib.ImageUT import Alphamap


def exec_img(img_path: Path):
    img = Image.open(img_path).convert("RGBA")

    color_img, alpha_img = Alphamap.separate(img)

    base = img_path.parent / img_path.stem
    color_img.save(f"{base}_c.png")
    alpha_img.save(f"{base}_a.png")


def main():
    for a in sys.argv[1:]:
        img_path = Path(a)
        exec_img(img_path)

if __name__ == "__main__":
    main()
