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