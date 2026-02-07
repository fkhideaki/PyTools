'''
# ExpandAlpha.py

## 概要
- アルファチャンネルを膨張させ、RGB色を拡張するツール
- 3DCGのテクスチャ作成時などに、アルファ境界の色抜けを防止するための機能

## 使い方
- python ExpandAlpha.py [画像ファイル] [options]
- options:
  - --thick:[n] : 膨張の太さを指定
  - --pass:[n] : 膨張の繰り返し回数
  - --saveTmp : 中間結果を保存する
'''


import sys
from pathlib import Path
from PIL import Image

from lib.ImageUT import AlphaExpand, AlphaExpandCfg


def exec_img(fp, cfg: AlphaExpandCfg):
    src = Image.open(fp).convert('RGBA')
    _, _, _, am = src.split()
    
    ext = AlphaExpand._expand(src, cfg)
    rr, rg, rb, _ = ext.split()
    dst = Image.merge("RGBA", (rr, rg, rb, am))
    dst.save(fp.parent / (fp.stem + "_expand.png"))

    if cfg.save_tmp:
        ext.save(fp.parent / (fp.stem + "_expand_t1.png"))
        ext_rgb = Image.merge("RGB", (rr, rg, rb))
        ext_rgb.save(fp.parent / (fp.stem + "_expand_t2.png"))

def main():
    options: list[str] = []
    files: list[str] = []
    for s in sys.argv[1:]:
        if s.startswith('--'):
            options.append(s)
        else:
            files.append(s)

    cfg = AlphaExpandCfg(3, 3)
    for s in options:
        if s.startswith('--thick:'):
            cfg.thickness = int(s.split(':')[1])
        elif s.startswith('--pass:'):
            cfg.passes = int(s.split(':')[1])
        elif s == '--saveTmp':
            cfg.save_tmp = True

    for s in files:
        p = Path(s)
        if p.is_file():
            exec_img(p, cfg)

if __name__ == "__main__":
    main()
