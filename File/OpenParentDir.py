'''
引数に受け取ったファイルの親フォルダをエクスプローラで開く

フォルダが指定された場合はそれ自体をエクスプローラで開く
'''

from pathlib import Path
import subprocess
import sys


def main():
    if len(sys.argv) < 2:
        print('Usage: python OpenParentDir.py <file_path>')
        sys.exit(1)

    arg = sys.argv[1]
    path = Path(arg)

    if path.is_file():
        dir = path.parent
    elif path.is_dir():
        dir = path
    else:
        print(f'Error: The specified path does not exist: {path}')
        sys.exit(1)

    subprocess.run(['explorer', dir])


if __name__ == '__main__':
    main()
