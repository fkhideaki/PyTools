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
'''


from dataclasses import dataclass, field
from pathlib import Path
from PIL import Image
import sys


@dataclass
class SizeCfg:
    scale: float | None = None
    width: int | None = None
    height: int | None = None
    max_len: int | None = None


@dataclass
class Cfg:
    repeat: bool = False
    out_type: str | None = None
    size_cfg: SizeCfg = field(default_factory=SizeCfg)


def getDstSize(img: Image, dst_size: SizeCfg):
    scale = dst_size.scale
    width = dst_size.width
    height = dst_size.height
    max_len = dst_size.max_len

    orgW, orgH = img.size
    if scale is not None:
        newW = int(orgW * scale)
        newH = int(orgH * scale)
        return (newW, newH)
    elif width is not None:
        newW = width
        newH = int(width * orgH / orgW)
        return (newW, newH)
    elif height is not None:
        newH = height
        newW = int(height * orgW / orgH)
        return (newW, newH)
    elif max_len is not None:
        if orgW >= orgH:
            newW = max_len
            newH = int(max_len * orgH / orgW)
        else:
            newH = max_len
            newW = int(max_len * orgW / orgH)
        return (newW, newH)
    return None

def resizeMain(img: Image, cfg: Cfg):
    resample = Image.Resampling.BILINEAR
    newSz = getDstSize(img, cfg.size_cfg)
    if newSz:
        return img.resize(newSz, resample)
    else:
        return img

def resizeImg(fp: Path, cfg: Cfg):
    print(fp)
    if not fp.is_file():
        print(f"  ファイルが見つかりません: {fp}")
        return
    
    ext = fp.suffix.lower()
    if ext not in ['.webp', '.avif', '.png']:
        print(f"  サポートされていない形式です: {fp}")
        return

    img = Image.open(fp)
    outImg = resizeMain(img, cfg)

    saveType = cfg.out_type if cfg.out_type else ext
    base = fp.parent / fp.stem
    outFN = f"{base}_resized{saveType}"

    if saveType == '.webp':
        outImg.save(outFN, 'WEBP', quality=85)
    elif saveType == '.avif':
        outImg.save(outFN, 'AVIF', quality=85)
    elif saveType == '.png':
        outImg.save(outFN, 'PNG', optimize=True)

def resizeImgInDir(dir_path: Path, cfg: Cfg):
    for f in dir_path.iterdir():
        if f.is_file():
            resizeImg(f, cfg)

def main():
    options: list[str] = []
    files: list[str] = []
    for s in sys.argv[1:]:
        if s.startswith('--'):
            options.append(s)
        else:
            files.append(s)

    cfg = Cfg()
    size_cfg = cfg.size_cfg
    for s in options:
        if s.startswith('--s'):
            size_cfg.scale = float(s.split(':')[1])
        elif s.startswith('--w'):
            size_cfg.width = int(s.split(':')[1])
        elif s.startswith('--h'):
            size_cfg.height = int(s.split(':')[1])
        elif s.startswith('--b'):
            size_cfg.max_len = int(s.split(':')[1])
        elif s.startswith('--t'):
            cfg.outType = '.' + s.split(':')[1]

    for s in files:
        p = Path(s)
        if p.is_dir():
            resizeImgInDir(p, cfg)
        elif p.is_file():
            resizeImg(p, cfg)

if __name__ == "__main__":
    main()
