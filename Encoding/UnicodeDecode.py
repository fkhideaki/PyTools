import pyperclip
import re

def mainproc():
    s = pyperclip.paste()
    ss = s.encode().decode('unicode-escape')
    print('')
    print('----------------------------------------')
    print('', ss)
    print('----------------------------------------')
    input()

mainproc()
