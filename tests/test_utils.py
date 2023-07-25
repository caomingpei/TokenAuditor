import sys
sys.path.append("..")
from config import *
from helper import utils


def _test_constructor_detect(path):
    ans = utils.constructor_detect(path)
    return ans


def _test_get_chain():
    chain = utils.get_chain()
    return chain


if __name__ == "__main__":
    filename = "example"
    test_path = os.path.join(ABI_PATH, filename+".json")
    print(_test_constructor_detect(test_path))