from dataclasses import dataclass, field
from pathlib import Path
from typing import Self
from PIL import Image, ImageChops
import numpy as np
from scipy import ndimage


@dataclass
class TargetSize:
    scale: float | None = None
    width: int | None = None
    height: int | None = None
    max_len: int | None = None

    def get_dst_size(self, img: Image):
        scale = self.scale
        width = self.width
        height = self.height
        max_len = self.max_len

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


@dataclass
class ResizeCfg:
    repeat: bool = False
    separate_rgb: bool = False
    target_size: TargetSize = field(default_factory=TargetSize)
    resample = Image.Resampling.BILINEAR


class ImageResizeExt:
    '''画像リサイズの拡張ユーティリティ'''

    @classmethod
    def resize(cls, img: Image, cfg: ResizeCfg):
        new_sz = cfg.target_size.get_dst_size(img)
        if not new_sz:
            return img

        if cfg.separate_rgb and img.mode == 'RGBA':
            buf_c, buf_a = cls._separate_alpha(img)
            resized_c = cls._resize_buf(buf_c, cfg, new_sz)
            resized_a = cls._resize_buf(buf_a, cfg, new_sz)

            rr, rg, rb = resized_c.split()
            return Image.merge("RGBA", (rr, rg, rb, resized_a))
        else:
            return cls._resize_buf(img, cfg, new_sz)

    @classmethod
    def _separate_alpha(cls, img):
        r, g, b, a = img.split()
        rgb = Image.merge("RGB", (r, g, b))
        return rgb, a

    @classmethod
    def _resize_buf(cls, buf, cfg: ResizeCfg, new_sz):
        if cfg.repeat:
            return cls.repeat_sampling_resize(buf, new_sz, cfg.resample)
        else:
            return buf.resize(new_sz, cfg.resample)

    @classmethod
    def repeat_sampling_resize(cls, img, new_sz, sample):
        arr = np.array(img)
        
        pad_size = 4
        if arr.ndim == 2:
            padded = np.pad(arr, pad_size, mode='wrap')
            mode = 'L'
        else:
            padded = np.pad(arr, ((pad_size, pad_size), (pad_size, pad_size), (0, 0)), mode='wrap')
            mode = img.mode
        
        padded_img = Image.fromarray(padded.astype(np.uint8), mode=mode)
        
        old_w, old_h = img.size
        new_w, new_h = new_sz
        
        scale_x = new_w / old_w
        scale_y = new_h / old_h
        
        sxw = int((old_w + 2 * pad_size) * scale_x)
        sxh = int((old_h + 2 * pad_size) * scale_y)
        intermediate_sz = (sxw, sxh)
        resized_padded = padded_img.resize(intermediate_sz, sample)
        
        crop_l = int(pad_size * scale_x)
        crop_t = int(pad_size * scale_y)
        crop_r = crop_l + new_w
        crop_b = crop_t + new_h
        return resized_padded.crop((crop_l, crop_t, crop_r, crop_b))


class Alphamap:
    '''アルファマップ関連機能'''

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


class ImgRepeat:
    @classmethod
    def repeat2x(cls, img: Image) -> Image:
        '''
        - 指定された画像を長辺方向に2倍、短辺方向に出来るだけ正方形に近くなる回数リピートさせた画像を返す
        - 例えば500x300が入力された場合、横方向に2倍、縦方向に3倍リピートさせた1000x900の画像を返す
        - ただし、長辺 / 短辺 が2.0倍以上であれば長辺方向にはリピートしない
        '''
        w, h = img.size
        repeat_long = 2
        whr = w / h
        if whr < (1.0 / 2.0) or whr > 2.0:
            repeat_long = 1
        if w > h:
            repeat_w = repeat_long
            repeat_h = (w * repeat_w) // h
        else:
            repeat_h = repeat_long
            repeat_w = (h * repeat_h) // w
        new_w = w * repeat_w
        new_h = h * repeat_h
        new_img = Image.new(img.mode, (new_w, new_h))
        for i in range(repeat_w):
            for j in range(repeat_h):
                new_img.paste(img, (i * w, j * h))
        return new_img

    @classmethod
    def make_halfstep_repeat(cls, img: Image, to_vert: bool) -> Image:
        '''\
        - 指定画像をハーフステップリピート画像の1リピート単位に変換する
        - to_vert: Trueを指定すると縦に2倍にして半周期ずらす、Falseを指定すると横に
        '''
        w, h = img.size

        if to_vert:
            # 下段: 横方向に半周期ずらす(ImageChops.offset は端が回り込む)
            shifted = ImageChops.offset(img, w // 2, 0)
            out = Image.new(img.mode, (w, h * 2))
            out.paste(img, (0, 0))
            out.paste(shifted, (0, h))
        else:
            # 右段: 縦方向に半周期ずらす
            shifted = ImageChops.offset(img, 0, h // 2)
            out = Image.new(img.mode, (w * 2, h))
            out.paste(img, (0, 0))
            out.paste(shifted, (w, 0))

        # パレット画像などの情報を引き継ぐ
        if img.mode == "P" and img.getpalette():
            out.putpalette(img.getpalette())
        return out


@dataclass
class AlphaExpandCfg:
    thickness: int = 1
    passes: int = 1
    color_only: bool = False
    save_tmp: bool = False


class AlphaExpand:
    '''アルファチャンネル膨張と色拡張のユーティリティ'''

    @classmethod
    def expand(cls, img: Image, cfg: AlphaExpandCfg):
        if not cfg.color_only:
            return cls._expand_main(img, cfg)
        else:
            arr1 = np.array(img)
            alpha = arr1[:, :, 3]

            t = cls._expand_main(img, cfg)
            arr2 = np.array(t)
            ext_c = arr2[:, :, :3]

            b = np.dstack([ext_c, alpha])
            return Image.fromarray(b.astype(np.uint8), 'RGBA')

    @classmethod
    def _expand_main(cls, img: Image, cfg: AlphaExpandCfg):
        t = img
        for _ in range(cfg.passes):
            t = cls._expand_iter(t, cfg)
        return t
    
    @classmethod
    def _expand_iter(cls, img: Image, cfg: AlphaExpandCfg):
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        arr = np.array(img)
        rgb = arr[:, :, :3]
        alpha = arr[:, :, 3]

        # モルフォロジー膨張処理
        ext_a = cls._expand_by_dilation(alpha, cfg)
        ext_c = cls._expand_colors_with_alpha(rgb, alpha, ext_a)

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


class FilesOperator:
    '''ファイルまたはディレクトリのリストを受け取り、ファイルを反復処理するユーティリティ'''

    def __init__(self, path_list: list[Path]):
        self.path_list = path_list

    @classmethod
    def from_strs(self, path_list: list[str]):
        v = [Path(s) for s in path_list]
        return FilesOperator(v)
    
    def iterate(self):
        for p in self.path_list:
            if p.is_dir():
                for f in p.iterdir():
                    if f.is_file():
                        yield f
            elif p.is_file():
                yield p
