"""
# ListBuilder.py

## 概要
- 指定されたフォルダ内の画像ファイルを一覧表示するHTMLページを生成する

## 使用方法
- python ListBuilder.py <フォルダパス>
"""

import sys
from pathlib import Path

def generatePage(folder_path: Path, images: list[str]):
    folder_name = folder_path.name
    title = f'{folder_name}'
    
    html_template = f"""\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        .container {{
            display: flex;
            flex-direction: row;
            flex-wrap: wrap;
        }}
        .container > div {{
            border : 1px solid #eee;
            padding : 0.8rem;
            margin : 0.2rem;
        }}
        .main-img {{
            max-width: 90dvw;
        }}
    </style>
</head>
<body>
<div class="container">
"""

    for i, image_file in enumerate(images):
        html_template += f'''\
<div>
    {image_file}<br>
    <img class="main-img" src="{image_file}"/>
</div>
'''

    html_template += """
</div>
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

    outFN = folder / "list.html"
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
