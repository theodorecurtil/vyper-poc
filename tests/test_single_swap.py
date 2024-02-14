#!/usr/bin/python3

import ape

def test_single_swap_input_usdc_to_wbtc(single_swap, owner, wbtc, usdc):

    usdc.approve(single_swap, 10000 *10 ** 6, sender=owner)

    single_swap.swapExactInputSingle(usdc, wbtc, 10000 * 10 ** 6, 0, sender=owner)
    assert wbtc.balanceOf(owner) > 0, "Did not receive tokenOut"
    assert usdc.balanceOf(owner) == 0, "Did not exactly swap all tokenIn"


def test_single_swap_without_approval_fails(single_swap, owner, wbtc, usdc):

    with ape.reverts():
        single_swap.swapExactInputSingle(usdc, wbtc, 0, 0, sender=owner)

    with ape.reverts():
        single_swap.swapExactOutputSingle(wbtc, usdc, 0, 0, sender=owner)


def test_single_swap_output_usdc_to_wbtc(single_swap, owner, wbtc, usdc):

    initial_balance_usdc = usdc.balanceOf(owner)

    amountOut = int(0.01 * 10 ** 8)             # amount of WBTC that we want
    amountInMaximum = usdc.balanceOf(owner)     # max amount of USDC we allow to swap

    usdc.approve(single_swap, amountInMaximum, sender=owner)    # approve spending of USDC

    single_swap.swapExactOutputSingle(usdc, wbtc, amountOut, amountInMaximum, sender=owner)
    assert wbtc.balanceOf(owner) == amountOut, f"Did not get the exact amount of WBTC expected ({wbtc.balanceOf(owner)} vs {amountOut})"

    final_balance_usdc = usdc.balanceOf(owner)
    balance_used = initial_balance_usdc - final_balance_usdc

    assert balance_used <= amountInMaximum, f"Used up more balance than expected for the swap ({balance_used} vs {amountInMaximum})"

def test_single_swap_output_fails_on_impossible_swap(single_swap, owner, wbtc, usdc):
    amountOut = 1 * 10 ** 8                     # amount of WBTC that we want, 1BTC but we have just $10k
    amountInMaximum = usdc.balanceOf(owner)     # max amount of USDC we allow to swap

    usdc.approve(single_swap, amountInMaximum, sender=owner)    # approve spending of USDC

    with ape.reverts():
        single_swap.swapExactOutputSingle(usdc, wbtc, amountOut, amountInMaximum, sender=owner)

def test_deposit_usdc(owner, single_swap, usdc, wbtc):
    # Deposit $10k USDC and check that swap occurs indeed
    amount_to_deposit = usdc.balanceOf(owner)
    usdc.approve(single_swap, amount_to_deposit, sender=owner)
    single_swap.deposit_numeraire(amount_to_deposit, sender=owner)
    assert usdc.balanceOf(owner) == 0
    assert wbtc.balanceOf(owner) > 0