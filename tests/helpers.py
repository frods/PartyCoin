from contextlib import contextmanager

def validate_contract_state(contract, state, balances=None):
    '''
    Validate contract state using accessor methods.

    balanances: a list if tuples specifying address, value for each balance to be checked
    '''
    balances = balances or []

    for key, value in state.items():
        if key == "balances":
            for address, value in balances:
                assert contract.call().balanceOf(address) == value
        else:
            assert getattr(contract.call(), key)() == value


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
