from helper import pathway
from env import *


class BugItem:
    def __init__(self, method, transaction, risk):
        self.method = method
        self.transaction = transaction
        self.risk = risk

    def __hash__(self):
        return hash((self.method, self.risk))

    def __eq__(self, other):
        if self.method == other.method and self.risk == other.risk:
            return True
        else:
            return False


def cal_rare(context, w_f):
    Y_least = 0.2
    all_hit_dict = context.accumulate_hit
    min_tag, min_val = "-1", float("inf")
    rare_tag = []
    history_hit = []
    for k, v in all_hit_dict.items():
        if v == 0:
            continue
        else:
            history_hit.append(v)
            if v < min_val:
                min_tag, min_val = k, v
    history_hit = sorted(history_hit)
    Y_min = history_hit[int(len(history_hit)*Y_least)]
    w_f.writelines(["rarity:", str(min_val), "\n"])
    w_f.writelines(["Y_least_min:", str(Y_min), "\n"])
    if min_val != float("inf"):
        i, acc = 0, 2**0
        left_val, right_val = 0, 1
        while acc <= min_val:
            i += 1
            acc *= 2
        if i > 0:
            left_val = int(pow(2, i-1))
            right_val = min(int(pow(2, i)), int(Y_min))
        for k, v in all_hit_dict.items():
            if v > left_val and v <= right_val:
                rare_tag.append(k)
    return rare_tag


def assessment(context, bug_collection: set, mode, contract_name):
    execinfo = []
    con_oracle = context.get_oracle()
    risk_list = con_oracle.arbiter(context)

    path_r = os.path.join(os.path.join(EVALUATION_RES_PATH, "risk"), str(contract_name)+"_"+str(con_oracle.name)+".txt")
    path_n = os.path.join(os.path.join(EVALUATION_RES_PATH, "newbug"), str(contract_name) + "_" +
                          str(con_oracle.name)+".txt")

    if risk_list:
        for risk_item in risk_list:
            tx_dict = risk_item["transaction_dict"]
            bug = BugItem(tx_dict["method"], tx_dict, risk_item["risk"])
            risk_index = risk_item["index"]
            if bug not in bug_collection and mode == "EXPERIMENT" :
                with open(path_n, "a+", newline="") as new_f:
                    new_f.writelines([str(context.get_mutation_epochs()), ",", str(risk_index), "\n"])
            bug_collection.add(bug)
            if mode == "EXPERIMENT":
                with open(path_r, "a+", newline="") as risk_f:
                    risk_f.writelines([str(context.get_mutation_epochs()), ",", str(risk_index), "\n"])
                ## print("risk:"+ str(risk_index))

    pc_dict = context.get_buildblock()
    batch_hitans = []
    exec_list = con_oracle.get_exec_res()
    cur_exec_list = con_oracle.get_cur_exec()
    rare_tag_list = []

    try:
        save_dirs = os.path.join(os.path.join(EVALUATION_RES_PATH, "hit"), str(contract_name)+"_"+str(con_oracle.name))
        if not os.path.exists(save_dirs):
            os.makedirs(save_dirs)
        path = os.path.join(save_dirs, contract_name + "_" + str(context.get_mutation_epochs()) + ".txt")
        
        for tx_dict, exec_item in cur_exec_list:
            if tx_dict != "error":
                hit_cnt = pathway.calculate_target(pc_dict, exec_item)
                for k, v in hit_cnt.items():
                    context.accumulate_hit[k] += v
                if mode == "EXPERIMENT":
                    with open(path, "w", newline="") as hit_f:
                        hit_f.writelines([str(context.accumulate_hit), "\n"])
                execinfo.append(tx_dict)
                con_oracle.valid_cnt += 1

        for tx_dict, exec_item in exec_list:
            if tx_dict != "error":
                hit_cnt = pathway.calculate_target(pc_dict, exec_item)
                batch_hitans.append([tx_dict, hit_cnt])

        if mode == "EXPERIMENT":
            can_file_path = os.path.join(os.path.join(EVALUATION_RES_PATH, "candidate"), contract_name + ".txt")
            with open(can_file_path, "a+", newline="") as can_f:
                can_f.writelines(["candidate:", str(len(execinfo)), "\n"])
                rare_tag_list = cal_rare(context, can_f)
        for i in range(len(batch_hitans)):
            item_list = batch_hitans[i]
            tx_dict, hit_cnt = item_list[0], item_list[1]
            for k, v in hit_cnt.items():
                if v != 0 and k in rare_tag_list:
                    execinfo.append(tx_dict)
                    break
    except:
        logging.info("analyzer: not batch_hitans")
    # print(batch_hitans)
    # print(context.accumulate_hit)
    return execinfo
