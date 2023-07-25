import sys
sys.path.append("../../")
from env import *
from helper import utils
from helper import deployer


OWNER_PRIVATE_KEY = "0x18ffb39958a9c3d9d885518a78393162ae9508688ca382015d07ed10ad8c2315"
OWNER_ADDRESS = "0x000000ACABf52abb95cA39fCCb42416cAb20cDDB"
USER_PRIVATE_KEY = "0x149a5a963103ac553c26368edafc55e6a3bc7634ef1ddd2bd869fc7f5c98133b"
USER_ADDRESS = "0xaAAA22497257c94996181c3ca2DAcE834Ee61d09"


def network_init():
    default_ETH = "1000000000000000000000000000000000000000"
    ganache_cmd = "ganache-cli --chain.vmErrorsOnRPCResponse true --server.port 8545 --miner.blockGasLimit 15000000 " \
                  "--gasPrice 0 --hardfork istanbul " \
                  "--account='"+str(OWNER_PRIVATE_KEY)+","+str(default_ETH)+"' "\
                  "--account='"+str(USER_PRIVATE_KEY)+","+str(default_ETH)+"' "
    # print(ganache_cmd)
    ganache_process = subprocess.Popen(ganache_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    time.sleep(1)
    return ganache_process


def network_kill(process: any):
    time.sleep(1)
    process = psutil.Process(process.pid)
    for proc in process.children(recursive=True):
        proc.kill()
    process.kill()


def web3_init():
    web3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545', request_kwargs={'timeout':60}))
    # print(web3.isConnected())
    return web3


if __name__ == "__main__":

    cnt = 0
    address_list = []
    num = 0
    for _, _, files_name in os.walk(ERC20_ABI_PATH):
        for f_name in files_name:
            name = f_name.split(".")[0]
            abi_p = os.path.join(ERC20_ABI_PATH, f_name)
            con_p = os.path.join(ERC20_CONSTRUCTOR_PATH, name+".txt")
            cre_p = os.path.join(ERC20_CREATIONCODE_PATH, name+".txt")

            with open(abi_p, 'r') as f:
                abi = json.load(f)

            with open(cre_p, 'r') as f:
                code = f.read()

            with open(con_p, "r") as f:
                constructor_input = f.read()

            constructor_list = utils.constructor_detect(abi)

            gp = network_init()

            web3 = web3_init()
            account = web3.eth.accounts[0]
            num += 1
            if num % 20 == 0:
                print("process: "+str(num))
            try:
                option = {'from': account, 'gas': 15000000}
                contractInsatce = deployer.contract_deployed(web3, abi, code, constructor_input, option)
                if not web3.eth.getCode(contractInsatce.address).hex():
                    cnt += 1
                print(contractInsatce.address)
            except:
                address_list.append(name)
                print(name)
                cnt += 1

            network_kill(gp)

