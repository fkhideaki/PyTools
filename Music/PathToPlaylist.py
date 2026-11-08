'''
walkman用のプレイリスト編集機能
クリップボードにコピーされたパスをwalkmanのm3u形式に変換して出力する
'''

import re
import pyperclip


# ドライブ文字（任意）＋ 直下の MUSIC フォルダ以降を取り出す
# 例: H:\MUSIC\aaaa\bbbb.mp3 -> aaaa\bbbb.mp3
PATTERN = re.compile(r'^[A-Za-z]:[\\/]+MUSIC[\\/]+(.*)$', re.IGNORECASE)


def convert_line(line: str) -> str:
    """1行を相対パス化し、区切り文字をスラッシュに変換する"""
    line = line.strip().strip('"')  # 前後の空白・引用符を除去
    if not line:
        return ""

    m = PATTERN.match(line)
    if m:
        relative = m.group(1)
    else:
        # MUSIC直下のパスでない場合はそのまま（区切り文字だけ変換）
        relative = line

    return relative.replace("\\", "/")


def main():
    text = pyperclip.paste()
    lines = text.splitlines()

    print('')
    for line in lines:
        print(convert_line(line))

    input('')


if __name__ == "__main__":
    main()
