import config
from fuzzer import preprocess, scheduler, mutator, analyzer
from helper import reporter
from oracle.OracleImport import *
from env import *

PENDING_CONTRACT = []


def set_pending_contract(contract_list=None):
    if isinstance(contract_list, list):
        for con in contract_list:
            PENDING_CONTRACT.append(con)
    else:
        for _, _, files in os.walk(config.CREATIONCODE_PATH):
            for name in files:
                contract_name = name.split(".bin")[0]
                PENDING_CONTRACT.append(contract_name)


def fuzzing(runtime_limit, mutation_batch, max_mutation_epochs, mode) -> dict:
    fuzzing_ans = dict()
    all_fuzzing_contract_num = len(PENDING_CONTRACT)
    all_num = 0
    print("executor:fuzzing need to fuzz "+str(all_fuzzing_contract_num) + " contracts")

    finished_path = os.path.join(config.RES_PATH, "FINISHED_CONTRACTS.log")
    valid_cnt = 0
    with open(finished_path, "a+", newline="") as fin_f:
        for contract_name in PENDING_CONTRACT:
            bug_collection = set()
            all_num += 1
            print("Number: " + str(all_num) + ", " + "Contract: "+str(contract_name))
            for oracle_name in ALL_ORACLE:
                t_start = time.time()
                gp, w3 = preprocess.network_prepare()
                fuzz_context = scheduler.configure(w3, contract_name, mutation_batch)
                tx_epochs = fuzz_context.mutation_epochs
                fuzz_context.set_oracle(oracle_name())
                f_view, f_nonpay, f_pay = preprocess.find_function(fuzz_context.get_contract())
                fuzz_context.set_function_context(f_view, f_nonpay, f_pay)

                token_flag = preprocess.suspect_token(f_view)
                exec_oracle = fuzz_context.get_oracle()
                init_flag = exec_oracle.init_status(fuzz_context)
                if not token_flag or not init_flag:
                    bugitem = analyzer.BugItem("", "", "Not Token Contract") if not token_flag else \
                        analyzer.BugItem("", "", "Not State Mutation Token Contract")
                    bug_collection.add(bugitem)
                    preprocess.network_kill(gp)
                    break
                mutator.init_trans(fuzz_context)
                while time.time() < t_start + runtime_limit and tx_epochs < max_mutation_epochs:
                    execinfo = analyzer.assessment(fuzz_context, bug_collection, mode, contract_name)
                    threshold = int(fuzz_context.get_mutation_batch()/2)
                    mutator.update(fuzz_context, execinfo, threshold, mode, contract_name, max_mutation_epochs)
                    tx_epochs += 1
                    fuzz_context.set_mutation_epochs(tx_epochs)
                preprocess.network_kill(gp)
                valid_cnt += fuzz_context.get_oracle().valid_cnt
                if fuzz_context.halt:
                    break

            if mode == "FORMAL":
                fin_f.writelines([contract_name, "\n"])
                # print(tx_epochs, valid_cnt)
                reporter.res_report(contract_name, bug_collection, tx_epochs, valid_cnt)
            else:
                eval_fin_path = os.path.join(EVALUATION_RES_PATH, "finished.txt")
                with open(eval_fin_path, "a+", newline="") as eval_fin_f:
                    eval_fin_f.writelines([contract_name, "\n"])
            fuzzing_ans[contract_name] = list(bug_collection)
    return fuzzing_ans

