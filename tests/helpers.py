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


def _validate_target(target, event):
    for key, value in iter(target.items()):
        if isinstance(value, dict):
            _validate_target(value, event[key])
        else:
            assert event[key] == value


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
        _validate_target(target, event)


@contextmanager
def verify_balance_change(web3, account, expected_change):
    '''
    Track balance trange accross context.
    Assert that change equals expected change
    '''
    original_balance = web3.eth.getBalance(account)
    yield
    final_balance = web3.eth.getBalance(account)
    print('change', final_balance - original_balance)
    assert final_balance - original_balance == expected_change
