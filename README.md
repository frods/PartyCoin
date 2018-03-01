# PartyCoin Solidity Contract

This repo contains the definision of the PartyCoin Ethereum smart contracts.

These contracts create a root generator contract which creates party contracts.

A party contract is a way for people to contribute to a party in exchange for party tokens.
The tokens can be used at the event in exchange for activities or items.

At the end of the event the creator will receive the ether used to buy tokens.

The owner of the generator script will receive 6% of the ether contributed.

Including [tests](tests) to validate that the contract works as expected.

## Running locally

To build the contract and run the tests on OSX:

First install dependencies and set up the python virtualenv environment by running:

```
bootstrap.sh
```

Compile the contract and run the test with:

```
populus compile
py.test tests
```

## Deploying the contract

The contract can be deployed to the Ethereum blockchain using the Mist wallet.

It is advisable to first deploy to the test blockchain before comitting real ether.

