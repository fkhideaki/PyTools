'''
VisualStudioのキャッシュファイルをクリアする
'''

import os
import re
import shutil
from pathlib import Path
from typing import List

def getWinTmpDir() -> str:
    return Path(os.environ['LOCALAPPDATA']) / 'Temp'

def getSubitemInDir(dir: Path, regex: str, isDir: bool):
    pattern = re.compile(regex)
    a = []

    for item in dir.iterdir():
        if isDir:
            if not item.is_dir():
                continue
        else:
            if not item.is_file():
                continue

        if pattern.search(item.name):
            a.append(str(item))

    return a

def getTmpFiles() -> List[str]:
    regex = r'_CL_([0-9a-z]+)'
    temp_dir = getWinTmpDir()
    return getSubitemInDir(temp_dir, regex, isDir=False)

def getTmpDirs() -> List[str]:
    regex = r'([0-9]+)_analysis'
    temp_dir = getWinTmpDir()
    return getSubitemInDir(temp_dir, regex, isDir=True)

def delFiles(files: List[str]) -> None:
    for file_path in files:
        os.remove(file_path)

def delDirs(dirs: List[str]) -> None:
    for dir_path in dirs:
        shutil.rmtree(dir_path)

def procFiles():
    tmps = getTmpFiles()
    num = len(tmps)
    if num == 0:
        input('no tmp files >>> ')
        return
    req = input(f'{num} tmp files delete (t/f) >>> ')
    if req != 't':
        print('canceled')
        return

    delFiles(tmps)

def procDirs():
    tmps = getTmpDirs()
    num = len(tmps)
    if num == 0:
        input('no tmp dirs >>> ')
        return
    req = input(f'{num} tmp dirs delete (t/f) >>> ')
    if req != 't':
        print('canceled')
        return

    delDirs(tmps)

def main():
    try:
        procFiles()
        procDirs()
        input('end >>> ')
    except Exception as e:
        input(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    main()
