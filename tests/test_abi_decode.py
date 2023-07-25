from eth_abi import decode_abi, encode_abi

if __name__ == "__main__":
    # encode_ans = encode_abi(["uint256", "uint256", "uint256[]"], [123, 100, [1, 2]])
    # print(encode_ans)
    constructor_string = "00000000000000000000000000000000000000000000000000000000000000c0000000000000000000000000056b9aed2af1bfb967a94b20499bd7236156028a000000000000000000000000cc1d78a8c45b181da76ad8122e716540f720d448000000000000000000000000fb51c6154a694f63fe891085755c4131a7f0fa6000000000000000000000000053b6b6212b65b45956546cc83dafa20cffe22947000000000000000000000000f271597deaa770020f98605e73533c89bafb7b6d000000000000000000000000000000000000000000000000000000000000000400000000000000000000000095e0f97c3924a21ed0fcbbb4a851835091ba987a0000000000000000000000002646e6b5acb3626a77390d9f131256bd896ee276000000000000000000000000cbd75b09d3fdfdf3c229ceef774df6d5f84176a8000000000000000000000000c256059aba84c017220b94359fa4eacfa9a9bac8"

    b = bytes.fromhex(constructor_string)
    print(b)
    print(type(b'\x0a\xa0'))
    decode_ans = decode_abi(["address[]", "address", "address", "address", "address", "address"], b)
    print(decode_ans)
