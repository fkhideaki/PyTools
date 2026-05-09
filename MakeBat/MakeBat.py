'''
# MakeBat

## 概要
- pythonを起動するbatを作成する機能

## コマンド
- python _MakeBat.py [files] [options]
- options:
  - --pause
    - 完了時に待機するバッチファイルを出力する
  - --cd
    - カレントディレクトリをファイルの親フォルダに移動してファイル名でコマンドを起動
    - 未指定時は対象ファイルをフルパスで指定する
  - --self
    - 自分自身のbatを作成する
  - --cmd_full
    - pythonの実行コマンドに現在のpythonのフルパスを指定
    - 未指定時にはpython launcherを使う
  - --arg_files
    - 1つ目の引数を対象のpythonファイルとし、2つ目以降をその引数としてbatを作成する
'''

from dataclasses import dataclass
from pathlib import Path
import sys

@dataclass
class Cfg:
    py_cmd: str = ''
    cd: bool = False
    pause: bool = False

def contents(py: Path, cfg: Cfg, args: list[str]):
    arg = ' '.join([f'"{s}"' for s in args])
    if cfg.cd:
        yield f'cd "{py.parent}"'
        yield f'"{cfg.py_cmd}" "{py.name}" {arg} %*'
    else:
        yield f'"{cfg.py_cmd}" "{py.resolve()}" {arg} %*'
    if cfg.pause:
        yield 'pause'

def make_bat(cfg, py, args):
    p = Path(py)
    bn = p.parent / (p.stem + '.bat')
    with open(bn, mode='w') as f:
        for s in contents(p, cfg, args):
            f.write(s + '\n')

def main():
    options = []
    files = []
    for s in sys.argv[1:]:
        if s.startswith('--'):
            options.append(s)
        else:
            files.append(s)

    cfg = Cfg()
    cfg.cd = '--cd' in options
    cfg.pause = '--pause' in options

    arg_files = '--arg_files' in options
    make_self = '--self' in options
    cmd_full = '--cmd_full' in options

    if cmd_full:
        cfg.py_cmd = sys.executable
    else:
        cfg.py_cmd = 'py'

    if make_self:
        files = [__file__]

    if arg_files:
        if files:
            make_bat(cfg, files[0], files[1:])
    else:
        for f in files:
            make_bat(cfg, f, [])

if __name__ == "__main__":
    main()
