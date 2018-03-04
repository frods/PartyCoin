pragma solidity ^0.4.19;

import "./Owned.sol";
import "./Party.sol";

/// @title Generator creates party contracts.
/// @author frods
contract Generator is Owned {
    string public name;

    event PartyStarted(string name, string symbol, address party);

    function Generator(string _name) public {
        name = _name;
    }

    function createParty(string name, string symbol, uint256 tokenRate) public {
        address newParty = new Party(name, symbol, tokenRate, owner);
        PartyStarted(name, symbol, newParty);
    }
}