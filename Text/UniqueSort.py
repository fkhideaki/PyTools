"""
クリップボードから文字列を取得し、
行ごとにソート＆重複排除して標準出力に表示するスクリプト
"""

import pyperclip


def main():
    text = pyperclip.paste()
    lines = text.splitlines()

    unique_sorted_lines = sorted(set(lines))

    for line in unique_sorted_lines:
        print(line)

    if input('END (Input c to copy clipboard) >>> ').lower() == 'c':
        pyperclip.copy('\n'.join(unique_sorted_lines))

if __name__ == "__main__":
    main()
