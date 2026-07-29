'''
pythonの仮想環境のセットアップスクリプト
- venvを作成し、requirements.txtの内容をインストールする
'''

import os
import subprocess
import sys
import venv

VENV_DIR = ".venv"


def get_venv_python():
    """venv内のpython実行パスをOSに応じて返す"""
    if os.name == "nt":  # Windows
        return os.path.join(VENV_DIR, "Scripts", "python.exe")
    else:  # macOS/Linux
        return os.path.join(VENV_DIR, "bin", "python")


def ensure_venv():
    """venvが存在すればそれを使い、なければ新規作成する"""
    if os.path.exists(VENV_DIR) and os.path.exists(get_venv_python()):
        print(f"既存の仮想環境を使用します: {VENV_DIR}")
    else:
        print("仮想環境を作成中...")
        venv.create(VENV_DIR, with_pip=True)


def upgrade_pip(venv_python):
    """pipを最新版にアップグレード"""
    print("pipをアップグレード中...")
    subprocess.run(
        [venv_python, "-m", "pip", "install", "--upgrade", "pip"],
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

    upgrade_pip(venv_python)
    install_requirements(venv_python)

    print("セットアップ完了")


if __name__ == "__main__":
    main()
