from oracle.Factory import OracleFactory
from helper import deployer
from env import *
from fuzzer.preprocess import set_tx_para, FunctionItem


class TokenCompatibility(OracleFactory):
    def __init__(self):
        OracleFactory.__init__(self)
        self.set_mode("compatibility")
        self.compat_dict = dict()
        self.func_item_list = list()
        self.name = "comp"

    def _make_item(self, name: str, inputs: list, outputs: list, modifier: str):
        res_func = FunctionItem(name)
        res_func.set_inputs(inputs)
        res_func.set_outputs(outputs)
        res_func.set_modifier(modifier)
        return res_func

    def set_func_item(self):
        if self.proposal == "ERC20":
            erc20_item = [
                ["name", [], ["string"], "view"],
                ["symbol", [], ["string"], "view"],
                ["decimals", [], ["uint8"], "view"],
                ["totalSupply", [], ["uint256"], "view"],
                ["balanceOf", ["address"], ["uint256"], "view"],
                ["transfer", ["address", "uint256"], ["bool"], "nonpayable"],
                ["transferFrom", ["address", "address", "uint256"], ["bool"], "nonpayable"],
                ["approve", ["address", "uint256"], ["bool"], "nonpayable"],
                ["allowance", ["address", "address"], ["uint256"], "nonpayable"],
            ]
            for name, inputs, outputs, modifier in erc20_item:
                self.func_item_list.append(self._make_item(name, inputs, outputs, modifier))

        elif self.proposal == "ERC721":
            erc721_item = [
                ["balanceOf", ["address"], ["uint256"], "view"],
                ["ownerOf", ["uint256"], ["address"], "view"],
                ["safeTransferFrom", ["address", "address", "uint256"], [], "payable"],
                ["transferFrom", ["address", "address", "uint256"], [], "payable"],
                ["approve", ["address", "uint256"], [], "payable"],
                ["setApprovalForAll", ["address", "bool"], [], "nonpayable"],
                ["getApproved", ["uint256"], ["address"], "view"],
                ["isApprovedForAll", ["address", "address"], ["bool"], "view"],
            ]
            for name, inputs, outputs, modifier in erc721_item:
                self.func_item_list.append(self._make_item(name, inputs, outputs, modifier))

    def init_status(self, context) -> bool:
        func_context = context.get_function_context()
        func_view, func_nonpay, func_pay = func_context.get_function_view(), func_context.get_function_nonpayable(), \
                                           func_context.get_function_payable()
        if self.suspect_ERC(func_view, func_nonpay, func_pay):
            if self._find_mint(context) and self.owner_num != 0 and self.user_num != 0:
                # print("detected: ", self.owner_num, self.user_num)
                self.set_func_item()
                return True
            else:
                return False
        else:
            return False

    def arbiter(self, context):
        arbiter_ans = []
        transaction_list = self.get_transaction_list()
        risk_num = 0
        for tx_dict in transaction_list:
            self.all_tx_dict.append(tx_dict)
            option = set_tx_para(tx_dict["call_role"], tx_dict["value"])
            w3, contractInstance= context.web3, context.get_contract()
            modifier, method, f_para = tx_dict["modifier"], tx_dict["method"], tx_dict["f_para"]
            call_option = {"from":OWNER_ADDRESS, "gas": 15000000}
            if modifier == "view":
                success, tx_val, _ = deployer.safe_transact_contract(w3, contractInstance, method, f_para, option)
                if success:
                    if not tx_val:
                        risk_dict = {"transaction_dict": tx_dict,
                                     "risk": "TokenCompatibility-output error:" + str(method),
                                     "index": risk_num}
                        arbiter_ans.append(risk_dict)
                    else:
                        self.compat_dict[method] = True
                else:
                    risk_dict = {"transaction_dict": tx_dict,
                                 "risk": "TokenCompatibility-not specific function:" + str(method),
                                 "index": risk_num}
                    arbiter_ans.append(risk_dict)
            else:
                pre_tx = deployer.snapshot_state()
                if self.proposal == "ERC20":
                    if method == "transfer" or method == "transferFrom":
                        success, tx_val, tx_hash = deployer.safe_transact_contract(w3, contractInstance, method, f_para,
                                                                                   option)
                        if success and tx_val:
                            self.compat_dict[method] = True
                        else:
                            risk_dict = {"transaction_dict": tx_dict,
                                         "risk": "TokenCompatibility-not specific function:" + str(method),
                                         "index": risk_num}
                            arbiter_ans.append(risk_dict)
                    elif method == "approve":
                        approve_val = f_para[1]
                        success, tx_val, tx_hash = deployer.safe_transact_contract(w3, contractInstance, method, f_para,
                                                                                   option)
                        if success:
                            try:
                                view_val = deployer.call_contract(contractInstance, "allowance",
                                                                  [OWNER_ADDRESS, USER_ADDRESS], call_option)
                                if view_val != approve_val:
                                    risk_dict = {"transaction_dict": tx_dict,
                                                 "risk": "TokenCompatibility-output error:" + str(method),
                                                 "index": risk_num}
                                    arbiter_ans.append(risk_dict)
                                else:
                                    self.compat_dict[method] = True
                            except:
                                risk_dict = {"transaction_dict": tx_dict,
                                             "risk": "TokenCompatibility-not specific function: allowance",
                                             "index": risk_num}
                                arbiter_ans.append(risk_dict)

                        else:
                            risk_dict = {"transaction_dict": tx_dict,
                                         "risk": "TokenCompatibility-not specific function:" + str(method),
                                         "index": risk_num}
                            arbiter_ans.append(risk_dict)

                    deployer.revert_state(pre_tx)

                elif self.proposal == "ERC721":
                    if method == "safeTransferFrom" or method == "transferFrom":
                        transid = f_para[2]

                        success, tx_val, tx_hash = deployer.safe_transact_contract(w3, contractInstance, method, f_para,
                                                                                   option)
                        if success:
                            control_addr = deployer.call_contract(contractInstance, "ownerOf", [transid], call_option)
                            if control_addr != f_para[1]:
                                risk_dict = {"transaction_dict": tx_dict,
                                             "risk": "TokenCompatibility-output error:" + str(method),
                                             "index": risk_num}
                                arbiter_ans.append(risk_dict)
                            else:
                                self.compat_dict[method] = True
                        else:
                            risk_dict = {"transaction_dict": tx_dict,
                                         "risk": "TokenCompatibility-not specific function:" + str(method),
                                         "index": risk_num}
                            arbiter_ans.append(risk_dict)
                    elif method == "approve":
                        approve_addr, approve_val = f_para[0], f_para[1]
                        success, tx_val, tx_hash = deployer.safe_transact_contract(w3, contractInstance, method, f_para,
                                                                                   option)
                        if success:
                            try:
                                view_addr = deployer.call_contract(contractInstance, "getApproved", [approve_val],
                                                                   call_option)
                                if view_addr != approve_addr:
                                    risk_dict = {"transaction_dict": tx_dict,
                                                 "risk": "TokenCompatibility-output error:" + str(method),
                                                 "index": risk_num}
                                    arbiter_ans.append(risk_dict)
                                else:
                                    self.compat_dict[method] = True
                            except:
                                risk_dict = {"transaction_dict": tx_dict,
                                             "risk": "TokenCompatibility-not specific function: allowance",
                                             "index": risk_num}
                                arbiter_ans.append(risk_dict)
                        else:
                            risk_dict = {"transaction_dict": tx_dict,
                                         "risk": "TokenCompatibility-not specific function:" + str(method),
                                         "index": risk_num}
                            arbiter_ans.append(risk_dict)

                    elif method == "setApprovalForAll":
                        approve_flag = f_para[1]
                        if approve_flag:
                            success, tx_val, tx_hash = deployer.safe_transact_contract(w3, contractInstance, method,
                                                                                       f_para, option)
                            if success:
                                try:
                                    approve_return = deployer.call_contract(contractInstance, "isApprovedForAll",
                                                                            [OWNER_ADDRESS, USER_ADDRESS], call_option)
                                    if not approve_return:
                                        risk_dict = {"transaction_dict": tx_dict,
                                                     "risk": "TokenCompatibility-output error:" + str(method),
                                                     "index": risk_num}
                                        arbiter_ans.append(risk_dict)
                                    else:
                                        self.compat_dict[method] = True
                                except:
                                    risk_dict = {"transaction_dict": tx_dict,
                                                 "risk": "TokenCompatibility-not specific function: isApprovedForAll",
                                                 "index": risk_num}
                                    arbiter_ans.append(risk_dict)
                            else:
                                risk_dict = {"transaction_dict": tx_dict,
                                             "risk": "TokenCompatibility-not specific function:" + str(method),
                                             "index": risk_num}
                                arbiter_ans.append(risk_dict)

                    deployer.revert_state(pre_tx)
            risk_num += 1

        return arbiter_ans
