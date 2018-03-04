'''
Validate that Generator.sol performs as expected.
'''

import pytest
import ethereum
from helpers import *

DEFAULT_NAME = "Party Generator"

DEFAULT_STATE = {
    "name": DEFAULT_NAME,
}


def validate_contract(contract, **args):
    validate_contract_state(contract, {**DEFAULT_STATE, **args})


@pytest.fixture
def contract(chain):
    contract, _ = chain.provider.get_or_deploy_contract(
        'Generator', deploy_args=(DEFAULT_NAME, ))
    return contract

def test_create(contract, web3):
    validate_contract(contract, owner=web3.eth.coinbase)

def test_createParty(contract, chain, web3):
    partyName = "Great party"
    partySymbol = "GP"
    partyTokenRate = 10
    createParty_txn_hash = contract.transact().createParty(partyName, partySymbol, partyTokenRate)
    txn_result = chain.wait.for_receipt(createParty_txn_hash)

    assert txn_result.gasUsed == 648773

    event_filter = contract.on('PartyStarted')
    events = event_filter.get()

    validate_events(
        events, [
            {'event': 'PartyStarted',
             'args': {
                 'name': partyName,
                 'symbol': partySymbol,
                 }
            }
        ]
    )
