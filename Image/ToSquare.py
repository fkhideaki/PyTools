'''
# ToSquare

## 概要
- 指定画像を正方形化する
- 入力画像の長辺維持で、短辺側に透過の余白を追加して正方形化する
  - 元画像は中央に配置される
- 出力はpng形式
- 入力が正方形でも出力を行う

## 使い方
- python ToSquare.py [画像]
  - python ToSquare.py a.png
    - a.png -> a_square.png というファイル名で出力
'''


import sys
from pathlib import Path
from PIL import Image
import numpy as np

def has_alpha(img: Image.Image):
    '''画像にアルファチャンネルがあるか判定'''
    return img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info)

def to_square(img: Path):
    src = Image.open(img)
    w, h = src.size
    sz = max(w, h)
    ary_dst = np.zeros((sz, sz, 4), dtype=np.uint8)

    ary_src = np.array(src)
    if not has_alpha(src):
        # アルファチャンネルがない場合は不透明にする
        ary_src = np.dstack((ary_src, np.full((h, w), 255, dtype=np.uint8)))

    # 中央に配置するためのオフセットを計算
    offset_x = (sz - w) // 2
    offset_y = (sz - h) // 2
    ary_dst[offset_y:offset_y + h, offset_x:offset_x + w] = ary_src

    result_img = Image.fromarray(ary_dst)
    out_file = img.stem + "_square.png"
    result_img.save(out_file)
    print(f"Saved {out_file}")

def main():
    for a in sys.argv[1:]:
        img = Path(a)
        if not img.exists():
            print(f"File not found: {img}")
            continue
        to_square(img)

if __name__ == "__main__":
    main()
