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
'''


from dataclasses import dataclass
from pathlib import Path
from PIL import Image
import os
import sys


@dataclass
class SizeReq:
    scale: float | None = None
    width: int | None = None
    height: int | None = None
    max_len: int | None = None


def resizeMain(img: Image, dst_size: SizeReq):
    resample = Image.Resampling.BILINEAR
    scale = dst_size.scale
    width = dst_size.width
    height = dst_size.height
    max_len = dst_size.max_len

    orgW, orgH = img.size
    if scale is not None:
        newW = int(orgW * scale)
        newH = int(orgH * scale)
        return img.resize((newW, newH), resample)
    elif width is not None:
        newW = width
        newH = int(width * orgH / orgW)
        return img.resize((newW, newH), resample)
    elif height is not None:
        newH = height
        newW = int(height * orgW / orgH)
        return img.resize((newW, newH), resample)
    elif max_len is not None:
        if orgW >= orgH:
            newW = max_len
            newH = int(max_len * orgH / orgW)
        else:
            newH = max_len
            newW = int(max_len * orgW / orgH)
        return img.resize((newW, newH), resample)
    return img

def resizeImg(fp: Path, dst_size: SizeReq, saveType):
    print(fp)
    if not os.path.exists(fp):
        print(f"  ファイルが見つかりません: {fp}")
        return
    
    ext = os.path.splitext(fp)[1].lower()
    if ext not in ['.webp', '.avif', '.png']:
        print(f"  サポートされていない形式です: {fp}")
        return

    img = Image.open(fp)
    outImg = resizeMain(img, dst_size)

    saveType = saveType if saveType else ext
    base = os.path.splitext(fp)[0]
    outFN = f"{base}_resized{saveType}"

    if saveType == '.webp':
        outImg.save(outFN, 'WEBP', quality=85)
    elif saveType == '.avif':
        outImg.save(outFN, 'AVIF', quality=85)
    elif saveType == '.png':
        outImg.save(outFN, 'PNG', optimize=True)

def resizeImgInDir(dir_path: Path, dst_size: SizeReq, outType):
    for f in dir_path.iterdir():
        if f.is_file():
            resizeImg(f, dst_size, outType)

def main():
    options: list[str] = []
    files: list[str] = []
    for s in sys.argv[1:]:
        if s.startswith('--'):
            options.append(s)
        else:
            files.append(s)

    dst_size = SizeReq()
    outType = None
    for s in options:
        if s.startswith('--s'):
            dst_size.scale = float(s.split(':')[1])
        elif s.startswith('--w'):
            dst_size.width = int(s.split(':')[1])
        elif s.startswith('--h'):
            dst_size.height = int(s.split(':')[1])
        elif s.startswith('--b'):
            dst_size.max_len = int(s.split(':')[1])
        elif s.startswith('--t'):
            outType = '.' + s.split(':')[1]

    for s in files:
        p = Path(s)
        if p.is_dir():
            resizeImgInDir(p, dst_size, outType)
        elif p.is_file():
            resizeImg(s, dst_size, outType)

if __name__ == "__main__":
    main()
