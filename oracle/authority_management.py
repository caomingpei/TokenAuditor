from oracle.Factory import OracleFactory
from helper import deployer
from fuzzer.preprocess import set_tx_para
from env import *
from helper.deployer import debug_transaction


class AuthorityManagement(OracleFactory):
    def __init__(self):
        OracleFactory.__init__(self)
        self.name = "author"
    def _balance_check(self, context):
        contractInstance = context.get_contract()
        call_option = {"from": OWNER_ADDRESS, "gas": 15000000}
        if self.proposal == "ERC20":
            owner_bal = deployer.call_contract(contractInstance, "balanceOf", [OWNER_ADDRESS], call_option)
            user_bal = deployer.call_contract(contractInstance, "balanceOf", [USER_ADDRESS], call_option)
            return owner_bal, user_bal
        elif self.proposal == "ERC721":
            nft_list = self.owner_num + self.user_num
            own_bal, user_bal = 0, 0
            try:
                for nft_id in nft_list:
                    return_addr = deployer.call_contract(contractInstance, "ownerOf", [nft_id], call_option)
                    if return_addr == OWNER_ADDRESS:
                        own_bal += 1
                    elif return_addr == USER_ADDRESS:
                        user_bal += 1
                return own_bal, user_bal
            except:
                pass
        return 0, 0

    def arbiter(self, context):
        self.cur_exec = []
        arbiter_ans = []
        transaction_list = self.get_transaction_list()
        owner_t, user_t = self._balance_check(context)

        pre_tx = deployer.snapshot_state()
        risk_num = 0
        for tx_dict in transaction_list:
            self.all_tx_dict.append(tx_dict)
            call_role = "ATTACKER" if tx_dict["call_role"] != "OWNER" else "OWNER"
            option = set_tx_para(call_role, tx_dict["value"])
            method = tx_dict["method"]
            success, tx_val, tx_hash = deployer.safe_transact_contract(context.web3, context.get_contract(), method,
                                                                       tx_dict["f_para"], option)
            if self.check_contract(context):
                if success:
                    after_owner, after_user = self._balance_check(context)
                    if after_owner > owner_t and after_user < user_t:
                        exp_role = "owner" if call_role == "OWNER" else "other user"
                        risk_dict = {"transaction_dict": tx_dict, "risk": "AuthorityManagement-" + str(exp_role)
                                                                          + ":" + str(method), "index": risk_num}
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
