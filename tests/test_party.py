'''
Validate that Party.sol performs as expected.

Roughy validates that the contract conforms to ERC20 
https://github.com/ethereum/EIPs/blob/master/EIPS/eip-20.md
'''

import pytest
import ethereum
import random
from helpers import *

DEFAULT_NAME = "Party"
DEFAULT_SYMBOL = "P"
DEFAULT_TOKENRATE = 10

DEFAULT_STATE = {
    "name": DEFAULT_NAME,
    "symbol": DEFAULT_SYMBOL,
    "tokenRate": DEFAULT_TOKENRATE,
    "partyActive": True,
}


def validate_contract(contract, **args):
    validate_contract_state(contract, {**DEFAULT_STATE, **args})


@pytest.fixture
def contract(chain, web3):
    contract, _ = chain.provider.get_or_deploy_contract(
        'Party', deploy_args=(DEFAULT_NAME, DEFAULT_SYMBOL, DEFAULT_TOKENRATE, web3.eth.coinbase))
    return contract


@pytest.fixture
def closed_contract(contract, chain, web3):
    close_txn_hash = contract.transact().endParty()
    txn_result = chain.wait.for_receipt(close_txn_hash)
    return contract


def test_create(contract, web3):
    validate_contract(contract, owner=web3.eth.coinbase, generator=web3.eth.coinbase)


def test_buy_zero_tokens(contract, chain, web3):
    buy_txn_hash = contract.transact().buyTokens()
    txn_result = chain.wait.for_receipt(buy_txn_hash)

    assert txn_result.gasUsed == 28783
    validate_contract(
        contract,
        balances=[(web3.eth.coinbase, 0)])
    
    event_filter = contract.on('TokensPurchased')
    events = event_filter.get()

    validate_events(
        events, [
            {'event': 'TokensPurchased',
             'args': {
                 'buyer': web3.eth.coinbase,
                 'ammount': 0
                 }
            }
        ]
    )

def test_buy_ten_tokens(contract, chain, web3):
    num_tokens = 10
    ether_ammount = int(num_tokens / DEFAULT_TOKENRATE)
    other_account = web3.eth.accounts[1]
    gas_cost = 43783
    # Ensure other_account has some ether
    transfer_hash = web3.eth.sendTransaction(
        {"from": web3.eth.coinbase, "to": other_account, "value": ether_ammount})
    chain.wait.for_receipt(transfer_hash)
    
    with verify_balance_change(web3, other_account, -(ether_ammount + gas_cost)):
        with verify_balance_change(web3, contract.address, ether_ammount):
            buy_txn_hash = contract.transact({"from": other_account, "value": ether_ammount}).buyTokens()
            txn_result = chain.wait.for_receipt(buy_txn_hash)
            assert txn_result.gasUsed == gas_cost

    validate_contract(
        contract,
        balances=[(other_account, num_tokens)])
    
    event_filter = contract.on('TokensPurchased')
    events = event_filter.get()

    validate_events(
        events, [
            {'event': 'TokensPurchased',
             'args': {
                 'buyer': other_account,
                 'ammount': num_tokens
                 }
            }
        ]
    )

def test_buy_random_number_tokens(contract, chain, web3):
    ether_ammount = random.randint(0, 100000000)
    num_tokens = ether_ammount * DEFAULT_TOKENRATE
    other_account = web3.eth.accounts[1]
    gas_cost = 43783
    # Ensure other_account has some ether
    transfer_hash = web3.eth.sendTransaction(
        {"from": web3.eth.coinbase, "to": other_account, "value": ether_ammount})
    chain.wait.for_receipt(transfer_hash)
    
    with verify_balance_change(web3, other_account, -(ether_ammount + gas_cost)):
        with verify_balance_change(web3, contract.address, ether_ammount):
            buy_txn_hash = contract.transact({"from": other_account, "value": ether_ammount}).buyTokens()
            txn_result = chain.wait.for_receipt(buy_txn_hash)
            assert txn_result.gasUsed == gas_cost

    validate_contract(
        contract,
        balances=[(other_account, num_tokens)])
    
    event_filter = contract.on('TokensPurchased')
    events = event_filter.get()

    validate_events(
        events, [
            {'event': 'TokensPurchased',
             'args': {
                 'buyer': other_account,
                 'ammount': num_tokens
                 }
            }
        ]
    )


def test_end_party(chain, web3):
    ether_ammount = 100000;
    other_account = web3.eth.accounts[1]
    # Ensure other_account has some ether
    transfer_hash = web3.eth.sendTransaction(
        {"from": web3.eth.coinbase, "to": other_account, "value": ether_ammount})
    chain.wait.for_receipt(transfer_hash)
    other_account2 = web3.eth.accounts[2]

    contract, _ = chain.provider.get_or_deploy_contract(
        'Party', deploy_args=(DEFAULT_NAME, DEFAULT_SYMBOL, DEFAULT_TOKENRATE, other_account2))

    buy_ammount = 100
    buy_txn_hash = contract.transact({"from": other_account, "value": 100}).buyTokens()
    txn_result = chain.wait.for_receipt(buy_txn_hash)

    with verify_balance_change(web3, other_account2, buy_ammount * 0.06):
        close_txn_hash = contract.transact().endParty()
        txn_result = chain.wait.for_receipt(close_txn_hash)
        assert txn_result.gasUsed == 44472
    validate_contract(
        contract,
        partyActive=False)

    event_filter = contract.on('PartyFinished')
    events = event_filter.get()

    validate_events(
        events,
        [
            {'event': 'PartyFinished'}
        ])


def test_buy_party_over(closed_contract, chain, web3):
    with pytest.raises(ethereum.tester.TransactionFailed):
        buy_txn_hash = closed_contract.transact().buyTokens()

    validate_contract(
        closed_contract,
        partyActive=False)
    
    event_filter = closed_contract.on('TokensPurchased')
    events = event_filter.get()

    validate_events(events)
