from dataclasses import dataclass
from PIL import Image
import numpy as np
from scipy import ndimage


class Alphamap:
    @classmethod
    def separate(cls, img: Image):
        arr = np.array(img)
        
        color_arr = arr.copy()
        color_arr[:, :, 3] = 255
        color_img = Image.fromarray(color_arr)
        
        alpha_arr = np.zeros_like(arr)
        alpha_arr[:, :, :3] = arr[:, :, 3:4]
        alpha_arr[:, :, 3] = 255
        alpha_img = Image.fromarray(alpha_arr)

        return color_img, alpha_img

    @classmethod
    def combine(cls, img: Image, alphamap: Image):
        if img.size != alphamap.size:
            print(f"Error: Image size {img.size} and Alpha map size {alphamap.size} do not match.")
            return None

        ary_col = np.array(img)
        ary_a = np.array(alphamap)

        ary_dst = np.zeros_like(ary_col)
        ary_dst[:, :, :3] = ary_col[:, :, :3]
        ary_dst[:, :, 3] = ary_a[:, :, 0]
        img_dst = Image.fromarray(ary_dst)
        return img_dst


@dataclass
class AlphaExpandCfg:
    thickness: int = 1
    passes: int = 1
    save_tmp: bool = False


class AlphaExpand:
    @classmethod
    def _expand(cls, img: Image, cfg: AlphaExpandCfg):
        t = img
        for _ in range(cfg.passes):
            t = cls._expand(t, cfg)
        return t
    
    @classmethod
    def _expand(cls, img: Image, cfg: AlphaExpandCfg):
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        arr = np.array(img)
        
        # RGBとアルファに分離
        rgb = arr[:, :, :3]
        alpha = arr[:, :, 3]

        # モルフォロジー膨張処理
        ext_a = cls._expand_by_dilation(alpha, cfg)
        ext_c = cls._expand_colors_with_alpha(rgb, alpha, ext_a)

        # 結合
        result = np.dstack([ext_c, ext_a])
        return Image.fromarray(result.astype(np.uint8), 'RGBA')

    @classmethod
    def _expand_by_dilation(cls, alpha, cfg: AlphaExpandCfg):
        """モルフォロジー膨張でアルファチャンネルを拡大"""
        # 構造要素を作成（円形）
        t = cfg.thickness
        y, x = np.ogrid[-t:t + 1, -t:t + 1]
        structure = (x * x + y * y <= t*t)
        
        # 膨張処理
        return ndimage.grey_dilation(alpha, footprint=structure)

    @classmethod
    def _expand_colors_with_alpha(cls, rgb, old_alpha, new_alpha):
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
