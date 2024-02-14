#!/usr/bin/python3

def test_approve_usdc(single_swap, owner, usdc):
    usdc.approve(single_swap, 10000 * 10 ** 6, sender=owner)

    assert usdc.allowance(owner, single_swap) == 10000 * 10 ** 6
