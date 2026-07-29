'''
pythonの仮想環境のセットアップスクリプト
- venvを作成し、requirements.txtの内容をインストールする
'''

import os
from pathlib import Path
import subprocess
import venv

VENV_DIR = ".venv"


def get_venv_python() -> Path:
    """venv内のpython実行パスをOSに応じて返す"""
    if os.name == "nt":  # Windows
        return Path(VENV_DIR) / "Scripts" / "python.exe"
    else:  # macOS/Linux
        return Path(VENV_DIR) / "bin" / "python"


def ensure_venv():
    """venvが存在すればそれを使い、なければ新規作成する"""
    if Path(VENV_DIR).exists() and get_venv_python().exists():
        print(f"既存の仮想環境を使用します: {VENV_DIR}")
    else:
        print("仮想環境を作成中...")
        venv.create(VENV_DIR, with_pip=True)


def upgrade_pip(venv_python):
    """pipを最新版にアップグレード"""
    print("pipをアップグレード中...")
    subprocess.run(
        [venv_python, "-m", "ensurepip", "--upgrade"],
        check=True
    )


def install_requirements(venv_python):
    """requirements.txtの内容をインストール"""
    print("ライブラリをインストール中...")
    subprocess.run(
        [venv_python, "-m", "pip", "install", "-r", "requirements.txt"],
        check=True
    )


def main():
    ensure_venv()
    venv_python = get_venv_python()

    try:
        upgrade_pip(venv_python)
    except Exception as e:
        print('Failed upgrade pip')
        return

    if Path('requirements.txt').is_file():
        try:
            install_requirements(venv_python)
        except Exception as e:
            print('Failed install requirements')
            return

    print("セットアップ完了")


if __name__ == "__main__":
    main()
