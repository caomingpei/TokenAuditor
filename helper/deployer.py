import web3.eth
from helper import utils
from env import *


# deployed contract with constrctor args, abi, bytecode, constructor
def contract_deployed(w3, abi: dict, code: str, constructor: str, option: dict) -> web3.eth.Contract:
    constructor_list = utils.constructor_detect(abi)
    contract = w3.eth.contract(bytecode=code, abi=abi)
    if not constructor_list:
        tx_hash = contract.constructor().transact(option)
    else:
        decode_ans = decode_abi(constructor_list, bytes.fromhex(constructor))
        cur_lis = []
        for i in range(len(constructor_list)):
            type_cons = constructor_list[i]
            if str(type_cons).startswith("address"):
                address_val = decode_ans[i]
                address_to = []
                if isinstance(address_val, tuple):
                    for address in address_val:
                        address_to.append(w3.toChecksumAddress(address))
                    cur_lis.append(address_to)
                else:
                    cur_lis.append(w3.toChecksumAddress(decode_ans[i]))
            else:
                cur_lis.append(decode_ans[i])
        tx_hash = contract.constructor(*cur_lis).transact(option)

    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    contractInstance = w3.eth.contract(
        address=tx_receipt.contractAddress,
        abi=abi,
    )
    contractInstance.bytecode_runtime = w3.eth.getCode(tx_receipt.contractAddress).hex()[2:]
    return contractInstance


def call_contract(contractInstance: any, function: str, f_para: list, tx_para=None) -> any:
    if not contractInstance:
        logging.warning("deployer:transaction_contract No contract instance")
    methods = contractInstance.functions
    if function not in methods:
        logging.warning("deployer:transaction_contract illegal function name")
    expectcmd = "con" + ".functions." + function
    if f_para:
         expectcmd += "(*"+ "para"+ ")"
    else:
        expectcmd += "()"
    cmd_call = expectcmd+".call("+"option"+")"
    logging.info("deployer:transaction send transaction to contract")
    try:
        if f_para:
            return_val = eval(cmd_call, {"con": contractInstance, "para": f_para, "option": tx_para})
        else:
            return_val = eval(cmd_call, {"con": contractInstance, "option": tx_para})
    except:
        raise ValueError

    return return_val


def transact_contract(w3: any, contractInstance: any, function: str, f_para: list, tx_para=None) -> tuple:
    if not contractInstance:
        logging.warning("deployer:transaction_contract No contract instance")
    methods = contractInstance.functions
    if function not in methods:
        logging.info("deployer:transaction_contract illegal function name")
    expectcmd = "con" + ".functions." + function
    if f_para:
         expectcmd += "(*"+ "para"+ ")"
    else:
        expectcmd += "()"
    cmd_call = expectcmd+".call("+"option"+")"
    cmd_transact = expectcmd+".transact("+"option"+")"
    logging.info("deployer:transaction send transaction to contract")
    try:
        if f_para:
            return_val = eval(cmd_call, {"con": contractInstance, "para": f_para, "option": tx_para})
            tx_hash = eval(cmd_transact, {"con": contractInstance, "para": f_para, "option": tx_para})
        else:
            return_val = eval(cmd_call, {"con": contractInstance, "option": tx_para})
            tx_hash = eval(cmd_transact, {"con": contractInstance, "option": tx_para})
        tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    except:
        raise ValueError

    return return_val, tx_hash, tx_receipt


def safe_transact_contract(w3: any, contractInstance: any, function: str, f_para: list, tx_para=None) -> tuple:
    try:
        return_val, tx_hash, tx_receipt = transact_contract(w3, contractInstance, function, f_para, tx_para)
        return True, return_val, tx_hash
    except ValueError:
        return False, 0, 0


def debug_transaction(tx_hash):
    json_data = {
        'jsonrpc': '2.0',
        'id': 1337,
        'method': 'debug_traceTransaction',
        'params': [str(tx_hash.hex())],
    }
    response = requests.post("http://127.0.0.1:8545", json=json_data)
    response_dict = json.loads(response.text)
    response.close()
    return response_dict["result"]


# return snapshot id
def snapshot_state() -> str:
    json_data = {
        'jsonrpc': '2.0',
        'id': 1337,
        'method': 'evm_snapshot',
        'params': [],
    }
    response = requests.post("http://127.0.0.1:8545", json=json_data)
    response_dict = json.loads(response.text)
    response.close()
    return response_dict["result"]


# revert to state, This deletes the given snapshot, as well as any snapshots taken after
# (Ex: reverting to id 0x1 will delete snapshots with ids 0x1, 0x2, etc... )
def revert_state(id) -> str:
    json_data = {
        'jsonrpc': '2.0',
        'id': 1337,
        'method': 'evm_revert',
        'params': [str(id)],
    }
    response = requests.post("http://127.0.0.1:8545", json=json_data)
    response_dict = json.loads(response.text)
    response.close()
    return response_dict["result"]