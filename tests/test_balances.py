#!/usr/bin/python3

import pytest


def test_owner_has_zero_wbtc(wbtc, owner):
    assert wbtc.balanceOf(owner) == 0 * 10 ** 8

def test_owner_has_usdc(usdc, owner):
    assert usdc.balanceOf(owner) == 10000 * 10 ** 6
