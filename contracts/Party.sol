pragma solidity ^0.4.19;

import "./Owned.sol";

/// @title Party creates party contracts.
/// @author frods
contract Party is Owned {
    event TokensPurchased(address indexed buyer, uint256 ammount);
    event PartyFinished();

    string public name;
    string public symbol;
    uint256 public tokenRate;
    mapping (address => uint256) private balances;

    bool public partyActive;

    address public generator;

    function Party(string _name, string _symbol, uint256 _tokenRate, address _generator) public {
        name = _name;
        symbol = _symbol;
        tokenRate = _tokenRate;
        generator = _generator;
        partyActive = true;
    }

    /**
    * @dev Throws if the party isn't on
    */
    modifier partyOn() {
        require(partyActive);
        _;
    }

    /// @notice Query balance for an account
    /// @param _owner The address to query
    function balanceOf(address _owner) public returns (uint256) {
        return balances[_owner];
    }

    /// Buy tokens with wei
    /// tokenRate * wei tokens are added to balance
    function buyTokens() public payable partyOn {
        uint256 tokens = tokenRate * msg.value;
        balances[msg.sender] += tokens;
        TokensPurchased(msg.sender, tokens);
    }

    /// End the party and 
    function endParty() public onlyOwner partyOn{
        partyActive = false;
        PartyFinished();
    }
}