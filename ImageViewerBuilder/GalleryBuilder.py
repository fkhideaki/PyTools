"""
# GalleryBuilder.py

## 概要
- ギャラリー形式の画像ビューアーを生成する

## 使用方法
- python GalleryBuilder.py <フォルダパス>
"""

import sys
from pathlib import Path

def generatePage(folder_path: Path, images: list[str]):
    folder_name = folder_path.name
    title = f'{folder_name}'
    
    html_template = f"""\
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
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
            margin-bottom: 30px;
            font-size: 2em;
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
            max-width: min(90%, calc(100% - 24px - 90px));
            max-height: 90%;
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
            max-height: 80vh;
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
            z-index: 1001;
        }}
        
        .close:hover {{
            color: #bbb;
        }}
        
        .nav-button {{
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            color: #fff;
            font-size: 30px;
            font-weight: bold;
            cursor: pointer;
            background: rgba(200,200,200,0.3);
            width: 45px;
            height: 45px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 22px;
            transition: all 0.2s;
            user-select: none;
            z-index: 1001;
            line-height: 1;
        }}
        
        .nav-button.prev {{
            left: 10px;
        }}
        
        .nav-button.next {{
            right: 10px;
        }}
        
        .nav-button:hover {{
            background: rgba(200,200,200,0.9);
            transform: translateY(-50%) scale(1.1);
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
</head>
"""

    html_template += f"""\
<body>
    <h1>{folder_name}</h1>

    <div class="gallery">
    </div>
"""

    images_json = '['
    for img in images:
        images_json += f'\n"{img}"'
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
            const fn = images[index];
            modalImg.src = fn;
            modalImg.alt = fn;
            const numImg = images.length;
            modalFilename.textContent = fn + " (" + (index + 1) + "/" + numImg + ")";
        }}
        
        function openModal(filename) {{
            const modal = document.getElementById('modal');
            currentIndex = images.indexOf(filename);
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

        document.addEventListener('mousewheel', function(e) {{
            const modal = document.getElementById('modal');
            if (!modal.classList.contains('active')) return;

            if (e.deltaY < 0) {{
                prevImage();
            }} else if (e.deltaY > 0) {{
                nextImage();
            }}
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
                var fn = images[i];
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
                name.innerHTML = fn;
            }}
        }}

        makeGallery();
    </script>
"""

    html_template += f"""\
    
    <!-- モーダル -->
    <div id="modal" class="modal" onclick="closeModal()">
        <span class="close" onclick="closeModal()">&times;</span>
        <div class="nav-button prev" onclick="event.stopPropagation(); prevImage()">＜</div>
        <div class="nav-button next" onclick="event.stopPropagation(); nextImage()">＞</div>
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


def getImages(folder: Path) -> list[str]:
    extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'}

    if not folder.exists() or not folder.is_dir():
        raise ValueError(f"指定されたパスはフォルダではありません: {folder}")

    images = []
    for file in sorted(folder.iterdir()):
        if not file.is_file():
            continue
        if file.suffix.lower() in extensions:
            images.append(file.name)
    
    return images

def buidMain(folder: Path):
    if not folder.is_dir():
        print(f'{folder} is not folder')
        return

    images = getImages(folder)
    if not images:
        print(f"{folder} に画像ファイルが見つかりませんでした")
        return

    html = generatePage(folder, images)

    outFN = folder / "gallery.html"
    with open(outFN, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f'create viewer="{outFN}" images={len(images)}')

def main():
    if len(sys.argv) != 2:
        print(f"使用方法: python {Path(__file__).name} <フォルダパス>")
        return

    buidMain(Path(sys.argv[1]))

if __name__ == "__main__":
    main()
