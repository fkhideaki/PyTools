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
import numpy as np


@dataclass
class SizeCfg:
    scale: float | None = None
    width: int | None = None
    height: int | None = None
    max_len: int | None = None


@dataclass
class Cfg:
    repeat: bool = False
    separate_rgb: bool = False
    out_type: str | None = None
    size_cfg: SizeCfg = field(default_factory=SizeCfg)
    resample = Image.Resampling.BILINEAR


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

def repeat_sampling_resize(img, new_sz, sample):
    arr = np.array(img)
    
    kernel_size = 4
    pad_size = kernel_size
    if arr.ndim == 2:
        padded = np.pad(arr, pad_size, mode='wrap')
        mode = 'L'
    else:
        padded = np.pad(arr, ((pad_size, pad_size), (pad_size, pad_size), (0, 0)), mode='wrap')
        mode = img.mode
    
    padded_img = Image.fromarray(padded.astype(np.uint8), mode=mode)
    
    old_width, old_height = img.size
    new_width, new_height = new_sz
    
    scale_x = new_width / old_width
    scale_y = new_height / old_height
    
    intermediate_width = int((old_width + 2 * pad_size) * scale_x)
    intermediate_height = int((old_height + 2 * pad_size) * scale_y)
    
    resized_padded = padded_img.resize((intermediate_width, intermediate_height), sample)
    
    crop_left = int(pad_size * scale_x)
    crop_top = int(pad_size * scale_y)
    crop_right = crop_left + new_width
    crop_bottom = crop_top + new_height
    
    result = resized_padded.crop((crop_left, crop_top, crop_right, crop_bottom))
    
    return result

def separate_alpha(img):
    r, g, b, a = img.split()
    rgb = Image.merge("RGB", (r, g, b))
    return rgb, a

def resize_buf(buf, cfg: Cfg, new_sz):
    if cfg.repeat:
        return repeat_sampling_resize(buf, new_sz, cfg.resample)
    else:
        return buf.resize(new_sz, cfg.resample)

def resize_main(img: Image, cfg: Cfg):
    new_sz = getDstSize(img, cfg.size_cfg)
    if not new_sz:
        return img

    if cfg.separate_rgb and img.mode == 'RGBA':
        buf_c, buf_a = separate_alpha(img)
        resized_c = resize_buf(buf_c, cfg, new_sz)
        resized_a = resize_buf(buf_a, cfg, new_sz)

        rr, rg, rb = resized_c.split()
        return Image.merge("RGBA", (rr, rg, rb, resized_a))
    else:
        return resize_buf(img, cfg, new_sz)

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
    outImg = resize_main(img, cfg)

    save_type = cfg.out_type if cfg.out_type else ext
    base = fp.parent / fp.stem
    outFN = f"{base}_resized{save_type}"

    if save_type == '.webp':
        outImg.save(outFN, 'WEBP', quality=85)
    elif save_type == '.avif':
        outImg.save(outFN, 'AVIF', quality=85)
    elif save_type == '.png':
        outImg.save(outFN, 'PNG', optimize=True)

def proc_dir(dir_path: Path, cfg: Cfg):
    for f in dir_path.iterdir():
        if f.is_file():
            proc_img(f, cfg)

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
        if s.startswith('--s:'):
            size_cfg.scale = float(s.split(':')[1])
        elif s.startswith('--w:'):
            size_cfg.width = int(s.split(':')[1])
        elif s.startswith('--h:'):
            size_cfg.height = int(s.split(':')[1])
        elif s.startswith('--b:'):
            size_cfg.max_len = int(s.split(':')[1])
        elif s.startswith('--t:'):
            cfg.outType = '.' + s.split(':')[1]
        elif s == '--repeat':
            cfg.repeat = True
        elif s == '--separate':
            cfg.separate_rgb = True

    for s in files:
        p = Path(s)
        if p.is_dir():
            proc_dir(p, cfg)
        elif p.is_file():
            proc_img(p, cfg)

if __name__ == "__main__":
    main()
