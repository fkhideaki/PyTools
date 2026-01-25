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


def get_img_color(color_path):
    '''
    - 指定画像ファイルの代表色を取得する
    - 指定される画像ファイルは全ピクセルが同じ色の前提だが  
      この関数では(0, 0)の色を返す
    '''
    img = Image.open(color_path)
    return img.getpixel((0, 0))

def make_logo(logo_path, color_pixel):
    logo_img = Image.open(logo_path).convert("RGBA")

    result_img = Image.new("RGBA", logo_img.size)

    cr, cg, cb = color_pixel
    for x in range(logo_img.width):
        for y in range(logo_img.height):
            p = logo_img.getpixel((x, y))
            a = p[3]
            result_pixel = (cr, cg, cb, a)
            result_img.putpixel((x, y), result_pixel)

    return result_img

def exec_img(logo_path, color_path):
    color_pixel = get_img_color(color_path)

    result_img = make_logo(logo_path, color_pixel)

    output_path = f"{Path(logo_path).stem}_{Path(color_path).stem}.png"
    result_img.save(output_path)
    print(f"Saved {output_path}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python MakeColorLogo.py [logo_image] [color_image]")
        return

    logo_path = sys.argv[1]
    color_path = sys.argv[2]
    exec_img(logo_path, color_path)

if __name__ == "__main__":
    main()
