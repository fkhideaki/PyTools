'''\
## 概要
- 指定されたフォルダがVSCodeのpython用ワークスペースである前提で、python用のlaunch.jsonを生成する
'''


from pathlib import Path
import sys


def make_launch(dir: Path):
    '''\
    指定フォルダにlaunch.jsonを生成
    - 既に存在している場合は何もしない
    '''
    launch_file = dir / '.vscode' / 'launch.json'
    if launch_file.exists():
        input(f'launch.jsonは既に存在します: {launch_file}')
        return

    vscode_dir = dir / '.vscode'
    if not vscode_dir.exists():
        vscode_dir.mkdir(parents=True)

    with open(launch_file, 'w', encoding='utf-8') as f:
        f.write('''\
{
    // IntelliSense を使用して利用可能な属性を学べます。
    // 既存の属性の説明をホバーして表示します。
    // 詳細情報は次を確認してください: https://go.microsoft.com/fwlink/?linkid=830387
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python With args",
            "type": "debugpy",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "args": [""]
        },
        {
            "name": "Python pickArgs",
            "type": "debugpy",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "args": "${command:pickArgs}"
        }
    ]
}
''')

def main():
    for arg in sys.argv[1:]:
        dir = Path(arg)
        if not dir.exists():
            print(f'指定されたフォルダが存在しません: {dir}')
            continue
        make_launch(dir)

if __name__ == '__main__':
    main()
