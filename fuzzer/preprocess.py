import web3.eth
import config
from helper import utils, deployer
from collections import defaultdict
from env import *


def network_prepare() -> any:
    ganache = utils.network_setting()
    web3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
    return ganache, web3


def network_kill(gp):
    utils.network_kill(gp)


def state_snapshot():
    return deployer.snapshot_state()


def state_revert(id):
    deployer.revert_state(id)


def get_constructor_replace_address(contract_name: str) -> str:
    constructor_path = os.path.join(config.CONSTRUCOTR_PATH, contract_name + ".txt")
    abi_path = os.path.join(config.ABI_PATH, contract_name + ".abi")
    with open(abi_path, "r", encoding="utf-8") as f:
        abi = json.load(f)
    constructor_list = utils.constructor_detect(abi)
    if os.path.exists(constructor_path):
        with open(constructor_path, "r", encoding="utf-8") as con_f:
            constructor_str = con_f.read()
        con_tuple = decode_abi(constructor_list, bytes.fromhex(constructor_str))
        ans_list = []
        for i in range(len(constructor_list)):
            if str(constructor_list[i]).startswith("address"):
                ans_list.append(OWNER_ADDRESS)
            else:
                ans_list.append(con_tuple[i])
        ans_str = encode_abi(constructor_list, ans_list).hex()
        return ans_str
    else:
        logging.info("constructor arguments are None.")
        return ""


def deployed_contract(w3, contract_name, constructor_para, tx_call_para) -> web3.eth.Contract:
    abi_path = os.path.join(config.ABI_PATH, contract_name + ".abi")
    code_path = os.path.join(config.CREATIONCODE_PATH, contract_name + ".bin")
    if os.path.exists(abi_path) and os.path.exists(code_path):
        with open(abi_path, "r", encoding="utf-8") as f:
            abi = json.load(f)
        with open(code_path, "r", encoding="utf-8") as f:
            code = f.read()
        contractInstance = deployer.contract_deployed(w3, abi, code, constructor_para, tx_call_para)
    else:
        logging.warning("preprocess:deployed_contract Missing abi or creation code file. Please check!")
        sys.exit(1)
    return contractInstance


class FunctionItem:
    def __init__(self, name):
        self.method = name
        self.inputs = []
        self.outputs = []
        self.modifier = str()

    def __hash__(self):
        return hash((self.method, str(self.inputs), str(self.outputs)))

    def __eq__(self, other):
        return (self.method, self.inputs) == (other.method, other.inputs)

    def set_inputs(self, inputs_list):
        self.inputs = inputs_list

    def get_inputs(self):
        return self.inputs

    def set_outputs(self, outputs_list):
        self.outputs = outputs_list

    def get_outputs(self):
        return self.outputs

    def get_name(self):
        return self.method

    def set_modifier(self, modifier):
        self.modifier = modifier

    def get_modifier(self):
        return self.modifier


def function_inputs_processing(inputs: list) -> list:
    func_input_list = []
    for inp_dic in inputs:
        inp_type = inp_dic["type"]
        if inp_type == "tuple" or inp_type == "tuple[]":
            func_input_list.append(utils.tuple_dfs(inp_dic))
        else:
            func_input_list.append(inp_type)
    return func_input_list


def find_function(contractInstance: web3.eth.Contract) -> (defaultdict, defaultdict, defaultdict):
    func_view = defaultdict(list)
    func_nonpayable = defaultdict(list)
    func_payable = defaultdict(list)
    for abi_item in contractInstance.abi:
        abi_dict = dict(abi_item)
        if abi_dict["type"] == "function":
            curFuncItem = FunctionItem(abi_dict["name"])
            inputs_list = function_inputs_processing(list(abi_dict["inputs"]))
            outputs_list = function_inputs_processing(list(abi_dict["outputs"]))
            curFuncItem.set_inputs(inputs_list)
            curFuncItem.set_outputs(outputs_list)
            if "stateMutability" in abi_dict:
                if abi_dict["stateMutability"] == "view":
                    func_view[curFuncItem.method].append(curFuncItem)
                elif abi_item["stateMutability"] == "nonpayable":
                    func_nonpayable[curFuncItem.method].append(curFuncItem)
                elif abi_item["stateMutability"] == "payable":
                    func_payable[curFuncItem.method].append(curFuncItem)
            elif "constant" in abi_dict:
                if abi_dict["constant"] == True:
                    func_view[curFuncItem.method].append(curFuncItem)
                else:
                    if "payable" in abi_dict.keys() and abi_dict["payable"] == True:
                        func_payable[curFuncItem.method].append(curFuncItem)
                    else:
                        func_nonpayable[curFuncItem.method].append(curFuncItem)

    return func_view, func_nonpayable, func_payable


def suspect_token(func_view: defaultdict) -> bool:
    if "balanceOf" in func_view:
        func_list = func_view["balanceOf"]
        for func_item in func_list:
            input_list, output_list = func_item.inputs, func_item.outputs
            if input_list == ["address"] and output_list == ["uint256"]:
                return True
    return False


def set_tx_para(role, value):
    role_dict = {}
    if role == "OWNER":
        role_dict["from"] = OWNER_ADDRESS
    elif role == "ATTACKER":
        role_dict["from"] = ATTACKER_ADDRESS
    else:
        role_dict["from"] = USER_ADDRESS
    role_dict["gas"] = 15000000
    role_dict["value"] = value
    return role_dict
