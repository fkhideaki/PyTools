"""
## 概要
- フォルダ内のファイル一覧HTMLを生成するスクリプト

## 使い方
- python DownloadLinkBuilder.py <フォルダパス>

## options
- --gui : GUIモードで実行
- --php : phpのダウンロードカウント付きページを作成
- --title <タイトル> : ページタイトルを指定（省略時は'##TITLE##'という形式のプレースホルダ）
- --page_list : ダウンロード用ではなく通常のページリストを作成
- --download : リンクをdownload指定で生成
- --action : ダウンロード用アクションボタンを表示
- --sort : テーブルのソート機能を有効化
- --modified : 更新日時を表示
- --size : サイズを表示
- --desc : 説明を表示する列を追加
"""


import argparse
from dataclasses import dataclass
import sys
import math
from datetime import datetime
from pathlib import Path
from html import escape
from typing import Optional


import tkinter as tk
from tkinter import filedialog, messagebox
import tkinter as tk
import tkinterdnd2 as tkdnd


# ファイル拡張子に対応するアイコン（絵文字）
ICON_MAP = {
    # 圧縮ファイル
    ".zip": "📦", ".gz": "📦", ".tar": "📦", ".rar": "📦", ".7z": "📦",
    ".bz2": "📦", ".xz": "📦",
    # ドキュメント
    ".pdf": "📄", ".doc": "📝", ".docx": "📝", ".odt": "📝",
    ".xls": "📊", ".xlsx": "📊", ".ods": "📊",
    ".ppt": "📋", ".pptx": "📋", ".odp": "📋",
    ".txt": "📃", ".md": "📃", ".rst": "📃",
    # 画像
    ".jpg": "🖼️", ".jpeg": "🖼️",
    ".tif": "🖼️", ".tiff": "🖼️",
    ".png": "🖼️", ".gif": "🖼️",
    ".ai": "🖼️",
    # 動画
    ".mp4": "🎬", ".mov": "🎬", ".avi": "🎬", ".mkv": "🎬",
    ".webm": "🎬", ".flv": "🎬",
    # 音声
    ".mp3": "🎵", ".wav": "🎵", ".ogg": "🎵", ".flac": "🎵", ".aac": "🎵",
    # コード
    ".py": "🐍", ".js": "📜", ".ts": "📜", ".html": "🌐",
    ".css": "🎨", ".json": "📋", ".xml": "📋", ".yaml": "📋", ".yml": "📋",
    ".sh": "⚙️", ".bash": "⚙️", ".bat": "⚙️", ".ps1": "⚙️",
    # データ
    ".csv": "📊", ".tsv": "📊", ".sql": "🗄️", ".db": "🗄️",
    # 実行ファイル
    ".exe": "⚙️", ".msi": "⚙️", ".dmg": "⚙️", ".deb": "⚙️", ".rpm": "⚙️",
    # フォルダ
    "__dir__": "📁",
    # デフォルト
    "__default__": "📎",
}

def get_icon(path: Path) -> str:
    if path.is_dir():
        return ICON_MAP["__dir__"]
    return ICON_MAP.get(path.suffix.lower(), ICON_MAP["__default__"])


@dataclass
class Config:
    php_mode: bool = False
    download_link: bool = False
    enable_action: bool = False
    enable_sort: bool = False
    show_modified: bool = False
    show_size: bool = False
    show_desc: bool = False


def format_size(size_bytes: int) -> str:
    """バイト数を人間が読みやすい形式に変換"""
    if size_bytes == 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB"]
    i = int(math.floor(math.log(size_bytes, 1024)))
    i = min(i, len(units) - 1)
    val = size_bytes / (1024 ** i)
    if i == 0:
        return f"{int(val)} B"
    return f"{val:.1f} {units[i]}"


def format_mtime(mtime: float) -> str:
    """更新日時をフォーマット"""
    return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")

