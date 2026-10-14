'''
# Halfstep.py

## 概要
- 画像ファイルをハーフステップリピートの1単位に変換する

## 使い方
- python Halfstep.py [file] [options]
- options:
  - --v : 縦に2倍にして半周期ずらした画像を作成
  - --h : 横に2倍にして半周期ずらした画像を作成
'''

import sys
from pathlib import Path
from PIL import Image
from lib.ImageUT import ImgRepeat


def main():
    to_vert = False
    to_horiz = False
    files: list[Path] = []
    for arg in sys.argv[1:]:
        if arg == "--v":
            to_vert = True
        elif arg == "--h":
            to_horiz = True
        else:
            path = Path(arg)
            if not path.is_file():
                print(f"File not found: {arg}")
                continue
            files.append(path)

    if not (to_vert or to_horiz):
        print("Please specify --v or --h")
        return

    for path in files:
        if not path.is_file():
            continue

        img = Image.open(path)
        out_img = ImgRepeat.make_halfstep_repeat(img, to_vert)
        suf = "V" if to_vert else "H"
        out_file = path.with_name(f"{path.stem}_HS{suf}.png")
        out_img.save(out_file)

if __name__ == "__main__":
    main()
