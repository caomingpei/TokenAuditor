import web3.eth
from collections import defaultdict
from oracle import Factory
from fuzzer import preprocess
from helper import pathway
from oracle.Factory import OracleFactory
from env import *


class FunctionContext:
    def __init__(self):
        self.function_view = defaultdict(list)
        self.function_nonpayable = defaultdict(list)
        self.function_payable = defaultdict(list)

    def get_function_view(self):
        return self.function_view

    def set_function_view(self, function_view):
        self.function_view = function_view

    def get_function_nonpayable(self):
        return self.function_nonpayable

    def set_function_nonpayable(self, function_nonpayable):
        self.function_nonpayable = function_nonpayable

    def get_function_payable(self):
        return self.function_payable

    def set_function_payable(self, function_payable):
        self.function_payable = function_payable


class Context:
    def __init__(self, name, w3):
        self.name = name
        self.web3 = w3
        self.contract = web3.eth.Contract
        self.constructor_para = str
        self.oracle = Factory.OracleFactory
        self.mutation_batch = int
        self.mutation_epochs = int(0)
        self.function_context = FunctionContext()
        self.option = {'from': OWNER_ADDRESS, 'gas': 15000000}
        self.buildblock = dict()
        self.accumulate_hit = dict()
        self.halt = False

    def set_contract(self, contract):
        self.contract = contract

    def get_contract(self):
        return self.contract

    def set_buildblock(self, buildblock):
        self.buildblock = buildblock

    def get_buildblock(self):
        return self.buildblock

    def set_accumulate_hit(self, accumulate_hit):
        self.accumulate_hit = accumulate_hit

    def get_accumulate_hit(self):
        return self.accumulate_hit

    def set_constructor_para(self, constructor_para):
        self.constructor_para = constructor_para

    def get_constructor_para(self):
        return self.constructor_para

    def set_oracle(self, con_oracle):
        self.oracle = con_oracle

    def get_oracle(self) -> Type[OracleFactory]:
        return self.oracle

    def set_mutation_batch(self, mutation_batch):
        self.mutation_batch = mutation_batch

    def get_mutation_batch(self):
        return self.mutation_batch

    def set_mutation_epochs(self, mutation_epochs):
        self.mutation_epochs = mutation_epochs

    def get_mutation_epochs(self):
        return self.mutation_epochs

    def set_function_context(self, function_view, function_nonpayable, function_payable):
        self.function_context.set_function_view(function_view)
        self.function_context.set_function_nonpayable(function_nonpayable)
        self.function_context.set_function_payable(function_payable)

    def get_function_context(self) -> FunctionContext:
        return self.function_context

    def set_option(self, option: dict):
        self.option = option

    def get_option(self):
        return self.option

    def set_halt(self, halt: bool):
        self.halt = halt


def configure(w3, contract_name, mutation_batch):
    fuzz_context = Context(contract_name, w3)
    fuzz_context.set_mutation_epochs(0)
    fuzz_context.set_mutation_batch(mutation_batch)

    constructor_str = preprocess.get_constructor_replace_address(contract_name)
    fuzz_context.set_constructor_para(constructor_str)

    option = {'from': OWNER_ADDRESS, 'gas': 15000000}
    contractInstance = preprocess.deployed_contract(w3, contract_name, fuzz_context.get_constructor_para(), option)
    build_block = pathway.build_jump_block(contractInstance.bytecode_runtime)
    fuzz_context.set_buildblock(build_block)
    accumulate_hit = dict(zip(build_block.values(), [0 for _ in range(len(build_block))]))
    fuzz_context.set_accumulate_hit(accumulate_hit)
    fuzz_context.set_contract(contractInstance)

    return fuzz_context
