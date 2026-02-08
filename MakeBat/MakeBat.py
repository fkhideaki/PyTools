'''
# MakeBat

## 概要
- pythonを起動するbatを作成する機能

## コマンド
- python _MakeBat.py [files] [options]
- options:
  - --pause : 
    - 完了時に待機する
  - --cd : 
    - カレントディレクトリをファイルの親フォルダに移動してファイル名でコマンドを起動
  - --self : 
    - 自分自身のbatを作成する
  - --cmd_full : 
    - pythonの実行コマンドに現在のpythonのフルパスを指定
    - 未指定時にはpython launcherを使う
'''

import os
import sys

def contents(py: str, py_cmd: str, options: list[str]):
    if '--cd' in options:
        cdPath = os.path.dirname(py)
        pyName = os.path.basename(py)
        yield f'cd "{cdPath}" %*'
        yield f'call "{py_cmd}" "{pyName}" %*'
    else:
        yield f'call "{py_cmd}" "{py}" %*'
    if '--pause' in options:
        yield 'pause'

def make_bat(py: str, py_cmd: str, options: list[str]):
    ext = os.path.splitext(py)[-1]
    bn = py[0:-len(ext)] + '.bat'
    with open(bn, mode='w') as f:
        for s in contents(py, py_cmd, options):
            f.write(s + '\n')

def main():
    options = []
    files = []
    for s in sys.argv[1:]:
        if s.startswith('--'):
            options.append(s)
        else:
            files.append(s)

    py_cmd = 'py'
    if '--self' in options:
        my_file = os.path.abspath(__file__)
        files = [my_file]
    elif '--cmd_full' in options:
        py_cmd = sys.executable

    for a in files:
        make_bat(a, py_cmd, options)

if __name__ == "__main__":
    main()
