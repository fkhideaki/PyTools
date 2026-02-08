'''
# MakeBat

## 概要
- pythonを起動するbatを作成する機能

## コマンド
- python _MakeBat.py [files] [options]
- options:
  - --pause : 
    - 完了時に待機するバッチファイルを出力する
  - --cd : 
    - カレントディレクトリをファイルの親フォルダに移動してファイル名でコマンドを起動
    - 未指定時は対象ファイルをフルパスで指定する
  - --self : 
    - 自分自身のbatを作成する
  - --cmd_full : 
    - pythonの実行コマンドに現在のpythonのフルパスを指定
    - 未指定時にはpython launcherを使う
'''

from dataclasses import dataclass
from pathlib import Path
import sys

@dataclass
class Cfg:
    py_cmd: str = ''
    cd: bool = False
    pause: bool = False

def make_bat(py: Path, cfg: Cfg):
    if cfg.cd:
        yield f'cd "{py.parent}"'
        yield f'call "{cfg.py_cmd}" "{py.name}" %*'
    else:
        yield f'call "{cfg.py_cmd}" "{py.resolve()}" %*'
    if cfg.pause:
        yield 'pause'

def main():
    options = []
    files = []
    for s in sys.argv[1:]:
        if s.startswith('--'):
            options.append(s)
        else:
            files.append(s)

    cfg = Cfg()
    cfg.py_cmd = 'py'
    for s in options:
        if s == '--cd':
            cfg.cd = True
        elif s == '--self':
            files = [__file__]
        elif s == '--cmd_full':
            cfg.py_cmd = sys.executable
        elif s == '--pause':
            cfg.pause = True

    for a in files:
        py = Path(a)
        bn = py.parent / (py.stem + '.bat')
        with open(bn, mode='w') as f:
            for s in make_bat(py, cfg):
                f.write(s + '\n')

if __name__ == "__main__":
    main()
