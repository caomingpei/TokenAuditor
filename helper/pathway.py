import logging


def bytecode_disasm(bytecode: str) -> list:
    OPCODES = ['STOP', 'ADD', 'MUL', 'SUB', 'DIV', 'SDIV', 'MOD', 'SMOD', 'ADDMOD', 'MULMOD', 'EXP', 'SIGNEXTEND', '',
               '', '', '', 'LT', 'GT', 'SLT', 'SGT', 'EQ', 'ISZERO', 'AND', 'OR', 'XOR', 'NOT', 'BYTE', 'SHL', 'SHR',
               'SAR', '', '', 'SHA3', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 'ADDRESS', 'BALANCE',
               'ORIGIN', 'CALLER', 'CALLVALUE', 'CALLDATALOAD', 'CALLDATASIZE', 'CALLDATACOPY', 'CODESIZE', 'CODECOPY',
               'GASPRICE', 'EXTCODESIZE', 'EXTCODECOPY', 'RETURNDATASIZE', 'RETURNDATACOPY', 'EXTCODEHASH', 'BLOCKHASH',
               'COINBASE', 'TIMESTAMP', 'NUMBER', 'DIFFICULTY', 'GASLIMIT', 'CHAINID', 'SELFBALANCE', 'BASEFEE', '', '',
               '', '', '', '', '', 'POP', 'MLOAD', 'MSTORE', 'MSTORE8', 'SLOAD', 'SSTORE', 'JUMP', 'JUMPI', 'PC',
               'MSIZE', 'GAS', 'JUMPDEST', '', '', '', '', 'PUSH1', 'PUSH2', 'PUSH3', 'PUSH4', 'PUSH5', 'PUSH6',
               'PUSH7', 'PUSH8', 'PUSH9', 'PUSH10', 'PUSH11', 'PUSH12', 'PUSH13', 'PUSH14', 'PUSH15', 'PUSH16',
               'PUSH17', 'PUSH18', 'PUSH19', 'PUSH20', 'PUSH21', 'PUSH22', 'PUSH23', 'PUSH24', 'PUSH25', 'PUSH26',
               'PUSH27', 'PUSH28', 'PUSH29', 'PUSH30', 'PUSH31', 'PUSH32', 'DUP1', 'DUP2', 'DUP3', 'DUP4', 'DUP5',
               'DUP6', 'DUP7', 'DUP8', 'DUP9', 'DUP10', 'DUP11', 'DUP12', 'DUP13', 'DUP14', 'DUP15', 'DUP16',
               'SWAP1', 'SWAP2', 'SWAP3', 'SWAP4', 'SWAP5', 'SWAP6', 'SWAP7', 'SWAP8', 'SWAP9', 'SWAP10', 'SWAP11',
               'SWAP12', 'SWAP13', 'SWAP14', 'SWAP15', 'SWAP16', 'LOG0', 'LOG1', 'LOG2', 'LOG3', 'LOG4', '', '', '',
               '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
               '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
               '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 'CREATE', 'CALL',
               'CALLCODE', 'RETURN', 'DELEGATECALL', 'CREATE2', '', '', '', '', 'STATICCALL', '', '', 'REVERT',
               'INVALID', 'SUICIDE']
    ans_opcode = []
    if len(bytecode) %2 !=0:
        logging.warning("pathway:bytecode_disasm input bytecode should be 2 characters per byte.")
    idx = 0
    while idx < len(bytecode):
        cur_byte = bytecode[idx:idx+2]
        num = int(str(cur_byte), 16)
        if num < 0 or num >= 256:
            logging.warning("pathway:bytecode_disasm bytes are not between 0 and 255")
        if 0x60 <= num and num < 0x80:
            push_len = num-0x5f
            idx += 2
            push_value = bytecode[idx:idx+2*push_len]
            idx += 2*push_len
            ans_opcode.append(OPCODES[num])
            ans_opcode.append(push_value)
        else:
            chr = OPCODES[num]
            if chr:
                ans_opcode.append(chr)
            else:
                ans_opcode.append(cur_byte)
            idx += 2
    return ans_opcode


def build_jump_block(run_bytecode: str) -> dict:
    opcode_list = bytecode_disasm(run_bytecode)
    pc_jumpblock = dict()
    pc_jumpblock[0] = "tag0"
    pc, idx= 0, 0
    tag_num = 1

    while idx < len(opcode_list):
        op = opcode_list[idx]
        if op == "JUMPDEST":
            pc_jumpblock[pc] = "tag"+str(tag_num)
            tag_num += 1
        elif op.startswith("PUSH"):
            push_len = int(op.split("PUSH")[1])
            idx += 1
            pc += push_len
        pc += 1
        idx += 1

    return pc_jumpblock


def calculate_target(pc_dict: dict, result_json: dict) -> dict:
    ans_hit_count = dict()
    for _, v in pc_dict.items():
        ans_hit_count[v] = 0
    if not ("error" in result_json.keys()):
        logs = result_json["structLogs"]
        for log_dict in logs:
            if log_dict["op"] == "JUMPDEST" or log_dict["pc"] == 0:
                ans_hit_count[pc_dict[log_dict["pc"]]] += 1

        return ans_hit_count

