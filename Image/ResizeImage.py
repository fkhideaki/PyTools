'''
# ResizeImage.py

## 概要
- 画像ファイルを指定したスケールでリサイズするツール

## 使い方
- python ResizeImage.py [files or directories] [options]
- options:
  - --s:[scale] : リサイズのスケールを指定（例: --s:0.5 は50%にリサイズ、デフォルトは0.5）
  - --t:[type] : 出力画像の形式を指定（例: --t:webp、--t:avif、--t:png、デフォルトは元の形式）
'''

from pathlib import Path
from PIL import Image
import os
import sys

def resizeMain(img, scale):
    orgW, orgH = img.size
    newW = int(orgW * scale)
    newH = int(orgH * scale)
    return img.resize((newW, newH), Image.Resampling.LANCZOS)

def resizeImg(fn, scale, saveType=None):
    print(fn)
    if not os.path.exists(fn):
        print(f"ファイルが見つかりません: {fn}")
        return
    
    ext = os.path.splitext(fn)[1].lower()
    if ext not in ['.webp', '.avif', '.png']:
        print(f"サポートされていない形式です: {fn}")
        return

    img = Image.open(fn)

    resized = resizeMain(img, scale)

    saveType = saveType if saveType else ext
    base = os.path.splitext(fn)[0]
    outFN = f"{base}_resized{saveType}"

    if saveType == '.webp':
        resized.save(outFN, 'WEBP', quality=85)
    elif saveType == '.avif':
        resized.save(outFN, 'AVIF', quality=85)
    elif saveType == '.png':
        resized.save(outFN, 'PNG', optimize=True)

def main():
    options: list[str] = []
    files: list[str] = []
    for s in sys.argv[1:]:
        if s.startswith('--'):
            options.append(s)
        else:
            files.append(s)

    scale = 0.5
    outType = None
    for s in options:
        if s.startswith('--s'):
            scale = float(s.split(':')[1])
        elif s.startswith('--t'):
            outType = '.' + s.split(':')[1]

    for s in files:
        p = Path(s)
        if p.is_dir():
            for f in p.iterdir():
                if f.is_file():
                    resizeImg(f, scale, outType)
        elif p.is_file():
            resizeImg(s, scale, outType)

if __name__ == "__main__":
    main()
