'''
# GeneratePattern

## 概要
特定のパターンに基づいて文字列を生成するスクリプト。

## 使い方
1. `pattern` 変数に生成したい文字列のパターン。プレースホルダー `$0`, `$1`, `$2` を使用可。
2. `words0`, `words1`, `words2` リストにそれぞれのプレースホルダーに対応する文字列のリスト。
3. スクリプトを実行すると、指定したパターンに基づいて全ての組み合わせの文字列が生成され、出力される。
'''


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


for w0 in words0 or ['']:
    for w1 in words1 or ['']:
        for w2 in words2 or ['']:
            result = pattern.replace('$0', w0).replace('$1', w1).replace('$2', w2)
            print(result)
