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


def exec_img(img_path):
    img = Image.open(img_path).convert("RGBA")

    color_img = Image.new("RGBA", img.size)
    alpha_img = Image.new("RGBA", img.size)

    for x in range(img.width):
        for y in range(img.height):
            p = img.getpixel((x, y))
            r, g, b, a = p

            color_pixel = (r, g, b, 255)
            alpha_pixel = (a, a, a, 255)

            color_img.putpixel((x, y), color_pixel)
            alpha_img.putpixel((x, y), alpha_pixel)

    base_stem = Path(img_path).stem
    color_output_path = f"{base_stem}_c.png"
    alpha_output_path = f"{base_stem}_a.png"

    color_img.save(color_output_path)
    alpha_img.save(alpha_output_path)


def main():
    for img_path in sys.argv[1:]:
        exec_img(img_path)

if __name__ == "__main__":
    main()
