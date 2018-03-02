pragma solidity ^0.4.19;

import "./Owned.sol";

/// @title Party creates party contracts.
/// @author frods
contract Party is Owned {
    event TokensPurchased(address buyer, uint256 ammount);

    string public name;
    string public symbol;
    uint256 public tokenCost;
    mapping (address => uint256) private balances;

    address public generator;

    function Party(string _name, string _symbol, uint256 _tokenCost, address _generator) public {
        name = _name;
        symbol = _symbol;
        tokenCost = _tokenCost;
        generator = _generator;
    }

    /// @notice Query balance for an account
    /// @param _owner The address to query
    function balanceOf(address _owner) public returns (uint256) {
        return balances[_owner];
    }

    function buyTokens() public payable {
        uint256 tokens = msg.value / tokenCost;
        balances[msg.sender] += tokens;
        TokensPurchased(msg.sender, tokens);
    }
}