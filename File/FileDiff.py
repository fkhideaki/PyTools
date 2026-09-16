'''
## 概要
- 2ファイルを比較する
- 2ファイルを比較し、下記いずれかの状態を出力に表示する
  - 2ファイルが完全に同じ
  - file1のほうが大きい
  - file2のほうが大きい
  - ファイルサイズが同じだが内容が異なる

## コマンドライン
- py FileDiff.py [file1] [file2]
  - 指定された2つのファイルを比較する
- py FileDiff.py --gui
  - GUIでファイルを比較する
'''

from enum import Enum
import sys
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD


class CompareResult(Enum):
    SAME = 0
    SAME_FILE = 1
    FILE1_LARGER = 2
    FILE2_LARGER = 3
    FILE1_NOT_EXIST = 4
    FILE2_NOT_EXIST = 5
    CONTENT_DIFFERENT = 6

def ret_error(msg):
    print(msg)
    input('>>>')
    sys.exit(1)

def ret_result(msg):
    print(msg)
    input('>>>')
    sys.exit(0)

def compare_files(file1, file2) -> CompareResult:
    if file1.resolve() == file2.resolve():
        return CompareResult.SAME_FILE

    if not file1.is_file():
        return CompareResult.FILE1_NOT_EXIST

    if not file2.is_file():
        return CompareResult.FILE2_NOT_EXIST

    size1 = file1.stat().st_size
    size2 = file2.stat().st_size

    if size1 > size2:
        return CompareResult.FILE1_LARGER
    if size1 < size2:
        return CompareResult.FILE2_LARGER

    with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
        if not f1.read() == f2.read():
            return CompareResult.CONTENT_DIFFERENT

    return CompareResult.SAME

def gui_main():
    '''\
    GUIモードでのメイン処理
    - 比較する2ファイルを指定するインタフェース
      - ファイルパス入力テキストボックス＋参照ボタン
      - 各テキストボックスはファイルドロップでも指定可能
    - 比較ボタン
    - 比較ボタンを押すとその下に結果を表示する
    '''
    def compare():
        file1 = Path(entry_file1.get())
        file2 = Path(entry_file2.get())
        result = compare_files(file1, file2)
        if result == CompareResult.SAME_FILE:
            result_label.config(text="同じファイルです。")
        elif result == CompareResult.FILE1_LARGER:
            result_label.config(text="file1 のほうが大きいです。")
        elif result == CompareResult.FILE2_LARGER:
            result_label.config(text="file2 のほうが大きいです。")
        elif result == CompareResult.FILE1_NOT_EXIST:
            result_label.config(text="file1 が存在しないか、ファイルではありません。")
        elif result == CompareResult.FILE2_NOT_EXIST:
            result_label.config(text="file2 が存在しないか、ファイルではありません。")
        elif result == CompareResult.CONTENT_DIFFERENT:
            result_label.config(text="サイズが同じですが、内容が異なります。")
        else:
            result_label.config(text="完全に同じです。")

    def clear_result():
        result_label.config(text="")

    def select_file(entry):
        file_path = filedialog.askopenfilename()
        entry.delete(0, tk.END)
        entry.insert(0, file_path)
        clear_result()

    def on_drop(event, entry):
        dropped_files = root.tk.splitlist(event.data)
        if len(dropped_files) == 1:
            entry.delete(0, tk.END)
            entry.insert(0, dropped_files[0])
            clear_result()
        elif len(dropped_files) == 2:
            entry_file1.delete(0, tk.END)
            entry_file1.insert(0, dropped_files[0])
            entry_file2.delete(0, tk.END)
            entry_file2.insert(0, dropped_files[1])
            clear_result()

    root = TkinterDnD.Tk()
    root.title("File Diff")

    tk.Label(root, text="File 1:").grid(row=0, column=0, padx=5, pady=5)
    entry_file1 = tk.Entry(root, width=100)
    entry_file1.grid(row=0, column=1, padx=5, pady=5)
    tk.Button(root, text="参照", command=lambda: select_file(entry_file1)).grid(row=0, column=2, padx=5, pady=5)
    # ファイルドロップに対応
    entry_file1.drop_target_register(DND_FILES)
    entry_file1.dnd_bind('<<Drop>>', lambda e: on_drop(e, entry_file1))

    tk.Label(root, text="File 2:").grid(row=1, column=0, padx=5, pady=5)
    entry_file2 = tk.Entry(root, width=100)
    entry_file2.grid(row=1, column=1, padx=5, pady=5)
    tk.Button(root, text="参照", command=lambda: select_file(entry_file2)).grid(row=1, column=2, padx=5, pady=5)
    # ファイルドロップに対応
    entry_file2.drop_target_register(DND_FILES)
    entry_file2.dnd_bind('<<Drop>>', lambda e: on_drop(e, entry_file2))

    tk.Button(root, text="比較", command=compare).grid(row=2, column=1, padx=5, pady=10)

    # 結果表示GUI
    result_label = tk.Label(root, text="", fg="blue")
    result_label.grid(row=3, column=0, columnspan=3, padx=5, pady=5)

    root.mainloop()

def main():
    gui_mode = False
    if len(sys.argv) == 2 and sys.argv[1] == '--gui':
        gui_mode = True

    if gui_mode:
        gui_main()
        return

    if len(sys.argv) != 3:
        print("Usage: py FileDiff.py [file1] [file2]")
        sys.exit(1)

    file1 = Path(sys.argv[1])
    file2 = Path(sys.argv[2])

    print(f'file1 : {file1}')
    print(f'file2 : {file2}')
    print(f'')

    result = compare_files(file1, file2)
    if result == CompareResult.SAME_FILE:
        ret_result("同じファイルです。")
    elif result == CompareResult.FILE1_LARGER:
        ret_result("file1 のほうが大きいです。")
    elif result == CompareResult.FILE2_LARGER:
        ret_result("file2 のほうが大きいです。")
    elif result == CompareResult.FILE1_NOT_EXIST:
        ret_result("file1 が存在しないか、ファイルではありません。")
    elif result == CompareResult.FILE2_NOT_EXIST:
        ret_result("file2 が存在しないか、ファイルではありません。")
    elif result == CompareResult.CONTENT_DIFFERENT:
        ret_result("サイズが同じですが、内容が異なります。")
    else:
        ret_result("完全に同じです。")

if __name__ == "__main__":
    main()
