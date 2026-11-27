'''
# GeneratePattern

## 概要
特定のパターンに基づいて文字列を生成するスクリプト。

## 使い方
1. `pattern` 変数に生成したい文字列のパターン。プレースホルダー `$0`, `$1`, `$2` を使用可。
2. `words0`, `words1`, `words2` リストにそれぞれのプレースホルダーに対応する文字列のリスト。
3. スクリプトを実行すると、指定したパターンに基づいて全ての組み合わせの文字列が生成され、出力される。

## GUI
- Pattern 欄にパターンを入力する。
- $0 / $1 / $2 の各欄に、1行につき1単語を入力する（空行は無視される）。
- Generate ボタンで結果欄に全組み合わせが出力される。
- 「同一インデックスで組み合わせる」をオンにすると総当たりではなく、
  各欄の同じ行どうしを組み合わせる（足りない欄は空文字扱い）。
  例: Pattern=$0_$1, $0=[1,2], $1=[a,b,c] → 1_a, 2_b, _c
'''

from dataclasses import dataclass
import tkinter as tk
from tkinter import ttk


@dataclass
class PatternGenerator:
    pattern: str
    words0: list
    words1: list
    words2: list

    def gen_words(self):
        for w0 in self.words0 or ['']:
            t0 = self.pattern.replace('$0', w0)
            for w1 in self.words1 or ['']:
                t1 = t0.replace('$1', w1)
                for w2 in self.words2 or ['']:
                    t2 = t1.replace('$2', w2)
                    yield t2

    def gen_words_by_index(self):
        '''各リストの同一インデックスの単語を組み合わせて生成する。
        最も長いリストの件数分を生成し、足りないリストは空文字で埋める。'''
        lists = (self.words0, self.words1, self.words2)
        count = max(len(w) for w in lists)
        for i in range(count):
            w0, w1, w2 = (w[i] if i < len(w) else '' for w in lists)
            yield self.pattern.replace('$0', w0).replace('$1', w1).replace('$2', w2)


def start_implement():
    pattern = 'file_$0$1.txt'

    words0 = [
        'a',
        'b',
        'c'
    ]
    words1 = [
        '0',
        '1'
    ]
    words2 = [
    ]

    generator = PatternGenerator(pattern, words0, words1, words2)
    for s in generator.gen_words():
        print(s)


def _make_scrolled_text(parent, height, width):
    '''縦スクロールバー付きの Text を parent 内に配置して返す。'''
    parent.columnconfigure(0, weight=1)
    parent.rowconfigure(0, weight=1)
    text = tk.Text(parent, height=height, width=width, wrap=tk.NONE, undo=True)
    text.grid(row=0, column=0, sticky=tk.NSEW)
    yscroll = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=text.yview)
    yscroll.grid(row=0, column=1, sticky=tk.NS)
    xscroll = ttk.Scrollbar(parent, orient=tk.HORIZONTAL, command=text.xview)
    xscroll.grid(row=1, column=0, sticky=tk.EW)
    text.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
    return text


def _get_lines(text_widget):
    '''Text の内容を1行1単語として取得する（前後の空白を除去し、空行は無視）。'''
    content = text_widget.get('1.0', tk.END)
    return [line.strip() for line in content.splitlines() if line.strip()]


def start_gui():
    root = tk.Tk()
    root.title("Pattern Generator")

    main = ttk.Frame(root, padding=10)
    main.grid(row=0, column=0, sticky=tk.NSEW)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    for c in range(3):
        main.columnconfigure(c, weight=1, uniform='words')
    main.rowconfigure(2, weight=1)  # 単語入力欄
    main.rowconfigure(4, weight=2)  # 結果欄

    # --- Pattern ---
    pattern_frame = ttk.Frame(main)
    pattern_frame.grid(row=0, column=0, columnspan=3, sticky=tk.EW, pady=(0, 8))
    pattern_frame.columnconfigure(1, weight=1)
    ttk.Label(pattern_frame, text="Pattern:").grid(row=0, column=0, sticky=tk.W, padx=(0, 6))
    pattern_entry = ttk.Entry(pattern_frame, width=90)
    pattern_entry.grid(row=0, column=1, sticky=tk.EW)

    ttk.Label(main, text="各欄に 1行1単語 で入力してください（空行は無視されます）").grid(
        row=1, column=0, columnspan=3, sticky=tk.W, pady=(0, 4))

    # --- Words ($0, $1, $2) ---
    words_texts = []
    for i in range(3):
        frame = ttk.LabelFrame(main, text=f"Words for ${i}", padding=4)
        frame.grid(row=2, column=i, sticky=tk.NSEW, padx=(0 if i == 0 else 4, 0 if i == 2 else 4))
        words_texts.append(_make_scrolled_text(frame, height=10, width=22))

    # --- Buttons ---
    button_frame = ttk.Frame(main)
    button_frame.grid(row=3, column=0, columnspan=3, pady=8)

    status_var = tk.StringVar(value="")
    by_index_var = tk.BooleanVar(value=False)

    def generate():
        pattern = pattern_entry.get()
        words0, words1, words2 = (_get_lines(t) for t in words_texts)

        generator = PatternGenerator(pattern, words0, words1, words2)
        if by_index_var.get():
            results = list(generator.gen_words_by_index())
        else:
            results = list(generator.gen_words())
        output_text.delete('1.0', tk.END)
        output_text.insert(tk.END, '\n'.join(results))
        status_var.set(f"{len(results)} 件生成しました")

    def copy_output():
        root.clipboard_clear()
        root.clipboard_append(output_text.get('1.0', 'end-1c'))
        status_var.set("結果をクリップボードにコピーしました")

    ttk.Checkbutton(button_frame, text="同一インデックスで組み合わせる（総当たりしない）",
                    variable=by_index_var).grid(row=0, column=0, padx=(0, 12))
    ttk.Button(button_frame, text="Generate", command=generate).grid(row=0, column=1, padx=4)
    ttk.Button(button_frame, text="Copy", command=copy_output).grid(row=0, column=2, padx=4)
    ttk.Label(button_frame, textvariable=status_var).grid(row=0, column=3, padx=(12, 0))

    # --- Output ---
    output_frame = ttk.LabelFrame(main, text="Result", padding=4)
    output_frame.grid(row=4, column=0, columnspan=3, sticky=tk.NSEW)
    output_text = _make_scrolled_text(output_frame, height=20, width=90)

    # 初期サイズで全パーツが収まるようにし、それ以下には縮まないようにする
    root.update_idletasks()
    root.minsize(root.winfo_reqwidth(), root.winfo_reqheight())

    pattern_entry.focus_set()
    root.mainloop()


def main():
    start_gui()
    # start_implement()


if __name__ == '__main__':
    main()
