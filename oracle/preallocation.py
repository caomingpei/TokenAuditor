from env import *
from oracle.Factory import OracleFactory
from helper import deployer
from fuzzer.preprocess import set_tx_para, FunctionItem
from fuzzer.generator import generate_limit
from helper.deployer import debug_transaction


class PreAllocation(OracleFactory):
    def __init__(self):
        OracleFactory.__init__(self)
        self.name = "prea"

    def init_status(self, context) -> bool:
        return True

    def arbiter(self, context):
        arbiter_ans = []
        self.cur_exec = []
        call_option = {"from": OWNER_ADDRESS, "gas": 15000000}
        try:
            init_balance = deployer.call_contract(context.get_contract(), "balanceOf", [OWNER_ADDRESS], call_option)
            pre_tx = deployer.snapshot_state()
            transaction_list = self.get_transaction_list()

            risk_num = 0
            for tx_dict in transaction_list:
                self.all_tx_dict.append(tx_dict)
                option = set_tx_para(tx_dict["call_role"], tx_dict["value"])
                success, tx_val, tx_hash = deployer.safe_transact_contract(context.web3, context.get_contract(),
                                                                           tx_dict["method"], tx_dict["f_para"], option)
                if self.check_contract(context):
                    after_balance = deployer.call_contract(context.get_contract(), "balanceOf", [OWNER_ADDRESS], call_option)
                    if success:
                        exec_trace = debug_transaction(tx_hash)
                        self.exec_res.append((tx_dict, exec_trace))
                        self.cur_exec.append((tx_dict, exec_trace))
                        risk_num += 1
                    else:
                        self.exec_res.append(("error", "revert"))

                    if after_balance > init_balance:
                        deployer.revert_state(pre_tx)
                        pre_tx = deployer.snapshot_state()
                        gen_fpara = generate_limit(tx_dict["inputs"], "USER")
                        after_option = set_tx_para("USER", 0)
                        user_success, sec_val, sec_hash = deployer.safe_transact_contract(context.web3, context.get_contract(),
                                                                                         tx_dict["method"], gen_fpara, after_option)
                        if not user_success:
                            block_item = FunctionItem(tx_dict["method"])
                            block_item.set_inputs(tx_dict["inputs"])
                            block_item.set_outputs(tx_dict["outputs"])
                            self.add_block_set(block_item)
                            risk_dict = {"transaction_dict": tx_dict, "risk": "PreAllocation", "index": risk_num}
                            arbiter_ans.append(risk_dict)
                else:
                    logging.info("selfdestruct transaction")

                deployer.revert_state(pre_tx)
                pre_tx = deployer.snapshot_state()

        except:
            context.set_halt(True)
            logging.info("balanceOf not support")

        return arbiter_ans
