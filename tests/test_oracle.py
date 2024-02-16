#!/usr/bin/python3

import json
import requests

def test_wbtc_price(single_swap):
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    price = json.loads(requests.get(url).content).get("bitcoin").get("usd")

    assert (single_swap.get_underlying_spot_price(0) / 10**18) > price * 0.95
    assert (single_swap.get_underlying_spot_price(0) / 10**18) < price * 1.05

def test_amount_out_min(owner, usdc, single_swap):
    # check that given an input quantity of USDC, we can calculate a meaningful amont of WBTC to expect from uniswap
    amount_numeraire_to_swap = usdc.balanceOf(owner)
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    price = json.loads(requests.get(url).content).get("bitcoin").get("usd")

    expected_amount_coingecko = amount_numeraire_to_swap / price / 10 ** 6
    assert (single_swap.get_amount_out_min(amount_numeraire_to_swap, 0) / 10**8) > expected_amount_coingecko * 0.95
    assert (single_swap.get_amount_out_min(amount_numeraire_to_swap, 0) / 10**8) < expected_amount_coingecko * 1.05

def test_nav_empty(single_swap):
    # check that NAV is 0 when no tokens are in the ETF
    assert single_swap.get_nav() == 0, "NAV should be zero"

def test_nav_transfer_usdc(single_swap, usdc, owner):
    usdc_amount = usdc.balanceOf(owner)
    usdc.transfer(single_swap, usdc_amount, sender=owner)
    assert single_swap.get_nav() == usdc_amount, f"NAV should be {usdc_amount}, not {single_swap.get_nav()}"

def test_nav_after_deposit(single_swap, usdc, owner):
    usdc_amount = usdc.balanceOf(owner)
    usdc.approve(single_swap, usdc_amount, sender=owner)
    single_swap.deposit_numeraire(usdc_amount, sender=owner)
    assert single_swap.get_nav() > 0.95 * usdc_amount, f"NAV too small ({single_swap.get_nav()})"
    assert single_swap.get_nav() < 1.05 * usdc_amount, f"NAV too large ({single_swap.get_nav()})"

def test_nav_single_token(single_swap, usdc, owner):
    usdc_amount = usdc.balanceOf(owner)
    usdc.approve(single_swap, usdc_amount, sender=owner)
    single_swap.deposit_numeraire(usdc_amount, sender=owner)
    assert single_swap.get_nav_token(0) > 0.95 * usdc_amount / 2, f"NAV too small ({single_swap.get_nav_token(0)})"
    assert single_swap.get_nav_token(0) < 1.05 * usdc_amount / 2, f"NAV too large ({single_swap.get_nav_token(0)})"