def generate_html(folder: Path, title: str, cfg: Config) -> str:
    """index.html の内容を生成"""

    entries = []
    for item in sorted(folder.iterdir()):
        if not item.is_file():
            continue
        if item.name in ['index.html', 'index.php', '_download.php', '_count.json']:
            continue
        stat = item.stat()
        entries.append({
            'name': item.name,
            'icon': get_icon(item),
            'size_bytes': stat.st_size,
            'mtime': format_mtime(stat.st_mtime),
        })

    entries.sort(key=lambda e: e["name"].lower())

    use_desc = cfg.show_desc
    use_size_bytes = cfg.show_size
    use_modified = cfg.show_modified
    use_download = cfg.enable_action
    download_link = cfg.download_link
    if not entries:
        rows_html = '<tr><td colspan="4" class="empty-msg">ファイルが見つかりません</td></tr>'
    else:
        rows_html = ""
        for e in entries:
            name = e['name']
            name_esc = escape(name)
            name_lower = escape(name.lower())
            size_bytes = e['size_bytes']
            size = format_size(size_bytes)
            icon = e['icon']
            mtime = e['mtime']
            td_desc = '<td class="col-desc">##description##</td>'
            td_size = f'<td class="col-size">{size}</td>'
            td_date = f'<td class="col-date">{mtime}</td>'
            if cfg.php_mode:
                download_url = f'_download.php?file={name_esc}'
            else:
                download_url = name_esc
            td_act = f'<td class="col-action"><a href="{download_url}" class="btn-dl" download title="ダウンロード">↓</a></td>'
            rows_html += f"""\
          <tr class="entry-row" data-name="{name_lower}" data-size="{size_bytes}">
            <td class="col-icon">{icon}</td>
            <td class="col-name">
              <a href="{download_url}" class="file-link" {'download' if download_link else ''}>{name_esc}</a>
            </td>
            {td_desc if use_desc else ''}
            {td_size if use_size_bytes else ''}
            {td_date if use_modified else ''}
            {td_act if use_download else ''}
          </tr>
"""

    main_table = f'''\
      <table id="file-table">
        <thead>
          <tr>
            <th class="col-icon"></th>
            <th class="col-name" data-col="name">Name</th>
            {'<th class="col-desc" data-col="desc">Description</th>' if use_desc else ''}
            {'<th class="col-size" data-col="size">Size</th>' if use_size_bytes else ''}
            {'<th class="col-date" data-col="date">Modified</th>' if use_modified else ''}
            {'<th class="col-action">Download</th>' if use_download else ''}
          </tr>
        </thead>
        <tbody id="file-body">
{rows_html}
        </tbody>
      </table>
'''
    sort_script = '' if not cfg.enable_sort else '''\
  <script>
    // ── テーブルソート ────────────────────────────────────
    const tbody = document.getElementById('file-body');
    let sortCol = null;
    let sortAsc = true;

    document.querySelectorAll('th[data-col]').forEach(th => {{
      th.addEventListener('click', () => {{
        const col = th.dataset.col;
        if (sortCol === col) {{
          sortAsc = !sortAsc;
        }} else {{
          sortCol = col;
          sortAsc = true;
        }}
        document.querySelectorAll('th').forEach(t => t.classList.remove('sort-asc', 'sort-desc'));
        th.classList.add(sortAsc ? 'sort-asc' : 'sort-desc');

        const rowArr = Array.from(tbody.querySelectorAll('.entry-row'));
        rowArr.sort((a, b) => {{
          let av, bv;
          if (col === 'name') {{
            av = a.dataset.name;
            bv = b.dataset.name;
            return sortAsc ? av.localeCompare(bv, 'ja') : bv.localeCompare(av, 'ja');
          }} else if (col === 'size') {{
            av = parseInt(a.dataset.size) || 0;
            bv = parseInt(b.dataset.size) || 0;
            return sortAsc ? av - bv : bv - av;
          }} else if (col === 'date') {{
            av = a.querySelector('.col-date')?.textContent || '';
            bv = b.querySelector('.col-date')?.textContent || '';
            return sortAsc ? av.localeCompare(bv) : bv.localeCompare(av);
          }}
          return 0;
        }});
        rowArr.forEach(r => tbody.appendChild(r));
      }});
    }});
  </script>
'''

    return f"""\
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <style>
    /* ─── Reset & Base ─────────────────────────────────── */
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    :root {{
      --bg:        #f5f7fa;
      --surface:   #ffffff;
      --border:    #dde2ea;
      --accent:    #2563eb;
      --accent2:   #7c3aed;
      --text:      #1e2433;
      --muted:     #6b7280;
      --hover-row: #f0f4ff;
      --radius:    10px;
      --font-mono: 'JetBrains Mono', 'Cascadia Code', 'Fira Code', monospace;
      --font-sans: 'Noto Sans JP', 'Hiragino Sans', 'Yu Gothic', system-ui, sans-serif;
    }}

    body {{
      background: var(--bg);
      color: var(--text);
      font-family: var(--font-sans);
      min-height: 100vh;
      padding: 2rem 1rem;
    }}

    /* ─── Layout ────────────────────────────────────────── */
    .container {{
      max-width: 960px;
      margin: 0 auto;
    }}

    /* ─── Header ────────────────────────────────────────── */
    .header {{
      margin-bottom: 1.5rem;
    }}

    .header-top {{
      display: flex;
      align-items: center;
      gap: 1rem;
    }}

    .folder-badge {{
      font-size: 2.5rem;
      line-height: 1;
      flex-shrink: 0;
    }}

    .header-text h1 {{
      font-size: clamp(1.4rem, 4vw, 2rem);
      font-weight: 700;
      letter-spacing: -0.02em;
      background: linear-gradient(135deg, var(--accent) 0%, var(--accent2) 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      word-break: break-all;
    }}

    /* ─── Table ─────────────────────────────────────────── */
    .table-wrap {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      overflow: hidden;
      box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
    }}

    thead tr {{
      background: #eef1f6;
      border-bottom: 1px solid var(--border);
    }}

    th {{
      padding: 0.75rem 1rem;
      text-align: left;
      font-size: 0.72rem;
      font-family: var(--font-mono);
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--muted);
      font-weight: 600;
      user-select: none;
      white-space: nowrap;
      {"cursor: pointer;" if cfg.enable_sort else ""}
    }}

    th:hover {{ color: var(--text); }}
    th.sort-asc::after  {{ content: " ↑"; color: var(--accent); }}
    th.sort-desc::after {{ content: " ↓"; color: var(--accent); }}

    .entry-row {{
      border-bottom: 1px solid var(--border);
      transition: background 0.15s;
      opacity: 0;
      animation: fadeIn 0.35s ease forwards;
    }}

    @keyframes fadeIn {{
      from {{ opacity: 0; transform: translateY(6px); }}
      to   {{ opacity: 1; transform: translateY(0); }}
    }}

    .entry-row:last-child {{ border-bottom: none; }}
    .entry-row:hover {{ background: var(--hover-row); }}

    td {{
      padding: 0.7rem 1rem;
      font-size: 0.88rem;
      vertical-align: middle;
    }}

    .col-icon   {{ width: 2rem; font-size: 1.1rem; padding-right: 0; }}
    .col-name   {{ max-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
    .col-desc   {{ width: 12rem; color: var(--muted); font-size: 0.85rem; }}
    .col-size   {{ width: 7rem; text-align: center; color: var(--muted); font-family: var(--font-mono); font-size: 0.78rem; }}
    .col-date   {{ width: 11rem; text-align: center; color: var(--muted); font-family: var(--font-mono); font-size: 0.78rem; }}
    .col-action {{ width: 3rem; text-align: center; }}

    @media (max-width: 600px) {{
      .col-date {{ display: none; }}
      .col-size {{ width: 5.5rem; }}
    }}

    .file-link {{
      color: var(--text);
      text-decoration: none;
      font-weight: 500;
      transition: color 0.15s;
    }}

    .file-link:hover {{ color: var(--accent); }}

    .btn-dl {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 1.8rem;
      height: 1.8rem;
      border-radius: 6px;
      background: transparent;
      border: 1px solid var(--border);
      color: var(--accent);
      font-size: 0.9rem;
      font-weight: 700;
      text-decoration: none;
      transition: background 0.15s, color 0.15s;
    }}

    .btn-dl:hover {{
      background: var(--accent);
      color: #fff;
      border-color: var(--accent);
    }}

    .empty-msg {{
      text-align: center;
      color: var(--muted);
      padding: 3rem !important;
      font-style: italic;
    }}
  </style>
</head>
<body>
  <div class="container">

    <!-- ヘッダー -->
    <header class="header">
      <div class="header-top">
        <div class="folder-badge">📂</div>
        <div class="header-text">
          <h1>{title}</h1>
        </div>
      </div>
    </header>

    <!-- テーブル -->
    <div class="table-wrap">
{main_table}
    </div>
  </div>
{sort_script}
</body>
</html>
"""


