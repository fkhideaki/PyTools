'''
# MakeBat

## 概要
- pythonを起動するbatを作成する機能

## コマンド
- python MakeBat.py [files] [options]
- options:
  - --pause
    - 完了時に待機するバッチファイルを出力する
  - --abs
    - 対象ファイルをフルパスで指定する
    - 未指定時はカレントディレクトリをファイルの親フォルダに移動してファイル名でコマンドを起動
  - --rel
    - 対象ファイルを相対パスで指定する
  - --self
    - 自分自身のbatを作成する
  - --cmd_full
    - pythonの実行コマンドに現在のpythonのフルパスを指定
    - 未指定時にはpython launcherを使う
    - --env
      - 対象ファイルがuvプロジェクト内にある場合、uv runで起動する
      - uvプロジェクトでない場合、対象ファイルと同じフォルダに.venvがあれば、そのpythonで起動する
  - --arg_files
    - 1つ目の引数を対象のpythonファイルとし、2つ目以降をその引数としてbatを作成する
'''

from dataclasses import dataclass
from pathlib import Path
import sys
from enum import Enum

class PathMode(Enum):
    '''パスの指定方法'''

    # 相対パス
    REL = 1

    # 絶対パス
    ABS = 2

    # カレントディレクトリに移動してファイル名で指定
    CUR = 3

@dataclass
class Cfg:
    py_cmd: str = ''
    env: bool = False
    path_mode: PathMode = PathMode.CUR
    pause: bool = False

def is_uv_project(py: Path):
    dir = py.parent
    proj = dir / 'pyproject.toml'
    return proj.is_file()

def contents(py: Path, cfg: Cfg, args: list[str]):
    arg = ' '.join([f'"{s}"' for s in args])

    py_cmd = f'"{cfg.py_cmd}"'
    if cfg.env:
        if is_uv_project(py):
            py_cmd = f'uv run'
        else:
            venv_python = (py.parent / '.venv' / 'Scripts' / 'python.exe').resolve()
            if venv_python.is_file():
                if cfg.path_mode == PathMode.CUR:
                    py_cmd = '.venv\\Scripts\\python.exe'
                elif cfg.path_mode == PathMode.REL:
                    py_cmd = '%~dp0.venv\\Scripts\\python.exe'
                elif cfg.path_mode == PathMode.ABS:
                    py_cmd = f'"{venv_python}"'

    if cfg.path_mode == PathMode.REL:
        yield f'{py_cmd} "%~dp0{py.name}" {arg} %*'
    elif cfg.path_mode == PathMode.ABS:
        yield f'{py_cmd} "{py.resolve()}" {arg} %*'
    elif cfg.path_mode == PathMode.CUR:
        yield f'cd /d "%~dp0"'
        yield f'{py_cmd} "{py.name}" {arg} %*'

    if cfg.pause:
        yield 'pause'

def make_bat(cfg: Cfg, py: str, args: list[str]):
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
    if '--rel' in options:
        cfg.path_mode = PathMode.REL
    elif '--abs' in options:
        cfg.path_mode = PathMode.ABS
    else:
        cfg.path_mode = PathMode.CUR

    cfg.pause = '--pause' in options
    cfg.env = '--env' in options

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
