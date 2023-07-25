from fuzzer import generator
from helper import deployer
from env import *
from fuzzer.preprocess import set_tx_para


class OracleFactory:
    def __init__(self):
        self.name = str()
        self.mode = "normal"
        self.transaction_list = list()
        self.exec_res = list()
        self.block_set = set()
        self.owner_num = list()
        self.user_num = list()
        self.proposal = str()
        self.cur_exec = list()
        self.all_tx_dict = list()
        self.valid_cnt = 0

    def set_mode(self, mode):
        self.mode = mode

    def get_mode(self):
        return self.mode

    def add_transaction_list(self, item):
        self.transaction_list.append(item)

    def set_transaction_list(self, transaction_list):
        self.transaction_list = transaction_list

    def get_transaction_list(self):
        return self.transaction_list

    def set_exec_res(self, exec_res):
        self.exec_res = exec_res

    def get_exec_res(self):
        return self.exec_res

    def add_block_set(self, function_item):
        self.block_set.add(function_item)

    def get_block_set(self):
        return self.block_set

    def get_cur_exec(self):
        return self.cur_exec

    def get_all_tx_dict(self):
        return self.all_tx_dict

    def set_all_tx_dict(self, all_tx_dict):
        self.all_tx_dict = all_tx_dict

    def arbiter(self, context):
        pass

    def suspect_ERC(self, func_view, func_nonpay, func_pay) -> bool:
        erc20_list = ["balanceOf", "transfer"]
        erc721_list = ["balanceOf", "ownerOf", "transferFrom"]
        erc20_dict = dict(zip(erc20_list, [False for _ in range(len(erc20_list))]))
        erc721_dict = dict(zip(erc721_list, [False for _ in range(len(erc721_list))]))
        for k, func_list in func_view.items():
            for func_item in func_list:
                if func_item.method in erc20_dict:
                    erc20_dict[func_item.method] = True
                if func_item.method in erc721_dict:
                    erc721_dict[func_item.method] = True
        for k, func_list in func_nonpay.items():
            for func_item in func_list:
                if func_item.method in erc20_dict:
                    erc20_dict[func_item.method] = True
                if func_item.method in erc721_dict:
                    erc721_dict[func_item.method] = True
        for k, func_list in func_pay.items():
            for func_item in func_list:
                if func_item.method in erc20_dict:
                    erc20_dict[func_item.method] = True
                if func_item.method in erc721_dict:
                    erc721_dict[func_item.method] = True

        if not (False in erc721_dict.values()):
            self.proposal = "ERC721"
            return True
        elif not (False in erc20_dict.values()):
            self.proposal = "ERC20"
            return True
        else:
            return False

    def _event_token(self, contractInstance, option):
        try:
            event_filter = contractInstance.events.Transfer.createFilter(fromBlock="latest")
            mint_event_list = event_filter.get_all_entries()
            owner_ids = []
            for event in mint_event_list:
                event_val = list(event["args"].values())
                if event_val[0] == "0x0000000000000000000000000000000000000000" and event_val[1] == option["from"]:
                    owner_ids.append(event_val[2])
            return owner_ids
        except:
            logging.info("oracle:Factory not event_token")
            return []

    def _find_mint(self, context) -> bool:
        contractInstance = context.get_contract()
        call_option = {"from": OWNER_ADDRESS, "gas": 15000000}
        init_balance = deployer.call_contract(context.get_contract(), "balanceOf", [OWNER_ADDRESS], call_option)
        if init_balance > 3 and self.proposal == "ERC20":
            send_uint = int(init_balance / 3)
            sender_option = {'from': OWNER_ADDRESS, 'gas': 15000000}
            try:
                deployer.safe_transact_contract(context.web3, contractInstance, "transfer",
                                                [USER_ADDRESS, send_uint], sender_option)
                self.owner_num = init_balance - send_uint
                self.user_num = send_uint
                return True
            except:
                return False
        else:
            pre_id = deployer.snapshot_state()
            func_context = context.get_function_context()
            func_nonpay, func_pay = func_context.get_function_nonpayable(), func_context.get_function_payable()
            func_item_list = []
            for k, func_list in func_nonpay.items():
                for func_item in func_list:
                    func_item_list.append((func_item, "nonpayable"))
            for k, func_list in func_pay.items():
                for func_item in func_list:
                    func_item_list.append((func_item, "payable"))

            for func_tup in func_item_list:
                tx_dict = generator.generate_limit_tx_dict(func_tup[0], func_tup[1], "OWNER", "OWNER", 100)
                option = set_tx_para(tx_dict["call_role"], tx_dict["value"])
                success, _, _ = deployer.safe_transact_contract(context.web3, contractInstance,
                                                                tx_dict["method"], tx_dict["f_para"], option)
                if self.check_contract(context):
                    if success and self.proposal == "ERC20":
                        after_balance = deployer.call_contract(context.get_contract(), "balanceOf", [OWNER_ADDRESS],
                                                               call_option)
                        if after_balance - init_balance > 3:
                            deployer.revert_state(pre_id)
                            deployer.safe_transact_contract(context.web3, contractInstance, tx_dict["method"],
                                                            tx_dict["f_para"], option)
                            true_balance = deployer.call_contract(context.get_contract(), "balanceOf",
                                                                  [OWNER_ADDRESS], call_option)
                            send_uint = int(true_balance / 3)
                            deployer.safe_transact_contract(context.web3, contractInstance, "transfer",
                                                            [USER_ADDRESS, send_uint], option)
                            self.owner_num = true_balance - send_uint
                            self.user_num = send_uint
                            return True
                    elif success and self.proposal == "ERC721":
                        owner_ids = []
                        owner_ids.extend(self._event_token(contractInstance, option))
                        if len(owner_ids) >= 2:
                            deployer.safe_transact_contract(context.web3, contractInstance, "transferFrom",
                                                            [OWNER_ADDRESS, USER_ADDRESS, owner_ids[0]], option)
                            self.owner_num = owner_ids[1:]
                            self.user_num = [owner_ids[0]]
                            return True
                        elif len(owner_ids) == 1:
                            tx_new = generator.generate_limit_tx_dict(func_tup[0], func_tup[1], "OWNER", "OWNER", 100)
                            option = set_tx_para(tx_new["call_role"], tx_new["value"])
                            deployer.safe_transact_contract(context.web3, contractInstance, tx_new["method"],
                                                            tx_new["f_para"], option)
                            owner_ids.extend(self._event_token(contractInstance, option))
                            deployer.safe_transact_contract(context.web3, contractInstance, "transferFrom",
                                                            [OWNER_ADDRESS, USER_ADDRESS, owner_ids[0]], option)
                            self.owner_num = owner_ids[1:]
                            self.user_num = [owner_ids[0]]
                            return True

            return False

    def init_status(self, context) -> bool:
        func_context = context.get_function_context()
        func_view, func_nonpay, func_pay = func_context.get_function_view(), func_context.get_function_nonpayable(), \
                                           func_context.get_function_payable()
        if self.suspect_ERC(func_view, func_nonpay, func_pay):
            if self._find_mint(context):
                if self.proposal == "ERC20" and self.owner_num != 0 and self.user_num != 0:
                    return True
                elif self.proposal == "ERC721" and len(self.owner_num) >= 1 and len(self.user_num) >= 1:
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False

    def check_contract(self, context) -> bool:
        w3 = context.web3
        contractInsance = context.get_contract()
        code = w3.eth.getCode(contractInsance.address)
        if len(code) > len("0x"):
            return True
        else:
            return False
