import random
from fuzzer import generator
from env import *
from bitstring import BitArray
from collections import defaultdict

MUTATOR_TYPE = ["bool", "uint", "int", "byte", "string", "address", "uint8", "uint16", "uint24", "uint32", "uint40",
                "uint48", "uint56", "uint64", "uint72", "uint80", "uint88", "uint96", "uint104", "uint112", "uint120",
                "uint128", "uint136", "uint144", "uint152", "uint160", "uint168", "uint176", "uint184", "uint192",
                "uint200", "uint208", "uint216", "uint224", "uint232", "uint240", "uint248", "uint256", "int8", "int16",
                "int24", "int32", "int40", "int48", "int56", "int64", "int72", "int80", "int88", "int96", "int104",
                "int112", "int120", "int128", "int136", "int144", "int152", "int160", "int168", "int176", "int184",
                "int192", "int200", "int208", "int216", "int224", "int232", "int240", "int248", "int256", "bytes1",
                "bytes2", "bytes3", "bytes4", "bytes5", "bytes6", "bytes7", "bytes8", "bytes9", "bytes10", "bytes11",
                "bytes12", "bytes13", "bytes14", "bytes15", "bytes16", "bytes17", "bytes18", "bytes19", "bytes20",
                "bytes21", "bytes22", "bytes23", "bytes24", "bytes25", "bytes26", "bytes27", "bytes28", "bytes29",
                "bytes30", "bytes31", "bytes32", "bytes"]


def candidate_gen(context, maxnum: int) -> list:
    oracle = context.get_oracle()
    function_context = context.get_function_context()
    function_nonpayable = function_context.get_function_nonpayable()
    function_payable = function_context.get_function_payable()
    candidate_list = list()

    for k, func_list in function_nonpayable.items():
        for func_item in func_list:
            call_address = "OWNER" if random.random() > 0.5 else "USER"
            tx_dict = generator.generate_tx_dict(func_item, "seeds", "nonpayable", call_address, "OWNER")
            oracle.add_transaction_list(tx_dict)
            candidate_list.append([func_item, "nonpayable"])

    for k, func_list in function_payable.items():
        for func_item in func_list:
            call_address = "OWNER" if random.random() > 0.5 else "USER"
            tx_dict = generator.generate_tx_dict(func_item, "seeds", "payable", call_address, "OWNER")
            oracle.add_transaction_list(tx_dict)
            candidate_list.append([func_item, "payable"])

    select_list = [random.choice(candidate_list) for _ in range(maxnum)]
    chose_list = []
    for func_item, func_mode in select_list:
        call_address = "OWNER" if random.random() > 0.5 else "USER"
        tx_dict = generator.generate_tx_dict(func_item, "seeds", func_mode, call_address, "OWNER")
        chose_list.append(tx_dict)
    return chose_list


def init_trans(context):
    oracle = context.get_oracle()
    function_context = context.get_function_context()
    function_nonpayable = function_context.get_function_nonpayable()
    function_payable = function_context.get_function_payable()
    candidate_list = list()
    if oracle.get_mode() == "normal":
        for k, func_list in function_nonpayable.items():
            for func_item in func_list:
                tx_dict = generator.generate_tx_dict(func_item, "seeds", "nonpayable", "OWNER", "OWNER")
                oracle.add_transaction_list(tx_dict)
                candidate_list.append([func_item, "nonpayable"])

        for k, func_list in function_payable.items():
            for func_item in func_list:
                tx_dict = generator.generate_tx_dict(func_item, "seeds", "payable", "OWNER", "OWNER")
                oracle.add_transaction_list(tx_dict)
                candidate_list.append([func_item, "payable"])

        if len(candidate_list) > context.get_mutation_batch():
            context.set_mutation_batch(2 * len(candidate_list))
            logging.warning("mutator:init_trans Not proper mutation batch setting, change to " +
                            str(2 * len(candidate_list)))

        batch_max = context.get_mutation_batch()
        tx_num = len(oracle.get_transaction_list())
        select_list = [random.choice(candidate_list) for _ in range(batch_max-tx_num)]
        for func_item, func_mode in select_list:
            tx_dict = generator.generate_tx_dict(func_item, "seeds", func_mode, "OWNER", "OWNER")
            oracle.add_transaction_list(tx_dict)
    elif oracle.get_mode() == "compatibility":
        for func_item in oracle.func_item_list:
            tx_dict = generator.generate_token_standard(oracle.proposal, func_item, oracle.owner_num)
            oracle.add_transaction_list(tx_dict)


