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


from dataclasses import dataclass
import sys
from pathlib import Path
from PIL import Image
import numpy as np
from scipy import ndimage


@dataclass
class ExpandCfg:
    thickness: int = 1
    passes: int = 1
    save_tmp: bool = False


def expand_by_dilation(alpha, cfg: ExpandCfg):
    """モルフォロジー膨張でアルファチャンネルを拡大"""
    # 構造要素を作成（円形）
    t = cfg.thickness
    y, x = np.ogrid[-t:t + 1, -t:t + 1]
    structure = (x * x + y * y <= t*t)
    
    # 膨張処理
    return ndimage.grey_dilation(alpha, footprint=structure)

def expand_colors_with_alpha(rgb, old_alpha, new_alpha):
    """
    新しいアルファチャンネルに合わせてRGB色を拡張
    元の色情報を周辺に伝播させる
    """
    # 元のアルファが存在する領域のマスク
    mask = old_alpha > 220
    
    # 各チャンネルごとに処理
    result_rgb = np.zeros_like(rgb)
    
    for i in range(3):
        channel = rgb[:, :, i].astype(float)
        
        # 最近傍の色を伝播
        # 距離変換で最も近い有効ピクセルのインデックスを取得
        _, indices = ndimage.distance_transform_edt(
            ~mask, 
            return_indices=True
        )
        
        # インデックスを使って色を伝播
        expanded_channel = channel[indices[0], indices[1]]
        
        # 新しいアルファの領域のみ適用
        result_channel = np.where(new_alpha > 0, expanded_channel, 0)
        result_rgb[:, :, i] = result_channel
    
    return result_rgb

def expand(img: Image, cfg: ExpandCfg):
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    arr = np.array(img)
    
    # RGBとアルファに分離
    rgb = arr[:, :, :3]
    alpha = arr[:, :, 3]

    # モルフォロジー膨張処理
    ext_a = expand_by_dilation(alpha, cfg)
    ext_c = expand_colors_with_alpha(rgb, alpha, ext_a)

    # 結合
    result = np.dstack([ext_c, ext_a])
    return Image.fromarray(result.astype(np.uint8), 'RGBA')

def expand_color(img: Image, cfg: ExpandCfg):
    t = img
    for _ in range(cfg.passes):
        t = expand(t, cfg)
    return t

def test(fp, cfg: ExpandCfg):
    src = Image.open(fp).convert('RGBA')
    _, _, _, am = src.split()
    
    ext = expand_color(src, cfg)
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

    cfg = ExpandCfg(3, 3)
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
            test(p, cfg)

if __name__ == "__main__":
    main()
