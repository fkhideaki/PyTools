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
    - 未指定時は対象ファイルをフルパスで指定する
  - --self : 
    - 自分自身のbatを作成する
  - --cmd_full : 
    - pythonの実行コマンドに現在のpythonのフルパスを指定
    - 未指定時にはpython launcherを使う
'''

from pathlib import Path
import sys

def contents(py: Path, py_cmd: str, options: list[str]):
    if '--cd' in options:
        yield f'cd "{py.parent}"'
        yield f'call "{py_cmd}" "{py.name}" %*'
    else:
        yield f'call "{py_cmd}" "{py.resolve()}" %*'

def make_bat(py: Path, py_cmd: str, options: list[str]):
    bn = py.parent / (py.stem + '.bat')
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
        files = [__file__]
    elif '--cmd_full' in options:
        py_cmd = sys.executable

    for a in files:
        make_bat(Path(a), py_cmd, options)

    if '--pause' in options:
        yield 'pause'

if __name__ == "__main__":
    main()
