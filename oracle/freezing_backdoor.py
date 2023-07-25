from oracle.Factory import OracleFactory
from helper import deployer
from fuzzer.preprocess import set_tx_para
from env import *
from helper.deployer import debug_transaction


class FreezingBackdoor(OracleFactory):
    def __init__(self):
        OracleFactory.__init__(self)
        self.name = "freez"

    def _transfer_check(self, context) -> bool:
        pre_id = deployer.snapshot_state()
        contractInstance = context.get_contract()
        user_call_option = {"from": USER_ADDRESS, "gas": 15000000}
        if self.proposal == "ERC20":
            user_bal = deployer.call_contract(contractInstance, "balanceOf", [USER_ADDRESS], user_call_option)
            if user_bal > 1:
                success, tx_val, tx_hash = deployer.safe_transact_contract(context.web3, contractInstance, "transfer",
                                                                           [OWNER_ADDRESS, random.randint(1, user_bal-1)],
                                                                           user_call_option)
                if success:
                    deployer.revert_state(pre_id)
                    return True

        if self.proposal == "ERC721":
            success, tx_val, tx_hash = deployer.safe_transact_contract(context.web3, contractInstance, "transferFrom",
                                                                       [USER_ADDRESS, OWNER_ADDRESS, self.user_num[0]],
                                                                       user_call_option)
            try:
                address_res = deployer.call_contract(contractInstance, "ownerOf", [self.user_num[0]], user_call_option)
                if success and address_res == OWNER_ADDRESS:
                    deployer.revert_state(pre_id)
                    return True
            except:
                pass

        deployer.revert_state(pre_id)
        return False

    def arbiter(self, context):
        arbiter_ans = []
        self.cur_exec = []
        transaction_list = self.get_transaction_list()
        before_suc = self._transfer_check(context)

        pre_tx = deployer.snapshot_state()
        risk_num = 0
        for tx_dict in transaction_list:
            self.all_tx_dict.append(tx_dict)
            option = set_tx_para(tx_dict["call_role"], tx_dict["value"])
            success, tx_val, tx_hash = deployer.safe_transact_contract(context.web3, context.get_contract(),
                                                                       tx_dict["method"], tx_dict["f_para"], option)
            if self.check_contract(context):
                if success:
                    after_suc = self._transfer_check(context)
                    if before_suc and not after_suc:
                        risk_dict = {"transaction_dict": tx_dict, "risk": "FreezingBackdoor", "index": risk_num}
                        arbiter_ans.append(risk_dict)
                    exec_trace = debug_transaction(tx_hash)
                    self.exec_res.append((tx_dict, exec_trace))
                    self.cur_exec.append((tx_dict, exec_trace))
                    risk_num += 1
                else:
                    self.exec_res.append(("error", "revert"))
            else:
                logging.info("selfdestruct transaction")

            deployer.revert_state(pre_tx)
            pre_tx = deployer.snapshot_state()


        return arbiter_ans