def bin_bit_flip(ori_bin):
    bit_len = len(ori_bin)
    start_pos = random.randint(0, bit_len)
    end_pos = min(start_pos + random.choice([1, 2, 4]), bit_len)
    fir_str, mid_str, end_str = ori_bin[:start_pos], "", ori_bin[end_pos:]
    for i in range(start_pos, end_pos):
        mid_str += "0" if ori_bin[i] == 1 else "1"
    return fir_str + mid_str + end_str


def get_random_unicode(length):
    # Update this to include code point ranges to be sampled
    include_ranges = [
        (0x0021, 0x0021),
        (0x0023, 0x0026),
        (0x0028, 0x007E),
        (0x00A1, 0x00AC),
        (0x00AE, 0x00FF),
        (0x0100, 0x017F),
        (0x0180, 0x024F),
        (0x2C60, 0x2C7F),
        (0x16A0, 0x16F0),
        (0x0370, 0x0377),
        (0x037A, 0x037E),
        (0x0384, 0x038A),
        (0x038C, 0x038C),
    ]
    alphabet = [
        chr(code_point) for current_range in include_ranges
            for code_point in range(current_range[0], current_range[1] + 1)
    ]
    return ''.join(random.choice(alphabet) for i in range(length))


def bit_flip(item_type: str, value):
    if item_type.startswith("int") or item_type.startswith("uint"):
        true_type = item_type if item_type.split("int")[-1] else item_type+str(256)
        bit_array = BitArray(str(true_type)+"="+str(value))
        bit_array.bin = bin_bit_flip(bit_array.bin)
        if item_type.startswith("int"):
            return bit_array.int
        else:
            return bit_array.uint

    elif item_type.startswith("byte"):
        if item_type != "bytes":
            bit_array = BitArray(bytes=value)
            bit_array.bin = bin_bit_flip(bit_array.bin)
            return bit_array.bytes
        else:
            return value

    elif item_type.startswith("string"):
        random_chr = get_random_unicode(1)
        if len(value) <= 1:
            return random_chr
        if random.randint(0, 1) == 1:
            return value+random_chr
        else:
            position = random.randint(1, len(value) - 1)
            return value[:position-1] + random_chr + value[position:]


def arithmetic_convert(item_type: str, value):
    num = item_type.split("int")[-1]
    if item_type.startswith("uint"):
        bit_len = int(num) if num else 256
        true_type = "uint"+str(bit_len)
        bit_array = BitArray(str(true_type) + "=" + str(value))
        max_num = int(2 ** bit_len - 1)
        if random.randint(0, 1):
            mutate_para = (bit_array.uint + random.randint(0, 35)) % max_num
        else:
            mutate_para = (bit_array.uint + 2 ** random.randint(0, 16)) % max_num
        return mutate_para
    elif item_type.startswith("int"):
        bit_len = int(num) if num else 256
        true_type = "int" + str(bit_len)
        bit_array = BitArray(str(true_type) + "=" + str(value))
        max_num = int(2 ** (bit_len - 1) - 1)
        if random.randint(0, 1):
            cur = (bit_array.int + random.randint(-35, 35)) % max_num
            mutate_para = -cur if random.randint(0, 1) else cur
        else:
            cur = abs((bit_array.int + 2 ** random.randint(0, 16)) % max_num)
            mutate_para = -cur if random.randint(0, 1) else cur
        return mutate_para


def boundary_seed(item_type: str):
    seed_dict = {
        "uint": [0, 1, 2, 3, 100, 127, 128, 255, 256, 511, 512, 1023, 1024, 65535, 65536],
        "bytes": [b'\x01', b'\x02', b'\x03', b'\x32', b'\x99', b'\xaa', b'\xff', b'\xfe'],
        "string": [" ", ""],
    }
    if item_type.startswith("uint"):
        num = item_type.split("uint")[-1]
        bit_len = int(num) if num else 256
        max_num = int(2 ** bit_len - 1)
        return random.choice(seed_dict["uint"]) % max_num
    elif item_type.startswith("int"):
        num = item_type.split("int")[-1]
        bit_len = int(num) if num else 256
        max_num = int(2 ** (bit_len - 1) - 1)
        cur = random.choice(seed_dict["uint"]) % max_num
        return -cur if random.randint(0, 1) else cur
    elif item_type.startswith("bytes") and item_type != "bytes":
        num = item_type.split("bytes")[-1]
        byte_len = int(num)
        max_len = random.randint(1, byte_len)
        return b''.join(random.choice(seed_dict["bytes"]) for _ in range(max_len))
    elif item_type.startswith("string"):
        return random.choice(seed_dict["string"])


