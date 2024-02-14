#!/usr/bin/python3

def test_effective_weight_no_token(single_swap):
    effective_weights = single_swap.get_effective_weights()
    for w in effective_weights:
        assert w == 0, "Weight should be zero, since no tokens are in the ETF"

def test_deposit_respects_policy_weights(single_swap, owner, usdc):
    # deposit in ETF
    usdc.approve(single_swap, usdc.balanceOf(owner), sender=owner)
    single_swap.deposit_numeraire(usdc.balanceOf(owner), sender=owner)

    # retrieve policy weights and effective weights
    effective_weights = single_swap.get_effective_weights()
    for i in range(len(effective_weights)):
        assert effective_weights[i] > 0.95 * single_swap.policy_weights(i)
        assert effective_weights[i] < 1.05 * single_swap.policy_weights(i)