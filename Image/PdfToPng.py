"""
## 概要
- PDFファイルの各ページをPNG画像として出力する
- オプションで画像を回転できる

## 依存ライブラリ
- pymupdf

## 使い方:
py PdfToPng.py <入力PDFファイル> [出力先ディレクトリ] [--dpi DPI] [--rot ROT]

## 例
- py pdf_rotate_to_png.py sample.pdf
- py pdf_rotate_to_png.py sample.pdf ./output --dpi 300 --rot 90
  - rotは時計回り
"""

import argparse
import sys
from pathlib import Path

import pymupdf


def rotate_pdf_pages_to_png(pdf_path: str, output_dir: str, dpi: int, rot: int) -> list[str]:
    """
    PDFの各ページを90度時計回りに回転してPNGとして保存する。

    Args:
        pdf_path: 入力PDFファイルのパス
        output_dir: 出力先ディレクトリ（省略時はPDFと同じ場所）
        dpi: レンダリング解像度（デフォルト200）

    Returns:
        生成されたPNGファイルパスのリスト
    """
    pdf_file = Path(pdf_path)
    if not pdf_file.is_file():
        raise FileNotFoundError(f"PDFファイルが見つかりません: {pdf_path}")

    out_dir = Path(output_dir) if output_dir else pdf_file.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"PDFを読み込み中: {pdf_file}")
    doc = pymupdf.open(str(pdf_file))
    print(f"ページ数: {len(doc)}")

    # DPIからズーム倍率を算出（PDFの基準は72dpi）
    zoom = dpi / 72
    matrix = pymupdf.Matrix(zoom, zoom)

    output_paths = []
    for i, page in enumerate(doc, start=1):
        # ページ自体の回転角度に90度（時計回り）を加算してレンダリング
        # PyMuPDFのrotationは時計回りが正の方向
        if rot:
            page.set_rotation((page.rotation + rot) % 360)

        pix = page.get_pixmap(matrix=matrix)
        out_path = out_dir / f"{pdf_file.stem}_page{i:03d}.png"
        pix.save(str(out_path))
        output_paths.append(str(out_path))
        print(f"  保存: {out_path}")

    doc.close()
    return output_paths


def main():
    parser = argparse.ArgumentParser(
        description="PDFの各ページを90度時計回りに回転してPNGとして出力します。"
    )
    parser.add_argument("pdf_path", help="入力PDFファイルのパス")
    parser.add_argument(
        "output_dir", nargs="?", default=None, help="出力先ディレクトリ（省略可）"
    )
    parser.add_argument(
        "--dpi", type=int, default=200, help="出力画像の解像度（デフォルト: 200）"
    )
    parser.add_argument(
        "--rot", type=int, default=0, help="画像の回転(時計回り)"
    )
    args = parser.parse_args()

    try:
        outputs = rotate_pdf_pages_to_png(args.pdf_path, args.output_dir, args.dpi, args.rot)
        print(f"\n完了: {len(outputs)}枚のPNGを出力しました。")
    except Exception as e:
        print(f"エラー: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
