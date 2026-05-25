'''
# ResizeImage.py

## 概要
- 画像ファイルを指定したスケールでリサイズするツール

## 使い方
- python ResizeImage.py [files or directories] [options]
- options:
  - --s:[scale] : リサイズのスケールを指定（例: --s:0.5）
  - --w:[pixel] : 縦横比維持で横幅が指定値とあるようにリサイズする
  - --h:[pixel] : 縦横比維持で縦幅が指定値とあるようにリサイズする
  - --b:[pixel] : 縦横比維持で長辺が指定値とあるようにリサイズする
  - --t:[type] : 出力画像の形式を指定、デフォルトは元の形式
    - 対応形式
      - --t:webp
      - --t:avif
      - --t:png
  - --repeat : リピートリサンプルでリサイズする
  - --separate : カラーとアルファを個別にリサンプルして透過部のカラー値を維持する
'''


import sys
from dataclasses import dataclass, field
from pathlib import Path
from PIL import Image

from lib.ImageUT import FilesOperator, ImageResizeExt, ResizeCfg


@dataclass
class Cfg:
    resize_cfg: ResizeCfg = field(default_factory=ResizeCfg)
    out_type: str | None = None


def proc_img(fp: Path, cfg: Cfg):
    print(fp)
    if not fp.is_file():
        print(f"  ファイルが見つかりません: {fp}")
        return
    
    ext = fp.suffix.lower()
    if ext not in ['.webp', '.avif', '.png']:
        print(f"  サポートされていない形式です: {fp}")
        return

    img = Image.open(fp)
    outImg = ImageResizeExt.resize(img, cfg.resize_cfg)

    save_type = cfg.out_type if cfg.out_type else ext
    base = fp.parent / fp.stem
    outFN = f"{base}_resized{save_type}"

    if save_type == '.webp':
        outImg.save(outFN, 'WEBP', quality=85)
    elif save_type == '.avif':
        outImg.save(outFN, 'AVIF', quality=85)
    elif save_type == '.png':
        outImg.save(outFN, 'PNG', optimize=True)

def main():
    options: list[str] = []
    files: list[str] = []
    for s in sys.argv[1:]:
        if s.startswith('--'):
            options.append(s)
        else:
            files.append(s)

    cfg = Cfg()
    resize_cfg = cfg.resize_cfg
    target_size = resize_cfg.target_size
    for s in options:
        if s.startswith('--s:'):
            target_size.scale = float(s.split(':')[1])
        elif s.startswith('--w:'):
            target_size.width = int(s.split(':')[1])
        elif s.startswith('--h:'):
            target_size.height = int(s.split(':')[1])
        elif s.startswith('--b:'):
            target_size.max_len = int(s.split(':')[1])
        elif s.startswith('--t:'):
            cfg.out_type = '.' + s.split(':')[1]
        elif s == '--repeat':
            resize_cfg.repeat = True
        elif s == '--separate':
            resize_cfg.separate_rgb = True

    op = FilesOperator.from_strs(files)
    for s in op.iterate():
        p = Path(s)
        proc_img(p, cfg)

if __name__ == "__main__":
    main()
