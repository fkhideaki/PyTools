"""
# GalleryBuilder.py

## 概要
- ギャラリー形式の画像ビューアーを生成する

## 使用方法
- python GalleryBuilder.py <フォルダパス> [options]
- options:
  - --swipe
    - スマホ時にswipeでページ送りする機能を有効にする

## 一括ダウンロード機能
- 指定フォルダに一つだけzipファイルがある場合、そのファイルを一括ダウンロード用としてリンクを作成する
"""

from dataclasses import dataclass
import sys
from pathlib import Path
from typing import List

@dataclass
class Cfg:
    swipe: bool = False
    zip_file: str = ''

def generatePage(folder_path: Path, images: list[str], cfg: Cfg):
    folder_name = folder_path.name
    title = f'{folder_name}'

    enableSwipe = 'true' if cfg.swipe else 'false'

    html_template = f"""\
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        html {{
            scrollbar-gutter: stable;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }}
        
        h1 {{
            text-align: center;
            color: #333;
            margin-bottom: 16px;
            font-size: 1.8em;
            overflow-wrap: anywhere;
        }}
        
        .download-bar {{
            text-align: center;
            margin-bottom: 30px;
        }}

        .download-bar a {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 20px;
            background: #4a90d9;
            color: #fff;
            text-decoration: none;
            border-radius: 6px;
            font-size: 0.95em;
            font-weight: 500;
            transition: background 0.2s, transform 0.1s;
        }}

        .download-bar a:hover {{
            background: #2f72b8;
            transform: translateY(-1px);
        }}

        .download-bar a:active {{
            transform: translateY(0);
        }}

        .download-bar a svg {{
            flex-shrink: 0;
        }}
        
        .gallery {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .image-container {{
            background: white;
            border-radius: 8px;
            padding: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
            cursor: pointer;
            -webkit-user-select: none;
            user-select: none;
        }}
        
        .image-container:hover {{
            transform: translateY(-5px);
            box-shadow: 0 4px 16px rgba(0,0,0,0.2);
        }}
        
        .image-wrapper {{
            width: 100%;
            height: 200px;
            display: flex;
            align-items: center;
            justify-content: center;
            background-color: #eee;
            border: 2px solid #e0e0e0;
            overflow: hidden;
        }}
        
        .image-wrapper img {{
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
            display: block;
            background:
                linear-gradient(45deg, #bbb 25%, transparent 25%, transparent 75%, #bbb 75%),
                linear-gradient(45deg, #bbb 25%, transparent 25%, transparent 75%, #bbb 75%);
            background-size: 20px 20px;
            background-position: 0 0, 10px 10px;
        }}
        
        .image-name {{
            margin-top: 10px;
            font-size: 0.9em;
            color: #666;
            text-align: center;
            word-break: break-all;
        }}
        
        /* モーダル */
        .modal {{
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100dvw;
            height: 100dvh;
            background: rgba(10,10,10,0.9);
            align-items: center;
            justify-content: center;
            visibility: hidden;
            opacity: 0;
            overflow: hidden;
            overscroll-behavior: contain;
            touch-action: none;
            /* 高速クリックなどによる選択状態を防ぐ */
            -webkit-user-select: none;
            user-select: none;
            -webkit-tap-highlight-color: transparent;
        }}
        
        .modal.active {{
            visibility: visible;
            opacity: 1;
            display: flex;
            animation: fadeIn 0.3s ease-in-out forwards;
        }}
        
        .modal-content {{
            max-width: 100%;
            max-height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            background:
                linear-gradient(45deg, #aaa 25%, transparent 25%, transparent 75%, #aaa 75%),
                linear-gradient(45deg, #aaa 25%, transparent 25%, transparent 75%, #aaa 75%);
            background-color: #ccc;
            background-size: 30px 30px;
            background-position: 0 0, 15px 15px;
            transform-origin: center center;
            will-change: transform;
        }}
        
        .modal-content img {{
            max-width: 100%;
            max-height: 90vh;
            object-fit: contain;
            display: block;
            -webkit-user-drag: none;
            user-select: none;
            pointer-events: auto;
        }}
        
        .close {{
            position: absolute;
            top: 20px;
            right: 40px;
            color: #fff;
            font-size: 40px;
            font-weight: bold;
            cursor: pointer;
            transition: color 0.2s;
            z-index: 1002;
        }}
        
        .close:hover {{
            color: #bbb;
        }}
        
        .nav-zone {{
            position: absolute;
            top: 0;
            height: 100%;
            width: 15%;
            z-index: 1001;
            cursor: pointer;
        }}

        .nav-zone.prev {{
            left: 0;
        }}

        .nav-zone.next {{
            right: 0;
        }}

        .nav-zone-arrow {{
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            color: #fff;
            font-size: 30px;
            font-weight: bold;
            width: 30px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0;
            transition: opacity 0.2s;
            user-select: none;
            line-height: 1;
        }}

        .nav-zone.prev .nav-zone-arrow {{
            left: 10px;
        }}

        .nav-zone.next .nav-zone-arrow {{
            right: 10px;
        }}

        .nav-zone:hover .nav-zone-arrow {{
            opacity: 1;
        }}
        
        .modal-filename {{
            position: absolute;
            bottom: 4px;
            left: 50%;
            transform: translateX(-50%);
            color: white;
            background: rgba(100,100,100,0.7);
            padding: 4px 4px;
            border-radius: 4px;
            font-size: 1em;
            z-index: 1001;
            white-space: nowrap;
        }}
        
        @keyframes fadeIn {{
            from {{
                opacity: 0;
            }}
            to {{
                opacity: 1;
            }}
        }}
    </style>
    <title>{title}</title>
</head>
"""

    zip_file = cfg.zip_file
    if not zip_file:
        download_link = ''
    else:
        download_link = f'''\
    <div class="download-bar">
        <a href="{zip_file}" download>
            <svg xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2.5"
                stroke-linecap="round"
                stroke-linejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="7 10 12 15 17 10"/>
                <line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
            すべてダウンロード
        </a>
    </div>
'''

    html_template += f"""\
<body>
    <h1>{folder_name}</h1>

{download_link}
    <div class="gallery">
    </div>
"""

    images_json = '['
    for img in images:
        images_json += f'\n{{fn: "{img}", cap: "{Path(img).stem}"}}'
        if not img is images[-1]:
            images_json += ','
    images_json += '\n]'

    html_template += f"""\

    <script>
        const images = {images_json};
    </script>

    <!-- モーダル -->
    <div id="modal" class="modal" onclick="closeModal()">
        <span class="close" onclick="closeModal()">&times;</span>
        <div class="nav-zone prev" onclick="event.stopPropagation(); prevImage()">
            <div class="nav-zone-arrow">&lt;</div>
        </div>
        <div class="nav-zone next" onclick="event.stopPropagation(); nextImage()">
            <div class="nav-zone-arrow">&gt;</div>
        </div>
        <div class="modal-content" id="modal-content">
            <img id="modal-img" src="" alt="" draggable="false">
        </div>
        <div class="modal-filename" id="modal-filename"></div>
    </div>

    <script>
        let currentIndex = 0;

        // ---- 拡大縮小の状態 ----
        const ZOOM_MIN = 0.25;
        const ZOOM_MAX = 16;
        const zoom = {{ scale: 1, x: 0, y: 0 }};

        function applyZoom() {{
            const mc = document.getElementById('modal-content');
            mc.style.transform =
                'translate(' + zoom.x + 'px, ' + zoom.y + 'px) scale(' + zoom.scale + ')';
            mc.style.cursor = (zoom.scale !== 1) ? 'grab' : '';
        }}

        function resetZoom() {{
            zoom.scale = 1;
            zoom.x = 0;
            zoom.y = 0;
            applyZoom();
        }}

        // 画面座標(clientX, clientY)を基準に倍率を変更
        function zoomAt(clientX, clientY, factor) {{
            const modal = document.getElementById('modal');
            const newScale = Math.min(ZOOM_MAX, Math.max(ZOOM_MIN, zoom.scale * factor));
            if (newScale === zoom.scale) return;
            const ratio = newScale / zoom.scale;
            const cx = clientX - modal.clientWidth / 2;
            const cy = clientY - modal.clientHeight / 2;
            zoom.x = cx - ratio * (cx - zoom.x);
            zoom.y = cy - ratio * (cy - zoom.y);
            zoom.scale = newScale;
            applyZoom();
        }}

        function showImage(index) {{
            const modalImg = document.getElementById('modal-img');
            const modalFilename = document.getElementById('modal-filename');
            const fn = images[index].fn;
            const cap = images[index].cap;
            modalImg.src = fn;
            modalImg.alt = fn;
            const numImg = images.length;
            modalFilename.textContent = cap + " (" + (index + 1) + "/" + numImg + ")";
            resetZoom();
        }}
        
        function getIdx(filename) {{
            let n = images.length;
            for (var i = 0; i < n; ++i) {{
                if (images[i].fn == filename) {{
                    return i;
                }}
            }}
            return -1;
        }}
        
        function openModal(filename) {{
            const modal = document.getElementById('modal');
            currentIndex = getIdx(filename);
            showImage(currentIndex);
            modal.classList.add('active');
        }}
        
        function nextImage() {{
            currentIndex = (currentIndex + 1) % images.length;
            showImage(currentIndex);
        }}
        
        function prevImage() {{
            currentIndex = (currentIndex - 1 + images.length) % images.length;
            showImage(currentIndex);
        }}
        
        function closeModal() {{
            const modal = document.getElementById('modal');
            modal.classList.remove('active');
        }}

        function isModalActive() {{
            return document.getElementById('modal').classList.contains('active');
        }}
        
        // ESCキーでモーダルを閉じる、矢印キーで画像切り替え、+/-/0で拡大縮小
        document.addEventListener('keydown', function(e) {{
            if (!isModalActive()) return;
            
            if (e.key === 'Escape') {{
                closeModal();
            }} else if (e.key === 'ArrowRight') {{
                nextImage();
            }} else if (e.key === 'ArrowLeft') {{
                prevImage();
            }} else if (e.key === '+' || e.key === '=') {{
                const m = document.getElementById('modal');
                zoomAt(m.clientWidth / 2, m.clientHeight / 2, 1.25);
            }} else if (e.key === '-') {{
                const m = document.getElementById('modal');
                zoomAt(m.clientWidth / 2, m.clientHeight / 2, 1 / 1.25);
            }} else if (e.key === '0') {{
                resetZoom();
            }}
        }});

        // マウスホイール: モーダル表示中は背景をスクロールさせず、画像を拡大縮小する
        document.addEventListener('wheel', function(e) {{
            if (!isModalActive()) return;
            e.preventDefault();

            let delta = e.deltaY;
            if (e.deltaMode === 1) delta *= 16;        // 行単位
            else if (e.deltaMode === 2) delta *= 100;  // ページ単位
            const factor = Math.exp(-delta * 0.0015);
            zoomAt(e.clientX, e.clientY, factor);
        }}, {{ passive: false }});

        // 拡大中はドラッグで画像を移動
        let dragging = false;
        let dragMoved = false;
        let suppressClick = false;
        let dragLastX = 0;
        let dragLastY = 0;
        let dragStartX = 0;
        let dragStartY = 0;

        document.getElementById('modal-content').addEventListener('mousedown', function(e) {{
            if (e.button !== 0 || zoom.scale === 1) return;
            dragging = true;
            dragMoved = false;
            dragLastX = dragStartX = e.clientX;
            dragLastY = dragStartY = e.clientY;
            this.style.cursor = 'grabbing';
        }});

        window.addEventListener('mousemove', function(e) {{
            if (!dragging) return;
            if (Math.abs(e.clientX - dragStartX) > 3 || Math.abs(e.clientY - dragStartY) > 3) {{
                dragMoved = true;
            }}
            zoom.x += e.clientX - dragLastX;
            zoom.y += e.clientY - dragLastY;
            dragLastX = e.clientX;
            dragLastY = e.clientY;
            applyZoom();
        }});

        window.addEventListener('mouseup', function() {{
            if (!dragging) return;
            dragging = false;
            if (dragMoved) {{
                // ドラッグ直後のclickでモーダルが閉じないようにする
                suppressClick = true;
                setTimeout(function() {{ suppressClick = false; }}, 0);
            }}
            applyZoom();
        }});

        // タッチ操作: 2本指ピンチで拡大縮小（中点の移動でパンも可）、拡大中は1本指でパン
        (function() {{
            const modal = document.getElementById('modal');
            let lastDist = 0, lastX = 0, lastY = 0;
            let startX = 0, startY = 0;
            let touchMoved = false;

            function info(touches) {{
                if (touches.length >= 2) {{
                    const a = touches[0], b = touches[1];
                    return {{
                        n: 2,
                        dist: Math.hypot(b.clientX - a.clientX, b.clientY - a.clientY),
                        x: (a.clientX + b.clientX) / 2,
                        y: (a.clientY + b.clientY) / 2
                    }};
                }}
                return {{ n: 1, dist: 0, x: touches[0].clientX, y: touches[0].clientY }};
            }}

            modal.addEventListener('touchstart', function(e) {{
                if (!isModalActive() || e.touches.length === 0) return;
                const i = info(e.touches);
                lastDist = i.dist;
                lastX = i.x;
                lastY = i.y;
                if (e.touches.length === 1) {{
                    startX = i.x;
                    startY = i.y;
                    touchMoved = false;
                }} else {{
                    touchMoved = true; // 複数指の操作ではタップ扱いにしない
                }}
            }}, {{ passive: false }});

            modal.addEventListener('touchmove', function(e) {{
                if (!isModalActive() || e.touches.length === 0) return;
                const i = info(e.touches);
                if (i.n >= 2) {{
                    e.preventDefault();
                    touchMoved = true;
                    zoom.x += i.x - lastX;
                    zoom.y += i.y - lastY;
                    if (lastDist > 0 && i.dist > 0) {{
                        zoomAt(i.x, i.y, i.dist / lastDist);
                    }}
                    applyZoom();
                    lastDist = i.dist;
                }} else if (zoom.scale !== 1) {{
                    e.preventDefault();
                    if (Math.abs(i.x - startX) > 3 || Math.abs(i.y - startY) > 3) {{
                        touchMoved = true;
                    }}
                    zoom.x += i.x - lastX;
                    zoom.y += i.y - lastY;
                    applyZoom();
                }}
                lastX = i.x;
                lastY = i.y;
            }}, {{ passive: false }});

            modal.addEventListener('touchend', function(e) {{
                if (!isModalActive()) return;
                if (e.touches.length > 0) {{
                    // 指が1本残った場合: 位置が飛ばないよう基準を更新
                    const i = info(e.touches);
                    lastDist = i.dist;
                    lastX = i.x;
                    lastY = i.y;
                    touchMoved = true;
                    return;
                }}
                if (touchMoved) {{
                    // ピンチ/パンの後にclickでモーダルが閉じたり画像が切り替わらないようにする
                    if (e.cancelable) e.preventDefault();
                    suppressClick = true;
                    setTimeout(function() {{ suppressClick = false; }}, 350);
                }}
                touchMoved = false;
            }}, {{ passive: false }});

            modal.addEventListener('touchcancel', function() {{
                touchMoved = false;
            }});

            // iOS Safari のページ全体ピンチズームを抑止
            ['gesturestart', 'gesturechange', 'gestureend'].forEach(function(name) {{
                modal.addEventListener(name, function(e) {{ e.preventDefault(); }});
            }});
        }})();

        // 選択状態になるのを防ぐ（高速クリック・ダブルクリック対策）
        (function() {{
            const modal = document.getElementById('modal');
            // クリック開始時の選択・ドラッグ開始を抑止
            modal.addEventListener('mousedown', function(e) {{
                if (e.detail > 1 || true) e.preventDefault();
            }});
            modal.addEventListener('dblclick', function(e) {{
                e.preventDefault();
            }});
            modal.addEventListener('dragstart', function(e) {{
                e.preventDefault();
            }});
            // ドラッグ直後のclickを無効化（キャプチャ段階で止める）
            modal.addEventListener('click', function(e) {{
                if (suppressClick) {{
                    e.stopPropagation();
                    e.preventDefault();
                    suppressClick = false;
                }}
            }}, true);
        }})();

        document.addEventListener('selectstart', function(e) {{
            if (isModalActive()) e.preventDefault();
        }});

        let enableSwipe = {enableSwipe};

        // タッチスワイプイベント
        let touchStartX = 0;
        let touchEndX = 0;

        function handleSwipe() {{
            if (!enableSwipe) return;
            if (touchEndX < touchStartX - 50) {{
                // 右から左へのスワイプ（次の画像）
                nextImage();
            }} else if (touchEndX > touchStartX + 50) {{
                // 左から右へのスワイプ（前の画像）
                prevImage();
            }}
        }}
        
        document.addEventListener('touchstart', function(e) {{
            if (!isModalActive()) return;
            touchStartX = e.changedTouches[0].screenX;
        }});
        
        document.addEventListener('touchend', function(e) {{
            if (!isModalActive()) return;
            touchEndX = e.changedTouches[0].screenX;
            handleSwipe();
        }});

        function makeElem(tagType, className, parent)
        {{
            var d = document.createElement(tagType);
            if (className != '')
                d.className = className;
            parent.appendChild(d);
            return d;
        }}

        function makeGallery()
        {{
            var gallery = document.getElementsByClassName('gallery')[0];
            var n = images.length;
            for (var i = 0; i < n; ++i) {{
                var fn = images[i].fn;
                var cap = images[i].cap;
                var button = makeElem('div', 'image-container', gallery);
                button.onclick = function() {{
                    var fn = this.children[0].children[0].alt;
                    openModal(fn);
                }}
                var canvas = makeElem('div', 'image-wrapper', button);
                var img = makeElem('img', '', canvas);
                img.loading = "lazy";
                img.alt = fn;
                img.src = fn;
                var name = makeElem('div', 'image-name', button);
                name.innerHTML = cap;
            }}
        }}

        makeGallery();
    </script>
"""

    html_template += f"""\
</body>
</html>"""
    
    return html_template


