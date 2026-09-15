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

from enum import Enum
import sys
from pathlib import Path

class CompareResult(Enum):
    SAME = 0
    FILE1_LARGER = 1
    FILE2_LARGER = 2
    FILE1_NOT_EXIST = 3
    FILE2_NOT_EXIST = 4
    CONTENT_DIFFERENT = 5

def ret_error(msg):
    print(msg)
    input('>>>')
    sys.exit(1)

def ret_result(msg):
    print(msg)
    input('>>>')
    sys.exit(0)

def compare_files(file1, file2) -> CompareResult:
    print(f'file1 : {file1}')
    print(f'file2 : {file2}')
    print(f'')

    if not file1.is_file():
        return CompareResult.FILE1_NOT_EXIST

    if not file2.is_file():
        return CompareResult.FILE2_NOT_EXIST

    size1 = file1.stat().st_size
    size2 = file2.stat().st_size

    if size1 > size2:
        return CompareResult.FILE1_LARGER
    if size1 < size2:
        return CompareResult.FILE2_LARGER

    with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
        if not f1.read() == f2.read():
            return CompareResult.CONTENT_DIFFERENT

    return CompareResult.SAME

def main():
    if len(sys.argv) != 3:
        print("Usage: py FileDiff.py [file1] [file2]")
        sys.exit(1)

    file1 = Path(sys.argv[1])
    file2 = Path(sys.argv[2])

    result = compare_files(file1, file2)
    if result == CompareResult.FILE1_LARGER:
        ret_result("file1 のほうが大きいです。")
    elif result == CompareResult.FILE2_LARGER:
        ret_result("file2 のほうが大きいです。")
    elif result == CompareResult.FILE1_NOT_EXIST:
        ret_result("file1 が存在しないか、ファイルではありません。")
    elif result == CompareResult.FILE2_NOT_EXIST:
        ret_result("file2 が存在しないか、ファイルではありません。")
    elif result == CompareResult.CONTENT_DIFFERENT:
        ret_result("サイズが同じですが、内容が異なります。")
    else:
        ret_result("完全に同じです。")

if __name__ == "__main__":
    main()
