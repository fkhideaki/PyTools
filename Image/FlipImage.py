'''
# FlipImage

## 概要
- 画像を左右/上下方向に反転させる

## 使い方
- python FlipImage.py [option] [画像]
- option
  - --v : 上下方向に反転
  - --h : 左右方向に反転
'''


import sys
from pathlib import Path
from PIL import Image

def main():
    vertical = False
    horizontal = False
    files: list[Path] = []
    for arg in sys.argv[1:]:
        if arg == "--v":
            vertical = True
        elif arg == "--h":
            horizontal = True
        else:
            p = Path(arg)
            if p.exists():
                files.append(p)

    if not files:
        print("No valid image files provided.")
        return
    if vertical and horizontal:
        print("Please specify only one option: --v or --h.")
        return
    if not vertical and not horizontal:
        print("Please specify an option: --v or --h.")
        return

    for img_path in files:
        img = Image.open(img_path)
        if vertical:
            flipped_img = img.transpose(Image.FLIP_TOP_BOTTOM)
        elif horizontal:
            flipped_img = img.transpose(Image.FLIP_LEFT_RIGHT)

        output_path = img_path.parent / f"{img_path.stem}_flipped{img_path.suffix}"
        flipped_img.save(output_path)
        print(f"Saved {output_path}")

if __name__== "__main__":
    main()