download_api = r'''
<?php
define('FILES_DIR',  __DIR__ . '/');
define('COUNTS_FILE', __DIR__ . '/_counts.json');

$requested = isset($_GET['file']) ? basename($_GET['file']) : '';
$file_path = FILES_DIR . $requested;

function verifyFile()
{
    global $file_path;

    if (!is_file($file_path)) {
        http_response_code(404);
        exit('File not found.');
    }
}

function addCount()
{
    global $requested;

    $counts = [];

    $fp = fopen(COUNTS_FILE, 'c+');
    if ($fp === false) {
        http_response_code(500);
        exit('Could not open counts file.');
    }

    if (flock($fp, LOCK_EX)) {
        $size = filesize(COUNTS_FILE);
        if ($size > 0) {
            $json = fread($fp, $size);
            $counts = json_decode($json, true) ?? [];
        }

        $counts[$requested] = ($counts[$requested] ?? 0) + 1;

        ftruncate($fp, 0);
        rewind($fp);
        fwrite($fp, json_encode($counts, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
        fflush($fp);
        flock($fp, LOCK_UN);
    }
    fclose($fp);
}

function execDownload()
{
    global $requested;
    global $file_path;

    $mime = mime_content_type($file_path) ?: 'application/octet-stream';

    header('Content-Type: ' . $mime);
    header('Content-Disposition: attachment; filename="' . rawurlencode($requested) . '"');
    header('Content-Length: ' . filesize($file_path));
    header('Cache-Control: no-cache, no-store, must-revalidate');
    header('Pragma: no-cache');
    header('Expires: 0');

    readfile($file_path);
    exit;
}

verifyFile();
addCount();
execDownload();
'''


