import os
import sys
sys.path.append("..")
from config import *
from fuzzer import generator
from helper import deployer, utils
from fuzzer import preprocess
from env import *





if __name__ == "__main__":
    ganache, web3 = preprocess.network_prepare()
    abi_ERC20_path = ERC20_ABI_PATH
    bytecode_ERC20_path = ERC20_CREATIONCODE_PATH
    constructor_ERC20_path = ERC20_CONSTRUCTOR_PATH
    write_file = open("function_call_test.txt", "w", encoding="utf=8")
    cnt = 0
    fin = 0
    already_list = open("already_test.txt", "w", encoding="utf=8")
    for _, _, file_name in os.walk(abi_ERC20_path):
        for f_name in file_name:
            fin += 1
            if fin % 100 == 0:
                print("have been finished: "+ str(fin))
            name = f_name.split(".")[0]
            abi_f = os.path.join(abi_ERC20_path, name+".abi")
            byt_f = os.path.join(bytecode_ERC20_path, name + ".bin")
            con_f = os.path.join(constructor_ERC20_path, name + ".txt")

            ganache, web3 = preprocess.network_prepare()

            with open(abi_f, 'r') as f:
                abi = json.load(f)
            with open(byt_f, 'r') as f:
                code = f.read()
            with open(con_f, 'r') as f:
                constructor = f.read()

            account = web3.eth.accounts[0]
            option = {'from': account, 'gas': 15000000}
            contractInstance = deployer.contract_deployed(web3, abi, code, constructor, option)

            #print(name)
            func_view, func_nonpayable, func_payable = preprocess.find_function(contractInstance)
            # for k, func_list in func_nonpayable.items():
            #     for func in func_list:
            #         print("name: ", func.method)
            #         print("inputs: ", func.inputs)
            #         print("outputs: ", func.outputs)
            # myreturn_val= contractInstance.functions.genCuint([1, 5]).transact(option)
            # print("test_val: ", myreturn_val)
            for k, func_list in func_view.items():
                for func_item in func_list:
                    try:
                        generate_list = generator.generate_template(func_item.inputs, "OWNER")
                        # print(func_item.inputs)
                        # print(generate_list)
                        myreturn_val, mytx_hash, mytx_receipt = deployer.transact_contract(web3, contractInstance,
                                                                                             func_item.method,
                                                                                             generate_list, option)
                        # print("val: ", myreturn_val)
                        # print("hash: ", mytx_hash)
                        # print("receipt: ", mytx_receipt)
                        # print("===================================")
                        already_list.writelines([str(func_item.inputs),"\n"])
                    except:
                        cnt += 1
                        write_file.writelines([name, str(func_item.method), str(func_item.inputs), "\n"])
                        print(cnt)
            utils.network_kill(ganache)
    already_list.close()
    write_file.close()
