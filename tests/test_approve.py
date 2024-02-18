#!/usr/bin/python3

def test_approve_usdc(single_swap, owner, usdc):
    usdc.approve(single_swap, 10000 * 10 ** 6, sender=owner)

    assert usdc.allowance(owner, single_swap) == 10000 * 10 ** 6

def test_set_new_owner(single_swap, owner, receiver):

    assert single_swap.owner() == owner

    # set new owner
    single_swap.set_new_owner(receiver, sender=owner)
    assert single_swap.owner() == receiver