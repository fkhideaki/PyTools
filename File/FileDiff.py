'''
## 概要
- 2ファイルを比較する
- 2ファイルを比較し、下記いずれかの状態を出力に表示する
  - 2ファイルが完全に同じ
  - file1のほうが大きい
  - file2のほうが大きい
  - ファイルサイズが同じだが内容が異なる

## コマンドライン
- py FileDiff.py [file1] [file2]
'''

import sys
from pathlib import Path

def ret_error(msg):
    print(msg)
    input('>>>')
    sys.exit(1)

def ret_result(msg):
    print(msg)
    input('>>>')
    sys.exit(0)

def compare_files(file1, file2):
    print(f'file1 : {file1}')
    print(f'file2 : {file2}')
    print(f'')

    if not file1.is_file():
        ret_error("file1 が存在しないか、ファイルではありません。")

    if not file2.is_file():
        ret_error("file2 が存在しないか、ファイルではありません。")

    size1 = file1.stat().st_size
    size2 = file2.stat().st_size

    if size1 > size2:
        ret_result(f"file1 のほうが大きいです。")
    if size1 < size2:
        ret_result(f"file2 のほうが大きいです。")

    with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
        if not f1.read() == f2.read():
            ret_result("サイズが同じですが、内容が異なります。")

        ret_result("完全に同じです。")

def main():
    if len(sys.argv) != 3:
        print("Usage: py FileDiff.py [file1] [file2]")
        sys.exit(1)

    file1 = Path(sys.argv[1])
    file2 = Path(sys.argv[2])

    compare_files(file1, file2)

if __name__ == "__main__":
    main()
