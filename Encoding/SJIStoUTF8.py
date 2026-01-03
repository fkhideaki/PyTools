'''
# SJIStoUTF8.py

## 概要
- Shift-JISで書かれたファイルをUTF-8に変換するツール

## 使い方
- python SJIStoUTF8.py [files] [options]
- options:
  - --useBOM : UTF-8-BOM付きで出力する
  - --overwrite : 入力ファイルを上書きする
'''

import sys
import os

def convertToUTF8(inFile, outFile, useBOM):
    with open(inFile, 'r', encoding='shift_jis') as f:
        content = f.read()

    encoding = 'utf-8-sig' if useBOM else 'utf-8'
    with open(outFile, 'w', encoding=encoding) as f:
        f.write(content)

def mainA():
    options = []
    files = []
    for s in sys.argv[1:]:
        if s.startswith('--'):
            options.append(s)
        else:
            files.append(s)

    useBOM = '--useBOM' in options
    overwrite = '--overwrite' in options
    for a in files:
        print(a)
        if not os.path.isfile(a):
            print('file not exists : ' + a)
            continue
        if overwrite:
            out = a
        else:
            ex = os.path.splitext(a)
            out = ex[0] + '_convert' + ex[1]

        try:
            convertToUTF8(a, out, useBOM)
        except Exception as e:
            print('ERROR : ' + str(e))

if __name__ == '__main__':
    mainA()
