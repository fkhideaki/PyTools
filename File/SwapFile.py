'''
ファイルを入れ替える機能

## 概要
- 指定した2つのファイルを入れ替える
- 3つのモードがある
  - コマンドライン引数で指定した2つのファイルを入れ替える
  - コマンドライン引数で指定した2つのファイルを入れ替えるバッチファイルを作成する
  - クリップボードにコピーした2つのファイルを入れ替える

## 使い方
- py SwapFile.py file0 file1
  - コマンドライン引数で指定した2つのファイルを入れ替える
- py SwapFile.py --bat file0 file1
  - コマンドライン引数で指定した2つのファイルを入れ替えるバッチファイルを作成する
- py SwapFile.py --clip
  - クリップボードにコピーした2つのファイルを入れ替える
'''


from pathlib import Path
import sys
import os
import pyperclip
import random, string
import win32clipboard
import win32con

def getRandom(n):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=n))

def getTmpfile(f):
    for i in range(10):
        rk = '_TMP_' + getRandom(10)
        t = f + rk
        if not os.path.exists(t):
            return t
    return None

def swapFile(f0, f1):
    f0t = getTmpfile(f0)
    if not f0t:
        print('Failed to get tmp file path')
        input('[ERR] >>>')
        return

    os.rename(f0, f0t)
    os.rename(f1, f0)
    os.rename(f0t, f1)
    print(f'''
Swap:
  {f0}
  ↑↓
  {f1}
'''[1:])

def getClipboardFilesExplorer():
    win32clipboard.OpenClipboard()
    try:
        if win32clipboard.IsClipboardFormatAvailable(win32con.CF_HDROP):
            data = win32clipboard.GetClipboardData(win32con.CF_HDROP)
            return list(data)
        else:
            return []
    finally:
        win32clipboard.CloseClipboard()

def getClipboardFiles():
    sv = getClipboardFilesExplorer()
    if len(sv) == 2:
        return sv
    s = pyperclip.paste()
    sv2 = s.splitlines()
    if len(sv2) == 2:
        return sv2
    return []

def makeBat(f0, f1):
    p0 = Path(f0)
    p1 = Path(f1)
    fn = p0.parent / f'{p0.stem}_swap_{p1.stem}.bat'
    mypath = Path(__file__).resolve()
    with open(fn, mode="w") as f:
        f.write(f'''\
py "{mypath}" "{f0}" "{f1}"
''')

def remDQ(s):
    if len(s) < 2:
        return s
    if s[0] == '"' and s[-1] == '"':
        return s[1:-1]
    return s

def swapFileClip():
    sv = getClipboardFiles()
    if len(sv) < 2:
        print('Invalid clipboard')
        return

    f0 = remDQ(sv[0])
    f1 = remDQ(sv[1])
    swapFile(f0, f1)

def main():
    if len(sys.argv) == 2:
        if sys.argv[1] == '--clip':
            swapFileClip()
            return

    if len(sys.argv) == 4:
        if sys.argv[1] == '--bat':
            makeBat(sys.argv[2], sys.argv[3])
            return

    if len(sys.argv) == 3:
        swapFile(sys.argv[1], sys.argv[2])
        return

    print('Invalid args')


if __name__ == "__main__":
    main()
