'''
# AlphaSeparate

## 概要
- 指定されたpng画像にアルファマップを適用する

## 使い方
- python AlphaSeparate.py [メイン画像] [アルファマップ]
- 例
  - MakeColorLogo.py test.png alpha.png
    - test_out.pngに画像が出力される
    - test_out.pngはカラー値が全ピクセルtest.pngと一致し、  
      アルファ値がalpha.pngの値となったもの
    - alpha.pngに指定されるアルファマップは黒～白のカラー値でアルファ値があらわされた画像

## 入力画像について
- メイン画像とアルファマップは同ピクセル数でなければ処理は行わない
'''


import sys
from pathlib import Path
from PIL import Image


def exec_img(img_path, alphamap_path):
    img = Image.open(img_path).convert("RGBA")
    alphamap = Image.open(alphamap_path).convert("RGBA")

    if img.size != alphamap.size:
        print(f"Error: Image size {img.size} and Alpha map size {alphamap.size} do not match.")
        return

    result_img = Image.new("RGBA", img.size)

    for x in range(img.width):
        for y in range(img.height):
            p = img.getpixel((x, y))
            a_map = alphamap.getpixel((x, y))
            r, g, b, _ = p
            a = a_map[0]  # Use red channel of alpha map for alpha value

            result_pixel = (r, g, b, a)
            result_img.putpixel((x, y), result_pixel)

    base_stem = Path(img_path).stem
    output_path = f"{base_stem}_out.png"
    result_img.save(output_path)
    print(f"Saved {output_path}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python AlphaSeparate.py [image] [alpha_map]")
        return

    img_path = sys.argv[1]
    alphamap_path = sys.argv[2]

    exec_img(img_path, alphamap_path)

if __name__ == "__main__":
    main()
