import os
import sys
import re
import json
import random
import subprocess
import signal
import platform
import time
import logging
import psutil
import requests
import web3
from web3 import Web3
from eth_abi import decode_abi, encode_abi
from typing import *


ATTACKER_PRIVATE_KEY = "0x742d349d768c5a73c9368c9b2d04e88f0d511696d98f1d3cb1c7cecd80d391f5"
ATTACKER_ADDRESS = "0x99999b4922958aA33971682A2A6F36f16eF30579"
OWNER_PRIVATE_KEY = "0x18ffb39958a9c3d9d885518a78393162ae9508688ca382015d07ed10ad8c2315"
OWNER_ADDRESS = "0x000000ACABf52abb95cA39fCCb42416cAb20cDDB"
USER_PRIVATE_KEY = "0x149a5a963103ac553c26368edafc55e6a3bc7634ef1ddd2bd869fc7f5c98133b"
USER_ADDRESS = "0xaAAA22497257c94996181c3ca2DAcE834Ee61d09"

CUR_PATH, _ = os.path.split(os.path.realpath(__file__))
EVALUATION_ROOT_PATH = os.path.join(CUR_PATH, "evaluation")
EVALUATION_RES_PATH = os.path.join(EVALUATION_ROOT_PATH, "exp_result")
EVALUATION_DATASET_PATH = os.path.join(EVALUATION_ROOT_PATH, "dataset")
ERC20_PATH = os.path.join(EVALUATION_DATASET_PATH, "ERC20")
ERC20_ABI_PATH = os.path.join(ERC20_PATH, "abi")
ERC20_CONSTRUCTOR_PATH = os.path.join(ERC20_PATH, "constructor")
ERC20_CREATIONCODE_PATH = os.path.join(ERC20_PATH, "creationcode")

ERC721_PATH = os.path.join(EVALUATION_DATASET_PATH, "ERC721")
ERC721_ABI_PATH = os.path.join(ERC721_PATH, "abi")
ERC721_CONSTRUCTOR_PATH = os.path.join(ERC721_PATH, "constructor")
ERC721_CREATIONCODE_PATH = os.path.join(ERC721_PATH, "creationcode")

