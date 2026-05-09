'''
# RandomWord

## 概要
- ランダムな英数字の文字列を生成して表示するツール

## 使い方
- スクリプトを実行すると、ランダムな英数字の文字列が複数表示される
- 各文字列は10文字または20文字の長さで生成される
- 日付の接頭辞（YYYYMMDD形式）を付けた文字列も生成される
- ユーザーはEnterキーを押すことで再度文字列を生成でき、'q'を入力すると終了する

## コマンド
- python RandomWord.py [options]
- options:
  - --clip
    - リスト表示ではなくクリップボードに直接生成結果をセットする  
      名称の入力を受けて  
      日時_入力名_ランダム  
      という形式で出力する
'''

import random, string
import datetime
import sys

import pyperclip


def rw(n):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=n))

def getTodayYMD():
    d = datetime.datetime.now()
    return d.strftime('%Y%m%d')

def printRuler():
    print('''
--------------------
_123456789_123456789
--------------------''')

def printRandom(count, length, prefix):
    for i in range(count):
        r = rw(length)
        if prefix:
            print(f'{prefix}_{r}')
        else:
            print(r)
    print('--------------------')

def print_mode():
    todayYMD = getTodayYMD()

    while True:
        printRuler()
        printRandom(5, 10, '')
        printRandom(5, 20, '')
        printRandom(5, 10, todayYMD)
        print('')

        if input('Enter to retry (q to quit) >>') == 'q':
            break

def clip_mode():
    todayYMD = getTodayYMD()
    name = input('name >> ')
    r = rw(10)
    if name:
        s = f'{todayYMD}_{name}_{r}'
    else:
        s = f'{todayYMD}_{r}'
    pyperclip.copy(s)
    print(s)

def main():
    opt = sys.argv[1:]
    clip = '--clip' in opt
    if clip:
        clip_mode()
    else:
        print_mode()


if __name__ == "__main__":
    main()
