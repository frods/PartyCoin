pragma solidity ^0.4.19;

import "./Owned.sol";
import "./Party.sol";

/// @title Generator creates party contracts.
/// @author frods
contract Generator is Owned {
    event PartyStarted(string name, string symbol, address party);

    function createParty(string name, string symbol, uint256 tokenCost) onlyOwner public returns (address) {
        address newParty = new Party(name, symbol, tokenCost, owner);
        PartyStarted(name, symbol, newParty);
    }
}