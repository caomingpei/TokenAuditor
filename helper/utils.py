from env import *


def network_setting():
    default_ETH = "1000000000000000000000000000000000000000"
    ganache_cmd = "ganache-cli --chain.vmErrorsOnRPCResponse true " \
                  "--server.host 127.0.0.1 --port 8545 " \
                  "--miner.blockGasLimit 15000000 " \
                  "--miner.defaultGasPrice 0x0 --hardfork london " \
                  "--account='"+str(ATTACKER_PRIVATE_KEY)+","+str(default_ETH) +"' " \
                  "--account='"+str(OWNER_PRIVATE_KEY)+","+str(default_ETH)+"' "\
                  "--account='"+str(USER_PRIVATE_KEY)+","+str(default_ETH)+"' "
    logging.info(ganache_cmd)
    ganache_process = subprocess.Popen(ganache_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
    while ganache_process:
        return ganache_process


def network_kill(process: any):
    time.sleep(1)
    process = psutil.Process(process.pid)
    for proc in process.children(recursive=True):
        proc.kill()
    process.kill()


def tuple_dfs(abi_dict: dict) -> list:
    type_list = []
    for dic in abi_dict["components"]:
        if dic["type"] == "tuple" or dic["type"] == "tuple[]":
            type_list.append(tuple_dfs(dic))
        else:
            type_list.append(dic["type"])
    return list(type_list)


def constructor_detect(load_json: dict) -> list:
    constructor_type = []
    for dic in load_json:
        if dic["type"] == "constructor":
            inputs = dic["inputs"]
            for inp_dic in inputs:
                inp_type = inp_dic["type"]
                if inp_type == "tuple" or inp_type == "tuple[]":
                    constructor_type.append(tuple_dfs(inp_dic))
                else:
                    constructor_type.append(inp_type)
    logging.info("utils: constructor_detect build list[type]")
    return list(constructor_type)