def generate_main(folder, title, cfg):
    html = generate_html(folder, title, cfg)

    if cfg.php_mode:
        (folder / "index.php").write_text(html, encoding="utf-8")
        dl_api = folder / "_download.php"
        dl_api.write_text(download_api, encoding="utf-8")
        count = folder / "_counts.json"
        if not count.exists():
            count.write_text('{}', encoding="utf-8")
    else:
        output_path = folder / "index.html"
        output_path.write_text(html, encoding="utf-8")


def gui_mode():
    root = tkdnd.Tk()
    root.title("LinkListBuilder GUI")
    root.geometry("400x300")
    root.resizable(False, False)
    php_var = tk.BooleanVar()
    tk.Checkbutton(root, text="PHPモード (--php)", variable=php_var).pack(anchor='w', padx=20)
    download_link_var = tk.BooleanVar()
    tk.Checkbutton(root, text="リンクをdownload指定で生成 (--download)", variable=download_link_var).pack(anchor='w', padx=20)
    enable_action_var = tk.BooleanVar()
    tk.Checkbutton(root, text="アクションボタン (--action)", variable=enable_action_var).pack(anchor='w', padx=20)
    sort_var = tk.BooleanVar()
    tk.Checkbutton(root, text="テーブルソート有効 (--sort)", variable=sort_var).pack(anchor='w', padx=20)
    modified_var = tk.BooleanVar()
    tk.Checkbutton(root, text="更新日時表示 (--modified)", variable=modified_var).pack(anchor='w', padx=20)
    size_var = tk.BooleanVar()
    tk.Checkbutton(root, text="サイズ表示 (--size)", variable=size_var).pack(anchor='w', padx=20)
    desc_var = tk.BooleanVar()
    tk.Checkbutton(root, text="説明表示 (--desc)", variable=desc_var).pack(anchor='w', padx=20)

    tk.Label(root, text="ページタイトル (--title)", font=("Arial", 12)).pack(pady=10)
    title_entry = tk.Entry(root, width=30)
    title_entry.pack()
    title_entry.insert(0, "##TITLE##")
    tk.Label(root, text="フォルダをこのウィンドウにドロップしてください", font=("Arial", 10)).pack(pady=20)

    def on_drop(event):
        folder_path = event.data.strip('{}')  # ドロップされたパスを取得
        folder = Path(folder_path)
        if not folder.is_dir():
            messagebox.showerror("エラー", "有効なフォルダをドロップしてください")
            return
        cfg = Config(
            php_mode=php_var.get(),
            download_link=download_link_var.get(),
            enable_action=enable_action_var.get(),
            enable_sort=sort_var.get(),
            show_modified=modified_var.get(),
            show_size=size_var.get(),
            show_desc=desc_var.get()
        )
        title = title_entry.get() or "##TITLE##"
        generate_main(folder, title, cfg)
    root.drop_target_register(tkdnd.DND_FILES)
    root.dnd_bind('<<Drop>>', on_drop)
    root.mainloop()

def main():
    parser = argparse.ArgumentParser(
        description="フォルダ内のファイル一覧 index.html を生成します",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
例:
  python generate_index.py ./downloads
        """,
    )
    parser.add_argument("folder", nargs="?", help="対象フォルダのパス")
    parser.add_argument("--gui", action="store_true", help="GUIモードで実行")
    parser.add_argument("--php", action="store_true", help="phpモード")
    parser.add_argument("--title", default=None, help="ページタイトル")
    parser.add_argument("--download", action="store_true", help="リンクをdownload指定で生成")
    parser.add_argument("--action", action="store_true", help="ダウンロード用アクションボタンを表示")
    parser.add_argument("--sort", action="store_true", help="テーブルのソート機能を有効化")
    parser.add_argument("--modified", action="store_true", help="更新日時を表示")
    parser.add_argument("--size", action="store_true", help="サイズを表示")
    parser.add_argument("--desc", action="store_true", help="説明を表示する列を追加")
    args = parser.parse_args()

    if args.gui:
        gui_mode()
        return

    folder = Path(args.folder).resolve()
    if not folder.is_dir():
        print(f"❌ エラー: フォルダを指定してください: {folder}", file=sys.stderr)
        sys.exit(1)

    title = args.title
    if not title:
        title = '##TITLE##'

    cfg = Config()
    cfg.php_mode = args.php
    cfg.download_link = args.download
    cfg.enable_action = args.action
    cfg.enable_sort = args.sort
    cfg.show_modified = args.modified
    cfg.show_size = args.size
    cfg.show_desc = args.desc

    generate_main(folder, title, cfg)


if __name__ == "__main__":
    main()
