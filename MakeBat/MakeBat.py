'''
# MakeBat

## 概要
- pythonを起動するbatを作成する機能

## コマンド
- python _MakeBat.py [files] [options]
- options:
  - --pause : 完了時に待機する
  - --cd : カレントディレクトリをファイルの親フォルダに移動してファイル名でコマンドを起動
  - --self : 自分自身のbatを作成する
'''

import os
import sys

python = sys.executable
myFile = os.path.abspath(__file__)

def contents(py: str, options: list[str]):
    if '--cd' in options:
        cdPath = os.path.dirname(py)
        pyName = os.path.basename(py)
        yield f'cd "{cdPath}" %*'
        yield f'call "{python}" "{pyName}" %*'
    else:
        yield f'call "{python}" "{py}" %*'
    if '--pause' in options:
        yield 'pause'

def makeBat(py: str, options: list[str]):
    ext = os.path.splitext(py)[-1]
    bn = py[0:-len(ext)] + '.bat'
    with open(bn, mode='w') as f:
        for s in contents(py, options):
            f.write(s + '\n')

def mainA():
    options = []
    files = []
    for s in sys.argv[1:]:
        if s.startswith('--'):
            options.append(s)
        else:
            files.append(s)

    if '--self' in options:
        files = [myFile]

    for a in files:
        makeBat(a, options)

if __name__ == "__main__":
    mainA()
