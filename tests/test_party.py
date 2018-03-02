'''
Validate that Party.sol performs as expected.

Roughy validates that the contract conforms to ERC20 
https://github.com/ethereum/EIPs/blob/master/EIPS/eip-20.md
'''

import pytest
import ethereum
from contextlib import contextmanager

DEFAULT_NAME = "Party"
DEFAULT_SYMBOL = "P"
DEFAULT_TOKENCOST = 10

def validate_contract_state( #pylint: disable=invalid-name
        # Arguments are named after the contract accessor methods
        contract,
        name=DEFAULT_NAME,
        symbol=DEFAULT_SYMBOL,
        tokenCost=DEFAULT_TOKENCOST,
        owner=None,
        generator=None,
        balances=None):
    '''
    Validate contract state using accessor methods.

    balanances: a list if tuples specifying address, value for each balance to be checked
    '''
    balances = balances or []
    assert contract.call().name() == name
    assert contract.call().symbol() == symbol
    assert contract.call().tokenCost() == tokenCost
    if owner:
        assert contract.call().owner() == owner
    if generator:
        assert contract.call().generator() == generator
    for address, value in balances:
        assert contract.call().balanceOf(address) == value


def validate_events(events, expected=None):
    '''
    Validate given events

    expected: list of dictionaries specifying events. Only supplied keys are checked so
        only a subset of the full event need be specified.
    '''
    expected = expected or []
    assert len(events) == len(expected)
    for index, target in enumerate(expected):
        event = events[index]
        for key, value in iter(target.items()):
            assert event[key] == value


@contextmanager
def verify_balance_change(web3, account, expected_change):
    '''
    Track balance trange accross context.
    Assert that change equals expected change
    '''
    original_balance = web3.eth.getBalance(account)
    yield
    final_balance = web3.eth.getBalance(account)
    assert final_balance - original_balance == expected_change


@pytest.fixture
def contract(chain, web3):
    contract, _ = chain.provider.get_or_deploy_contract(
        'Party', deploy_args=(DEFAULT_NAME, DEFAULT_SYMBOL, DEFAULT_TOKENCOST, web3.eth.coinbase))
    return contract


def test_create(contract, web3):
    validate_contract_state(contract, owner=web3.eth.coinbase, generator=web3.eth.coinbase)


def test_buy_zero_tokens(contract, chain, web3):
    buy_txn_hash = contract.transact().buyTokens()
    txn_result = chain.wait.for_receipt(buy_txn_hash)

    assert txn_result.gasUsed == 28432
    validate_contract_state(
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
    ether_ammount = num_tokens * DEFAULT_TOKENCOST
    other_account = web3.eth.accounts[1]
    gas_cost = 43432
    # Ensure other_account has some ether
    transfer_hash = web3.eth.sendTransaction(
        {"from": web3.eth.coinbase, "to": other_account, "value": ether_ammount})
    chain.wait.for_receipt(transfer_hash)
    
    with verify_balance_change(web3, other_account, -(ether_ammount + gas_cost)):
        with verify_balance_change(web3, contract.address, ether_ammount):
            buy_txn_hash = contract.transact({"from": other_account, "value": ether_ammount}).buyTokens()
            txn_result = chain.wait.for_receipt(buy_txn_hash)

    assert txn_result.gasUsed == gas_cost
    validate_contract_state(
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

def test_buy_partial_tokens(contract, chain, web3):
    num_tokens = 10.5
    extra_ether = 0
    ether_ammount = int((num_tokens * DEFAULT_TOKENCOST) + extra_ether)
    other_account = web3.eth.accounts[1]
    gas_cost = 43432
    # Ensure other_account has some ether
    transfer_hash = web3.eth.sendTransaction(
        {"from": web3.eth.coinbase, "to": other_account, "value": ether_ammount})
    chain.wait.for_receipt(transfer_hash)
    
    with verify_balance_change(web3, other_account, -(ether_ammount + gas_cost)):
        with verify_balance_change(web3, contract.address, ether_ammount):
            buy_txn_hash = contract.transact({"from": other_account, "value": ether_ammount}).buyTokens()
            txn_result = chain.wait.for_receipt(buy_txn_hash)

    assert txn_result.gasUsed == gas_cost
    validate_contract_state(
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
