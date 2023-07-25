import os
import sys


__author__ = "Mingpei Cao"
__version__ = "0.1"

ROOT_PATH, _ = os.path.split(os.path.realpath(__file__))
CONTRACTS_PATH = os.path.join(ROOT_PATH, "contracts")
RES_PATH = os.path.join(ROOT_PATH, "result")

ABI_PATH = os.path.join(CONTRACTS_PATH, "abi")
CREATIONCODE_PATH = os.path.join(CONTRACTS_PATH, "creationcode")
SOURCE_PATH = os.path.join(CONTRACTS_PATH, "source")
CONSTRUCOTR_PATH = os.path.join(CONTRACTS_PATH, "constructor")

REPORTS_PATH = os.path.join(ROOT_PATH, "reports")


def set_EVALUATION_PATH(contracts_path):
    glb_dct = sys.modules["__main__"].__dict__
    glb_dct["CONTRACTS_PATH"] = contracts_path
    glb_dct["ABI_PATH"] = os.path.join(contracts_path, "abi")
    glb_dct["CREATIONCODE_PATH"] = os.path.join(contracts_path, "creationcode")
    glb_dct["SOURCE_PATH"] = os.path.join(contracts_path, "source")
    glb_dct["CONSTRUCOTR_PATH"] = os.path.join(contracts_path, "constructor")
    return CONTRACTS_PATH
