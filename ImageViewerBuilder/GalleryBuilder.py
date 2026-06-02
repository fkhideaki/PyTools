"""
# GalleryBuilder.py

## 概要
- ギャラリー形式の画像ビューアーを生成する

## 使用方法
- python GalleryBuilder.py <フォルダパス> [options]
- options:
  - --wheel
    - 拡大画面をホイールでページ送りする機能を有効にする
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
    wheel: bool = False
    zip_file: str = ''

def generatePage(folder_path: Path, images: list[str], cfg: Cfg):
    folder_name = folder_path.name
    title = f'{folder_name}'

    enableWheel = 'true' if cfg.wheel else 'false'
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
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }}
        
        h1 {{
            text-align: center;
            color: #333;
            margin-bottom: 16px;
            font-size: 2em;
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
            width: 100%;
            height: 100%;
            background: rgba(10,10,10,0.9);
            align-items: center;
            justify-content: center;
            visibility: hidden;
            opacity: 0;
        }}
        
        .modal.active {{
            visibility: visible;
            opacity: 1;
            display: flex;
            animation: fadeIn 0.3s ease-in-out forwards;
        }}
        
        .modal-content {{
            max-width: min(95%, calc(100% - 10px));
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
        }}
        
        .modal-content img {{
            max-width: 100%;
            max-height: 90vh;
            object-fit: contain;
            display: block;
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
            background: rgba(200,200,200,0.25);
            width: 45px;
            height: 45px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 22px;
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

    <script>
        let currentIndex = 0;

        function showImage(index) {{
            const modalImg = document.getElementById('modal-img');
            const modalFilename = document.getElementById('modal-filename');
            const fn = images[index].fn;
            const cap = images[index].cap;
            modalImg.src = fn;
            modalImg.alt = fn;
            const numImg = images.length;
            modalFilename.textContent = cap + " (" + (index + 1) + "/" + numImg + ")";
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
        
        // ESCキーでモーダルを閉じる、矢印キーで画像切り替え
        document.addEventListener('keydown', function(e) {{
            const modal = document.getElementById('modal');
            if (!modal.classList.contains('active')) return;
            
            if (e.key === 'Escape') {{
                closeModal();
            }} else if (e.key === 'ArrowRight') {{
                nextImage();
            }} else if (e.key === 'ArrowLeft') {{
                prevImage();
            }}
        }});

        let enableWheel = {enableWheel};
        let enableSwipe = {enableSwipe};

        document.addEventListener('mousewheel', function(e) {{
            if (!enableWheel) return;

            const modal = document.getElementById('modal');
            if (!modal.classList.contains('active')) return;

            if (e.deltaY < 0) {{
                prevImage();
            }} else if (e.deltaY > 0) {{
                nextImage();
            }}
        }});

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
            const modal = document.getElementById('modal');
            if (!modal.classList.contains('active')) return;
            touchStartX = e.changedTouches[0].screenX;
        }});
        
        document.addEventListener('touchend', function(e) {{
            const modal = document.getElementById('modal');
            if (!modal.classList.contains('active')) return;
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
    
    <!-- モーダル -->
    <div id="modal" class="modal" onclick="closeModal()">
        <span class="close" onclick="closeModal()">&times;</span>
        <div class="nav-zone prev" onclick="event.stopPropagation(); prevImage()">
            <div class="nav-zone-arrow">＜</div>
        </div>
        <div class="nav-zone next" onclick="event.stopPropagation(); nextImage()">
            <div class="nav-zone-arrow">＞</div>
        </div>
        <div class="modal-content">
            <img id="modal-img" src="" alt="">
        </div>
        <div class="modal-filename" id="modal-filename"></div>
    </div>
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
    cfg.wheel = '--wheel' in opt
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