def splicing(item_type: str, val1, val2):
    if item_type.startswith("int") or item_type.startswith("uint"):
        true_type = item_type if item_type.split("int")[-1] else item_type+str(256)
        barray1, barray2 = BitArray(str(true_type)+"="+str(val1)), BitArray(str(true_type)+"="+str(val2))
        split_pos = random.randint(1, int(item_type.split("int")[-1])-1)
        barray1.bin = barray1.bin[:split_pos] + barray2.bin[split_pos:]
        if item_type.startswith("int"):
            return barray1.int
        else:
            return barray1.uint

    elif item_type.startswith("byte") and item_type != "bytes":
        barray1, barray2 = BitArray(bytes=val1), BitArray(bytes=val2)
        split_pos = random.randrange(0, min(len(barray1.bin), len(barray2.bin)), 8)
        barray1.bin = barray1.bin[:split_pos] + barray2.bin[split_pos:]
        return barray1.bytes
    elif item_type.startswith("string"):
        max_len = min(len(val1), len(val2))
        if max_len <= 1:
            return val1 if len(val1) > len(val2) else val2
        split_pos = random.randint(1, max_len - 1)
        return val1[:split_pos] + val2[split_pos:]


def mutation_strategy(tx_dict, method_inputs_to_para, now_epochs, max_mutation_epochs) -> list:
    method, inputs, f_para = tx_dict["method"], tx_dict["inputs"], tx_dict["f_para"]
    ans_f_para = []
    key_check_name = str(method)+str(inputs)

    for i in range(len(inputs)):
        input_item, para_item,  = inputs[i], f_para[i]  # item_type, value
        candidate_mutate_para = []
        if input_item in MUTATOR_TYPE:
            mutate_para = ""
            if input_item == "address":
                mutate_para = OWNER_ADDRESS if random.randint(0, 1) else USER_ADDRESS
            elif input_item == "bool":
                mutate_para = True if random.randint(0, 1) else False
            elif input_item.startswith("uint") or input_item.startswith("int"):
                candidate_mutate_para.extend([bit_flip(input_item, para_item), arithmetic_convert(input_item, para_item)
                                              , boundary_seed(input_item)])

            elif input_item.startswith("bytes") or input_item.startswith("string"):
                candidate_mutate_para.extend([bit_flip(input_item, para_item), boundary_seed(input_item)])

            if key_check_name in method_inputs_to_para and now_epochs >= 3 and now_epochs >= max_mutation_epochs//2:
                splicing_val2 = method_inputs_to_para[key_check_name]
                candidate_mutate_para.append(splicing(input_item, para_item, splicing_val2[i]))
            if candidate_mutate_para:
                mutate_para = random.choice(candidate_mutate_para)

            ans_f_para.append(mutate_para)

        else:
            ans_f_para.append(para_item)

    if len(inputs) == len(ans_f_para):
        return ans_f_para
    else:
        return f_para


def update(context, execinfo, threshold, mode, contract_name, max_mutation_epochs):
    oracle = context.get_oracle()
    now_epochs = context.get_mutation_epochs()
    all_tx_list = oracle.get_all_tx_dict()
    method_inputs_to_para = defaultdict(list)
    for tx_dict in all_tx_list:
        method_inputs_to_para[str(tx_dict["method"])+str(tx_dict["inputs"])] = tx_dict["f_para"] # the last is val2

    if mode == "EXPERIMENT":
        can_file_path = os.path.join(os.path.join(EVALUATION_RES_PATH, "candidate"), contract_name+".txt")
        with open(can_file_path, "a+", newline="") as can_f:
            can_f.writelines(["candidate:", str(len(execinfo)), "\n"])
    if oracle.get_mode() == "normal":
        new_tx_list = []
        batch_max = context.get_mutation_batch()
        preinfo = execinfo[:]
        for tx_dict in execinfo:
            # print(tx_dict["method"])
            tx_dict["f_para"] = mutation_strategy(tx_dict, method_inputs_to_para, now_epochs, max_mutation_epochs)
            tx_dict["call_role"] = "OWNER" if random.randint(0, 1) else "USER"
            if tx_dict["value"] != 0:
                tx_dict["value"] = random.randint(1, 100)
        execinfo.extend(preinfo)
        if len(execinfo) <= threshold:
            new_tx_list.extend(execinfo)
        else:
            select_list = [random.choice(execinfo) for _ in range(threshold)]
            new_tx_list.extend(select_list)
        seeds_list = candidate_gen(context, batch_max - min(len(execinfo), threshold))
        new_tx_list.extend(seeds_list)
        oracle.set_transaction_list(new_tx_list)

    elif oracle.get_mode() == "compatibility":
        oracle.set_transaction_list([])
