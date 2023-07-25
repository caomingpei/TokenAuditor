import sys
sys.path.append("..")
from config import *
from helper import deployer


def _test_contract_deployed(project_name, path=os.path.join("scripts", "example.py")):
    ans = deployer.contract_deployed(path, project_name)
    return ans


def _test_transaction_contract(contract: any, function: str, f_para: list, tx_para: dict):
    ans = deployer.transaction_contract(contract, function, f_para, tx_para)
    return ans