def get_images(folder: Path) -> list[str]:
    extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'}

    images = []
    for file in sorted(folder.iterdir()):
        if not file.is_file():
            continue
        if file.suffix.lower() in extensions:
            images.append(file.name)
    
    return images

def get_zip(folder: Path) -> str:
    z = ''
    for file in folder.iterdir():
        if not file.is_file():
            continue
        if file.suffix.lower() == '.zip':
            if z:
                return ''
            z = file.name
    
    return z

def buildMain(folder: Path, opt: List[str]):
    if not folder.is_dir():
        print(f'{folder} is not folder')
        return

    if not folder.exists() or not folder.is_dir():
        raise ValueError(f"指定されたパスはフォルダではありません: {folder}")

    images = get_images(folder)
    if not images:
        print(f"{folder} に画像ファイルが見つかりませんでした")
        return

    cfg = Cfg()
    cfg.swipe = '--swipe' in opt
    cfg.zip_file = get_zip(folder)
    html = generatePage(folder, images, cfg)

    outFN = folder / "index.html"
    with open(outFN, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f'create viewer="{outFN}" images={len(images)}')

def main():
    dirs: List[Path] = []
    opt: List[str] = []
    
    for s in sys.argv[1:]:
        if s.startswith('--'):
            opt.append(s)
        else:
            p = Path(s)
            if p.is_dir():
                dirs.append(p)

    for d in dirs:
        buildMain(d, opt)

if __name__ == "__main__":
    main()
