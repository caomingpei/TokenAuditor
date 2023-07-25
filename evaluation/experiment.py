import sys
sys.path.append("..")
from config import *
from env import *
from fuzzer import executor

if __name__ == "__main__":
    print("hello, experiment")
    EVALUATION_PATH, _ = os.path.split(os.path.realpath(__file__))
    test_file_name = os.path.join(EVALUATION_PATH, "test.txt")
    finished_file = os.path.join(EVALUATION_PATH, "finished.txt")
    risk_folder_path = os.path.join(EVALUATION_RES_PATH, "risk")
    newbug_folder_path = os.path.join(EVALUATION_RES_PATH, "newbug")
    candidate_folder_path = os.path.join(EVALUATION_RES_PATH, "candidate")

    if not os.path.exists(risk_folder_path):
        os.makedirs(risk_folder_path)
    if not os.path.exists(newbug_folder_path):
        os.makedirs(newbug_folder_path)
    if not os.path.exists(candidate_folder_path):
        os.makedirs(candidate_folder_path)

    PENDING_CONTRACT = []
    fin_contract = set()
    with open(finished_file, "r", encoding="utf-8") as fin_f:
        for fin_name in fin_f.readlines():
            fin_contract.add(fin_name.split("\n")[0])

    for _, _, files in os.walk(CREATIONCODE_PATH):
        for name in files:
            contract_name = name.split(".bin")[0]
            if contract_name not in fin_contract:
                PENDING_CONTRACT.append(contract_name)

    executor.set_pending_contract(PENDING_CONTRACT)

    with open(finished_file, "a+", encoding="utf-8") as fin_f:

        with open(test_file_name, "a+", encoding="utf-8") as w_f:
            ans = executor.fuzzing(10000000000000000, 50, 3, "EXPERIMENT")
            for k, v in ans.items():
                for r in v:
                    w_f.writelines([str(k), ",", str(r.risk), "\n"])
