import string
from env import *


SUPPORT_TYPE = ["bool", "uint", "int", "byte", "string", "address", "uint8", "uint16", "uint24", "uint32", "uint40",
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


def _gen_bool() -> bool:
    num = random.randint(0, 1)
    if num:
        return True
    return False


def _gen_int(bit_len: int) -> int:
    ans = random.randint(-2**(bit_len-1), 2**(bit_len-1)-1)
    return ans


def _gen_uint(bit_len: int) -> int:
    ans = random.randint(0, 2**bit_len-1)
    return ans


def _gen_address(role) -> str:
    if role == "OWNER":
        return OWNER_ADDRESS
    elif role == "ATTACKER":
        return ATTACKER_ADDRESS
    elif role == "USER":
        return USER_ADDRESS
    else:
        addr = "".join([random.choice("0123456789abcdef") for _ in range(20 * 2)])
        return web3.Web3.toChecksumAddress("0x" + addr)


# bit_len equals 8 multiple byte_len
def _gen_bytes(byte_len: int) -> bytes:
    ans_byte = bytes([random.randint(0, 255) for _ in range(byte_len)])
    return ans_byte


def _gen_string(default_max=10) -> str:
    max_len = random.randint(1, default_max)
    randstr = "".join(random.choice(string.ascii_letters + string.digits) for _ in range(max_len))
    return randstr


def _gen_fixed_array(category: str, num: int, role: str, length: int) -> any:
    gen_list = []
    for i in range(length):
        gen_list.append(generate_single(category, num, role))
    return gen_list


def _gen_variable_array(category: str, num: int, role: str, default_len=5) -> any:
    gen_list = []
    length = random.randint(1, default_len)
    for i in range(length):
        gen_list.append(generate_single(category, num, role))
    return gen_list


def generate_single(category: str, num: int, role: str) -> any:
    if category == "bool":
        return _gen_bool()
    elif category == "int":
        if num == 0:
            return _gen_int(256)
        else:
            return _gen_int(num)
    elif category == "uint":
        if num == 0:
            return _gen_uint(256)
        else:
            return _gen_uint(num)
    elif category == "address":
        return _gen_address(role)
    elif category == "bytes":
        byte_len = num
        if byte_len > 32:
            logging.warning("generator: generate_singe byte_len mismatch")
        return _gen_bytes(byte_len)
    elif category == "byte":
        return _gen_bytes(1)
    elif category == "string":
        if num == 0:
            return _gen_string()
        else:
            return _gen_string(num)
    else:
        logging.warning("generator: generate_singe NOT DETECT " + category + " type!")


def generate_array(category: str, num: int, role: str, dimension: list) -> list:
    gen_list = []
    if len(dimension) == 1:
        if dimension[0] == -1:
            return _gen_variable_array(category, num, role)
        else:
            return _gen_fixed_array(category, num, role, dimension[0])
    else:
        for dim_int in dimension:
            if dim_int == -1:
                gen_list.append(_gen_variable_array(category, num, role))
            else:
                gen_list.append(_gen_fixed_array(category, num, role, dim_int))
        return gen_list


def generate_template(template_list, role) -> list:
    generate_ans = []
    if template_list:
        for type_item in template_list:
            if isinstance(type_item, list):
                generate_ans.append(generate_template(type_item, role))
            else:
                prefix_type = re.findall(r'[a-z]+', type_item)[0]
                if prefix_type in SUPPORT_TYPE:
                    type_list = type_item.split("[")
                    num_list = re.findall(r'[0-9]+', type_list[0])
                    num = num_list[0] if len(num_list) else 0
                    if len(type_list) > 1:
                        dimension_list = []
                        array_list = re.findall(r"\[[0-9]*\]", type_item)
                        for ditem in array_list:
                            dnum_list = re.findall(r'[0-9]+', ditem)
                            if dnum_list:
                                dimension_list.append(int(dnum_list[0]))
                            else:
                                dimension_list.append(-1)
                        generate_ans.append(generate_array(prefix_type, int(num), role, dimension_list))
                    else:
                        generate_ans.append(generate_single(prefix_type, int(num), role))
                else:
                    logging.warning("generator:generate_template NOT SUPPORT "+ prefix_type + " type")
    return generate_ans


def generate_seeds_single(category: str, role: str):
    seed_dict = {"uint": [0, 1, 2, 3],
                 "int": [1, 2, 3, -1],
                 "bytes": [b'\x01', b'\x02', b'\x03', b'\x32'],
                 "string": ["hello", "Token", "ethereum"],
                 "bool": [True, False],
                 "address": [OWNER_ADDRESS, USER_ADDRESS]
                 }
    if category == "bool":
        return random.choice(seed_dict["bool"])
    elif category == "int":
        return random.choice(seed_dict["int"])
    elif category == "uint":
        return random.choice(seed_dict["uint"])
    elif category == "address":
        return _gen_address(role)
    elif category == "bytes" or category == "byte":
        return random.choice(seed_dict["bytes"])
    elif category == "string":
        return random.choice(seed_dict["string"])
    else:
        logging.warning("generator: generate_singe NOT DETECT " + category + " type!")


def generate_seeds_array(category: str, role: str, dimension: list) -> list:
    gen_list = []
    if len(dimension) == 1:
        if dimension[0] == -1:
            for i in range(2):
                gen_list.append(generate_seeds_single(category, role))
        else:
            for i in range(dimension[0]):
                gen_list.append(generate_seeds_single(category, role))
        return gen_list
    else:
        for dim_int in dimension:
            cur_list = []
            if dim_int == -1:
                for i in range(2):
                    cur_list.append(generate_seeds_single(category, role))
                gen_list.append(cur_list)
            else:
                for i in range(dim_int):
                    cur_list.append(generate_seeds_single(category, role))
                gen_list.append(cur_list)
        return gen_list


def generate_seeds(template_list, role) -> list:
    generate_ans = []
    if template_list:
        for type_item in template_list:
            if isinstance(type_item, list):
                generate_ans.append(generate_template(type_item, role))
            else:
                prefix_type = re.findall(r'[a-z]+', type_item)[0]
                if prefix_type in SUPPORT_TYPE:
                    type_list = type_item.split("[")
                    if len(type_list) > 1:
                        dimension_list = []
                        array_list = re.findall(r"\[[0-9]*\]", type_item)
                        for ditem in array_list:
                            dnum_list = re.findall(r'[0-9]+', ditem)
                            if dnum_list:
                                dimension_list.append(int(dnum_list[0]))
                            else:
                                dimension_list.append(-1)
                        generate_ans.append(generate_seeds_array(prefix_type, role, dimension_list))
                    else:
                        generate_ans.append(generate_seeds_single(prefix_type, role))
                else:
                    logging.warning("generator:generate_template NOT SUPPORT " + prefix_type + " type")
    return generate_ans


def generate_limit_single(category: str, role: str, uint_max=255, int_max=127, byte_len_max=8, string_len_max=10):
    if category == "bool":
        return _gen_bool()
    elif category == "int":
        return random.randint(-abs(int_max), abs(int_max))
    elif category == "uint":
        return random.randint(0, uint_max)
    elif category == "address":
        return _gen_address(role)
    elif category == "bytes" or category == "byte":
        return _gen_bytes(byte_len_max)
    elif category == "string":
        return _gen_string(string_len_max)
    else:
        logging.warning("generator: generate_singe NOT DETECT " + category + " type!")


def generate_limit_array(category: str, role: str, dimension: list, uint_max, int_max, byte_len_max, string_len_max) -> list:
    gen_list = []
    if len(dimension) == 1:
        if dimension[0] == -1:
            for i in range(2):
                gen_list.append(generate_limit_single(category, role, uint_max, int_max, byte_len_max, string_len_max))
        else:
            for i in range(dimension[0]):
                gen_list.append(generate_limit_single(category, role, uint_max, int_max, byte_len_max, string_len_max))
        return gen_list
    else:
        for dim_int in dimension:
            cur_list = []
            if dim_int == -1:
                for i in range(2):
                    cur_list.append(generate_limit_single(category, role, uint_max, int_max, byte_len_max,
                                                          string_len_max))
                gen_list.append(cur_list)
            else:
                for i in range(dim_int):
                    cur_list.append(generate_limit_single(category, role, uint_max, int_max, byte_len_max,
                                                          string_len_max))
                gen_list.append(cur_list)
        return gen_list


def generate_limit(template_list, role, uint_max=255, int_max=127, byte_len_max=8, string_len_max=10):
    generate_ans = []
    if template_list:
        for type_item in template_list:
            if isinstance(type_item, list):
                generate_ans.append(generate_template(type_item, role))
            else:
                prefix_type = re.findall(r'[a-z]+', type_item)[0]
                if prefix_type in SUPPORT_TYPE:
                    type_list = type_item.split("[")
                    if len(type_list) > 1:
                        dimension_list = []
                        array_list = re.findall(r"\[[0-9]*\]", type_item)
                        for ditem in array_list:
                            dnum_list = re.findall(r'[0-9]+', ditem)
                            if dnum_list:
                                dimension_list.append(int(dnum_list[0]))
                            else:
                                dimension_list.append(-1)
                        generate_ans.append(generate_limit_array(prefix_type, role, dimension_list, uint_max, int_max,
                                                                 byte_len_max, string_len_max))
                    else:
                        generate_ans.append(generate_limit_single(prefix_type, role, uint_max, int_max, byte_len_max,
                                                                  string_len_max))
                else:
                    logging.warning("generator:generate_template NOT SUPPORT " + prefix_type + " type")
    return generate_ans


def generate_tx_dict(func_item, generate_mode, func_mode, address_role, call_role) -> dict:
    value = 0
    if func_mode == "payable":
        value = random.randint(10000000000000000000, 100000000000000000000)
    if generate_mode == "seeds":
        f_para = generate_seeds(func_item.inputs, address_role)
        tx_dict = {"method": func_item.method, "inputs": func_item.inputs, "outputs": func_item.outputs,
                   "f_para": f_para, "address_role": address_role, "call_role": call_role, "value": value}
        return tx_dict
    elif generate_mode == "normal":
        f_para = generate_template(func_item.inputs, address_role)
        tx_dict = {"method": func_item.method, "inputs": func_item.inputs, "outputs": func_item.outputs,
                   "f_para": f_para, "address_role": address_role, "call_role": call_role, "value": value}
        return tx_dict
    else:
        logging.warning("generator:generate_tx_dict Not illegal generate_mode input")


def generate_limit_tx_dict(func_item, func_mode, address_role, call_role, uint_max=255, int_max=127, byte_len_max=8,
                           string_len_max=10) -> dict:
    value = 0
    if func_mode == "payable":
        value = random.randint(10000000000000000000, 100000000000000000000)
    f_para = generate_limit(func_item.inputs, address_role, uint_max, int_max, byte_len_max, string_len_max)
    tx_dict = {"method": func_item.method, "inputs": func_item.inputs, "outputs": func_item.outputs,
               "f_para": f_para, "address_role": address_role, "call_role": call_role, "value": value}
    return tx_dict


def generate_token_standard(standard: str, func_item, owner_num) -> dict:
    value = 0
    if func_item.modifier == "payable":
        value = random.randint(10000000000000000000, 100000000000000000000)
    method = func_item.method
    if standard == "ERC20":
        f_para = []
        if method == "name" or method == "symbol" or method == "decimals" or method == "totalSupply":
            pass
        elif method == "balanceOf":
            f_para = [OWNER_ADDRESS]
        elif method == "transfer":
            f_para = [OWNER_ADDRESS, random.randint(1, owner_num-1)]
        elif method == "transferFrom":
            f_para = [OWNER_ADDRESS, USER_ADDRESS, random.randint(1, owner_num-1)]
        elif method == "approve":
            f_para = [USER_ADDRESS, random.randint(1, owner_num-1)]
        elif method == "allowance":
            f_para = [OWNER_ADDRESS, USER_ADDRESS]
        tx_dict = {"method": method, "inputs": func_item.inputs, "outputs": func_item.outputs,
                   "f_para": f_para, "call_role": "OWNER", "value": value, "modifier": func_item.modifier}
        return tx_dict
    elif standard == "ERC721":
        f_para = []
        if method == "balanceOf":
            f_para = [OWNER_ADDRESS]
        elif method == "ownerOf":
            f_para = [owner_num[0]]
        elif method == "safeTransferFrom":
            f_para = [OWNER_ADDRESS, USER_ADDRESS, owner_num[0]]
        elif method == "transferFrom":
            f_para = [OWNER_ADDRESS, USER_ADDRESS, owner_num[0]]
        elif method == "approve":
            f_para = [USER_ADDRESS, owner_num[0]]
        elif method == "setApprovalForAll":
            f_para = [USER_ADDRESS, True]
        elif method == "getApproved":
            f_para = [owner_num[0]]
        elif method == "isApproveForAll":
            f_para = [OWNER_ADDRESS, USER_ADDRESS]
        tx_dict = {"method": method, "inputs": func_item.inputs, "outputs": func_item.outputs,
                   "f_para": f_para, "call_role": "OWNER", "value": value, "modifier": func_item.modifier}
        return tx_dict
    else:
        logging.warning("generator:generate_token_standard don't support token standard")
