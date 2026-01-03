'''
# RandomWord

## 概要
- ランダムな英数字の文字列を生成して表示するツール

## 使い方
- スクリプトを実行すると、ランダムな英数字の文字列が複数表示される
- 各文字列は10文字または20文字の長さで生成される
- 日付の接頭辞（YYYYMMDD形式）を付けた文字列も生成される
- ユーザーはEnterキーを押すことで再度文字列を生成でき、'q'を入力すると終了する
'''

import random, string
import datetime


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

def main():
    todayYMD = getTodayYMD()

    while True:
        printRuler()
        printRandom(5, 10, '')
        printRandom(5, 20, '')
        printRandom(5, 10, todayYMD)
        print('')

        if input('Enter to retry (q to quit) >>') == 'q':
            break

if __name__ == "__main__":
    main()
