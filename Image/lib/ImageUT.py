from PIL import Image
import numpy as np


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
