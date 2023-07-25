import sys
sys.path.append("..")
from fuzzer import preprocess
import os
from config import *

if __name__ == "__main__":
    for _, _, f_n in os.walk(ABI_PATH):
        for fname in f_n:
            name = fname.split(".")[0]
            print(preprocess.get_constructor(name))