'''
# SetDPI

## 概要
- 指定画像のdpiを設定する

## 使い方
- python SetDPI.py -dpi 100 [画像]
  - 指定画像(複数可)のdpiを指定値に変更した画像を出力する
  - 出力画像は元ファイル名_outという形式で出力される(a.png->a_out.png)
- python SetDPI.py -w 100mm [画像]
  - 指定画像の横幅が指定幅となるようにdpiを変更した画像を出力する
  - 単位はcm、mmに対応
- python SetDPI.py -h 100mm [画像]
  - 指定画像の高さが指定幅となるようにdpiを変更した画像を出力する
'''

import argparse
import os
import re
import sys

from PIL import Image

MM_PER_INCH = 25.4


def parse_length_to_mm(length_str):
    """'100mm' や '10cm' のような文字列をmm単位のfloatに変換する"""
    m = re.fullmatch(r'\s*([0-9]*\.?[0-9]+)\s*(mm|cm)\s*', length_str, re.IGNORECASE)
    if not m:
        raise argparse.ArgumentTypeError(
            f"'{length_str}' は正しい形式ではありません。例: 100mm, 10cm"
        )
    value = float(m.group(1))
    unit = m.group(2).lower()
    if unit == 'cm':
        value *= 10.0
    return value


def make_out_path(path):
    root, ext = os.path.splitext(path)
    return f"{root}_out{ext}"


def build_argparser():
    parser = argparse.ArgumentParser(
        description='指定画像のdpiを設定する',
        add_help=False
    )
    parser.add_argument('--help', action='help', help='ヘルプメッセージを表示して終了')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-dpi', type=float, help='設定するdpi値')
    group.add_argument('-w', type=str, help='目標の横幅 (例: 100mm, 10cm)')
    group.add_argument('-h', type=str, help='目標の高さ (例: 100mm, 10cm)')
    parser.add_argument('images', nargs='+', help='対象画像ファイル(複数可)')
    return parser


def process_image(path, args):
    with Image.open(path) as img:
        width_px, height_px = img.size

        if args.dpi is not None:
            dpi_value = args.dpi
        elif args.w is not None:
            target_mm = parse_length_to_mm(args.w)
            target_inch = target_mm / MM_PER_INCH
            dpi_value = width_px / target_inch
        else:  # args.h
            target_mm = parse_length_to_mm(args.h)
            target_inch = target_mm / MM_PER_INCH
            dpi_value = height_px / target_inch

        out_path = make_out_path(path)
        save_kwargs = {}
        if img.info:
            save_kwargs.update({k: v for k, v in img.info.items() if k != 'dpi'})
        save_kwargs['dpi'] = (dpi_value, dpi_value)

        img.save(out_path, **save_kwargs)
        print(f"{path} -> {out_path} (dpi={dpi_value:.2f})")


def main():
    parser = build_argparser()
    args = parser.parse_args()

    # -dpi, -w, -h のいずれも指定されていない場合は処理を開始しない
    if args.dpi is None and args.w is None and args.h is None:
        parser.error('-dpi, -w, -h のいずれか一つを指定してください。')

    for path in args.images:
        if not os.path.isfile(path):
            print(f"警告: ファイルが見つかりません: {path}", file=sys.stderr)
            continue
        try:
            process_image(path, args)
        except Exception as e:
            print(f"エラー: {path} の処理に失敗しました ({e})", file=sys.stderr)


if __name__ == '__main__':
    main()
