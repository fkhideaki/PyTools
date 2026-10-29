'''
クリップボード内のパス一覧を整形して再度クリップボードに適用する
Windowsのファイルコピー式のクリップボード、プレーンテキスト両方に対応

## options
--n : ファイル名のみを出力する
--p : printのみ行い、クリップボードへの適用は行わない
'''

from pathlib import Path
import sys

import pyperclip
import win32clipboard
import win32con


def getClipboardFiles():
    win32clipboard.OpenClipboard()
    try:
        if win32clipboard.IsClipboardFormatAvailable(win32con.CF_HDROP):
            data = win32clipboard.GetClipboardData(win32con.CF_HDROP)
            return list(data)
        else:
            return []
    finally:
        win32clipboard.CloseClipboard()

def getRaw():
    files = []
    pf = pyperclip.paste().splitlines()
    for s in pf:
        if s[0] == '"' and s[-1] == '"':
            f = s[1:-1]
        else:
            f = s
        files.append(f)
    return files

def getFiles():
    files = getClipboardFiles()
    files += getRaw()
    return files

def main():
    opt = [a for a in sys.argv[1:] if a.startswith('--')]
    name_only = '--n' in opt
    print_mode = '--p' in opt

    files = getFiles()
    dst = []
    for s in files:
        p = Path(s)
        if name_only:
            dst.append(p.name)
        else:
            dst.append(s)
    s = '\n'.join(dst)
    if print_mode:
        print(s)
    else:
        pyperclip.copy(s)


if __name__ == "__main__":
    main()
