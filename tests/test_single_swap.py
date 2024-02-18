#!/usr/bin/python3

import ape

def test_owner_is_owner(single_swap, owner, hacker):
    # check that the owner is actually the owner
    assert single_swap.owner() == owner, "The owner that deployed the contract does not seem to be contract s owner"

    # check that the hacker cannot flush the ETF
    with ape.reverts():
        single_swap.flush_tokens(hacker, sender=hacker)

def test_owner_can_flush_etf(single_swap, owner, receiver, usdc):
    # send some tokens to the single_swap contract
    owner_balance = usdc.balanceOf(owner)
    usdc.transfer(single_swap, owner_balance, sender=owner)

    # flush contract
    single_swap.flush_tokens(receiver, sender=owner)
    assert usdc.balanceOf(receiver) == owner_balance

def test_single_swap_input_usdc_to_wbtc(single_swap, owner, wbtc, usdc):
    # This takes the usdc of the user, and converts it to wbtc in the contract

    usdc.approve(single_swap, 10000 *10 ** 6, sender=owner)

    single_swap.swapExactInputSingle(usdc, wbtc, 10000 * 10 ** 6, 0, sender=owner)
    assert wbtc.balanceOf(single_swap) > 0, "Did not receive tokenOut"
    assert usdc.balanceOf(owner) == 0, "Did not exactly swap all tokenIn"
    assert wbtc.balanceOf(owner) == 0, "should not have received wbtc in the process"


def test_single_swap_without_approval_fails(single_swap, owner, wbtc, usdc):

    with ape.reverts():
        single_swap.swapExactInputSingle(usdc, wbtc, 0, 0, sender=owner)

    with ape.reverts():
        single_swap.swapExactOutputSingle(wbtc, usdc, 0, 0, sender=owner)


def test_single_swap_output_usdc_to_wbtc(single_swap, owner, wbtc, usdc):
    # swap exactly 
    initial_balance_usdc = usdc.balanceOf(owner)

    amountOut = int(0.01 * 10 ** 8)             # amount of WBTC that we want
    amountInMaximum = usdc.balanceOf(owner)     # max amount of USDC we allow to swap

    usdc.approve(single_swap, amountInMaximum, sender=owner)    # approve spending of USDC

    single_swap.swapExactOutputSingle(usdc, wbtc, amountOut, amountInMaximum, sender=owner)
    assert wbtc.balanceOf(single_swap) == amountOut, f"Did not get the exact amount of WBTC expected ({wbtc.balanceOf(owner)} vs {amountOut})"

    final_balance_usdc = usdc.balanceOf(owner)
    balance_used = initial_balance_usdc - final_balance_usdc

    assert balance_used <= amountInMaximum, f"Used up more balance than expected for the swap ({balance_used} vs {amountInMaximum})"

def test_single_swap_output_usdc_to_little_wbtc(single_swap, owner, wbtc, usdc):
    # check that because not all usdc will be consumed, it will come back.
    initial_balance_usdc = usdc.balanceOf(owner)

    amountOut = int(0.00001 * 10 ** 8)          # amount of WBTC that we want
    amountInMaximum = usdc.balanceOf(owner)     # max amount of USDC we allow to swap

    usdc.approve(single_swap, amountInMaximum, sender=owner)    # approve spending of USDC

    single_swap.swapExactOutputSingle(usdc, wbtc, amountOut, amountInMaximum, sender=owner)
    assert wbtc.balanceOf(single_swap) == amountOut, f"Did not get the exact amount of WBTC expected ({wbtc.balanceOf(owner)} vs {amountOut})"

    assert usdc.balanceOf(owner) > 0

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
    assert wbtc.balanceOf(single_swap) > 0
    assert wbtc.balanceOf(owner) == 0
    assert usdc.balanceOf(single_swap) == 0

def test_deposit_usdc_and_flush(owner, single_swap, usdc, wbtc, receiver):
    # Deposit $5k USDC and send the other $5k to SC. Then flush
    amount_to_deposit = usdc.balanceOf(owner) // 2
    usdc.approve(single_swap, amount_to_deposit, sender=owner)
    single_swap.deposit_numeraire(amount_to_deposit, sender=owner)
    # Send the remaining to SC
    usdc.transfer(single_swap, usdc.balanceOf(owner), sender=owner)
    assert usdc.balanceOf(owner) == 0
    assert wbtc.balanceOf(single_swap) > 0
    assert usdc.balanceOf(single_swap) > 0

    # Flush
    single_swap.flush_tokens(receiver, sender=owner)
    assert wbtc.balanceOf(single_swap) == 0
    assert usdc.balanceOf(single_swap) == 0
    assert usdc.balanceOf(receiver) > 0
    assert wbtc.balanceOf(receiver) > 0

def test_withdraw_to_numeraire(single_swap, owner, receiver, usdc, wbtc):
    # owner initial amount usdc
    initial_usdc_amount = usdc.balanceOf(owner)

    # Deposit $5k USDC and send the other $5k to SC. Then flush
    amount_to_deposit = usdc.balanceOf(owner) // 2
    usdc.approve(single_swap, amount_to_deposit, sender=owner)
    single_swap.deposit_numeraire(amount_to_deposit, sender=owner)
    # Send the remaining to SC
    usdc.transfer(single_swap, usdc.balanceOf(owner), sender=owner)
    assert usdc.balanceOf(owner) == 0
    assert wbtc.balanceOf(single_swap) > 0
    assert usdc.balanceOf(single_swap) > 0

    # Withdraw
    single_swap.withdraw_numeraire_all(receiver, sender=owner)
    assert wbtc.balanceOf(single_swap) == 0
    assert usdc.balanceOf(single_swap) == 0
    assert usdc.balanceOf(receiver) > 0
    assert wbtc.balanceOf(receiver) == 0
    assert usdc.balanceOf(receiver) > 0.95 * initial_usdc_amount
    assert usdc.balanceOf(receiver) < 1.05 * initial_usdc_amount
    