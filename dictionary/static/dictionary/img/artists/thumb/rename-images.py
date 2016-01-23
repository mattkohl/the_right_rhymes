__author__ = 'MBK'


import os


files = os.listdir()

for file in files:
    tmp = file.replace('_', '-').lower()
    if tmp not in files:
        os.rename(file, tmp)