import sys
sys.path.append("..")
import config
from fuzzer import executor
from env import *


def check_dirs():
    candidate_path = os.path.join(EVALUATION_RES_PATH, "candidate")
    hit_path = os.path.join(EVALUATION_RES_PATH, "hit")
    newbug_path = os.path.join(EVALUATION_RES_PATH, "newbug")
    risk_path = os.path.join(EVALUATION_RES_PATH, "risk")
    dirs_list = [candidate_path, hit_path, newbug_path, risk_path]
    for cur_dir in dirs_list:
        if not os.path.exists(cur_dir):
            os.makedirs(cur_dir)
    open(os.path.join(EVALUATION_RES_PATH, "finished.txt"), "a")


if __name__ == "__main__":
    print("hello, experiment")
    EVALUATION_CONTRACTS_PATH = os.path.join(EVALUATION_DATASET_PATH, "C594")

    def set_PATH(contracts_path):
        config.CONTRACTS_PATH = contracts_path
        config.ABI_PATH = os.path.join(contracts_path, "abi")
        config.CREATIONCODE_PATH = os.path.join(contracts_path, "creationcode")
        config.SOURCE_PATH = os.path.join(contracts_path, "source")
        config.CONSTRUCOTR_PATH = os.path.join(contracts_path, "constructor")

    set_PATH(EVALUATION_CONTRACTS_PATH)

    check_dirs()

    fin_contract = set()
    with open(os.path.join(EVALUATION_RES_PATH, "finished.txt"), "r") as r_f:
        for line in r_f.readlines():
            fin_contract.add(line.strip("\n"))
    print(config.CREATIONCODE_PATH)
    for _, _, files in os.walk(config.CREATIONCODE_PATH):
        for name in files:
            contract_name = name.split(".bin")[0]
            if contract_name not in fin_contract:
                executor.PENDING_CONTRACT.append(contract_name)

    ans = executor.fuzzing(10000000000000000, 50, 3, "EXPERIMENT")
