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


def separate_alpha(img):
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

    return color_img, alpha_img

def exec_img(img_path: Path):
    img = Image.open(img_path).convert("RGBA")

    color_img, alpha_img = separate_alpha(img)

    base = img_path.parent / img_path.stem
    color_img.save(f"{base}_c.png")
    alpha_img.save(f"{base}_a.png")


def main():
    for img_path in sys.argv[1:]:
        exec_img(Path(img_path))

if __name__ == "__main__":
    main()
