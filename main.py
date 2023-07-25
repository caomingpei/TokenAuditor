from env import *
from fuzzer import executor
import argparse
from config import RES_PATH

EXEC_TIME_LIMIT = 3600
GENERATE_TX_PER_EPOCH = 10
TEST_EPOCHS = 50


if __name__ == "__main__":
    arg_description = "This script is an implement of TokenAuditor for fuzzing smart contract to detect\\ " \
                      "manipulation risk. Our work has been accepted by [QRS'22]."
    parser = argparse.ArgumentParser(description=arg_description)
    group = parser.add_mutually_exclusive_group()

    parser.add_argument('--exec_limit', '-l', type=int, default=EXEC_TIME_LIMIT, help='set the executing limit')
    parser.add_argument('--batch_size', '-b', type=int, default=GENERATE_TX_PER_EPOCH,
                        help='set the number of generating test samples per epoch')
    parser.add_argument('--epochs', '-e', type=int, default=TEST_EPOCHS, help='set the executing epoch')
    parser.add_argument('--contracts', '-c', type=str, default='', help='set the contracts under the fuzzing test')
    parser.add_argument('--mode', '-m', type=str, default="FORMAL", choices=["FORMAL", "TEST"],
                        help="set the mode, FORMAL is for normal usage and TEST is for evaluation results")

    args = parser.parse_args()

    EXEC_TIME_LIMIT = args.exec_limit
    GENERATE_TX_PER_EPOCH = args.batch_size
    TEST_EPOCHS = args.epochs
    if args.contracts:
        PENDING_CONTRACTS = args.contracts.split(",")
        executor.set_pending_contract(PENDING_CONTRACTS)
    MODE = args.mode

    if not os.path.exists(RES_PATH):
        os.makedirs(RES_PATH)
    if not os.path.exists(EVALUATION_RES_PATH):
        os.makedirs(EVALUATION_RES_PATH)

    if MODE == 'FORMAL' or MODE == "TEST":
        ans = executor.fuzzing(EXEC_TIME_LIMIT, TEST_EPOCHS, GENERATE_TX_PER_EPOCH, MODE)
        print("Finished! Please check in result/ folder!")
    else:
        raise RuntimeError("Invalid mode, please check")