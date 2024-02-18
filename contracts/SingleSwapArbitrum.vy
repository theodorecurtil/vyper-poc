# @version 0.3.10

"""
@title Uniswap Single Swap Contract
@license MIT
@author elefantoz
@notice Swap with single path two tokens on uniswap
@dev Implements the Uniswap ISwapRouter interface
"""

## EVENTS

event Swap:
    token_sold: address
    token_bought: address
    sold_amount: uint256
    bought_amount: uint256


# ===> INTERFACES <=== #

interface ERC20:  # ERC20 which works for USDC, WETH and WBTC, etc..
    def transfer(_to: address, _amount: uint256): nonpayable
    def transferFrom(_from: address, _to: address, _amount: uint256): nonpayable
    def approve(_spender: address, _value: uint256): nonpayable
    def allowance(_owner: address, _spender: address) -> uint256: view
    def balanceOf(_owner: address) -> uint256: view

# https://docs.uniswap.org/contracts/v3/guides/swaps/single-swaps
interface SwapRouter:
    def exactInputSingle(params: (address, address, uint24, address, uint256, uint256, uint256, uint160)) -> uint256: nonpayable
    def exactOutputSingle(params: (address, address, uint24, address, uint256, uint256, uint256, uint160)) -> uint256: nonpayable

interface ChainlinkPriceOracle:
    def latestAnswer() -> int256: view


# ===> CONSTANTS <=== #

## ETF

N_COINS: constant(int128) = 2                       # number of coins in ETF
ETF_COINS: constant(address[N_COINS]) = [
    0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f,     # WBTC
    0x82aF49447D8a07e3bd95BD0d56f35241523fBab1,     # WETH
]
COINS_PRECISIONS: constant(uint256[N_COINS]) = [
    10000000000,
    1,
]
COINS_WEIGHT: constant(uint256[N_COINS]) = [
    500000000000000000,
    500000000000000000,
]
PRECISION_WEIGHT: constant(uint256) = 1
TOLERANCE: constant(uint256) = 10 ** 16             # 1%

## NUMERAIRE

NUMERAIRE: constant(address) = 0xaf88d065e77c8cC2239327C5EDb3A432268e5831
NUMERAIRE_PRECISION: constant(uint256) = 1000000000000


## POOL FEE
POOL_FEE: constant(uint24) = 3000   # fee of 0.3%


## UNISWAP ROUTER
UNISWAP_ROUTER: constant(address) = 0xE592427A0AEce92De3Edee1F18E0157C05861564


## CHAINLINK ORACLES
CHAINLINK_ORACLES: constant(address[N_COINS]) = [
    0x6ce185860a4963106506C203335A2910413708e9,
    0x639Fe6ab55C921f74e7fac1ee960C0B6293ba612,
    ]
ORACLES_PRECISIONS: constant(uint256[N_COINS]) = [
    10000000000,
    10000000000,
]


# ===> STATE VARIABLES <=== #

uniswap_swap_router: public(SwapRouter)
owner: public(address)
policy_weights: public(uint256[N_COINS])


###########################################################################################
# ETF CONTRACT
###########################################################################################

@external
def __init__():
    self.owner = msg.sender
    self.uniswap_swap_router = SwapRouter(UNISWAP_ROUTER)
    self.policy_weights = COINS_WEIGHT

###########################################################################################
# INTERNAL FUNCTIONS
###########################################################################################

@internal
@view
def _get_underlying_spot_price(i: int128) -> uint256:
    return ORACLES_PRECISIONS[i] * convert(ChainlinkPriceOracle(CHAINLINK_ORACLES[i]).latestAnswer(), uint256)

@internal
@view
def _get_amount_out_min(quantity_in: uint256, i: int128) -> uint256:
    return 10 ** 18 * NUMERAIRE_PRECISION * quantity_in / self._get_underlying_spot_price(i) / COINS_PRECISIONS[i]

@internal
@view
def _get_nav_token(i: int128) -> uint256:
    return self._get_underlying_spot_price(i) * COINS_PRECISIONS[i] * ERC20(ETF_COINS[i]).balanceOf(self) / 10 ** 18 / NUMERAIRE_PRECISION

@internal
@view
def _get_nav() -> uint256:
    nav: uint256 = ERC20(NUMERAIRE).balanceOf(self)
    for i in range(N_COINS):
        nav += self._get_nav_token(i)

    return nav

@internal
@view
def _get_effective_weights() -> uint256[N_COINS]:
    """
    @dev To not multiply calls to the oracles, compute NAV token by token
    """
    nav: uint256 = 0
    nav_tokens: uint256[N_COINS] = empty(uint256[N_COINS])
    for i in range(N_COINS):
        nav_tokens[i] = self._get_nav_token(i)
        nav += nav_tokens[i]

    effective_weights: uint256[N_COINS] = empty(uint256[N_COINS])
    if nav == 0:
        return effective_weights

    for i in range(N_COINS):
        effective_weights[i] = 10 ** 18 * nav_tokens[i] / nav

    return effective_weights


@internal
def _swap_exact_input_single(tokenIn: address, tokenOut: address, amountIn: uint256, amountOutMin: uint256) -> uint256:
    
    # Approve for uni rooter to spend the tokenIn
    ERC20(tokenIn).approve(UNISWAP_ROUTER, amountIn)

    # make the swap
    amountOut: uint256 = self.uniswap_swap_router.exactInputSingle((
        tokenIn,
        tokenOut,
        POOL_FEE,
        self,
        block.timestamp,
        amountIn,
        amountOutMin,
        convert(0, uint160)
    ))

    log Swap(tokenIn, tokenOut, amountIn, amountOut)

    return amountOut

@internal
def _swap_exact_output_single(tokenIn: address, tokenOut: address, amountOut: uint256, amountInMaximum: uint256) -> uint256:
    
    # Approve for uni router to spend the tokenIn
    ERC20(tokenIn).approve(UNISWAP_ROUTER, amountInMaximum)

    # make the swap
    amountIn: uint256 = self.uniswap_swap_router.exactOutputSingle((
        tokenIn,
        tokenOut,
        POOL_FEE,
        self,
        block.timestamp,
        amountOut,
        amountInMaximum,
        convert(0, uint160)
    ))

    log Swap(tokenIn, tokenOut, amountIn, amountOut)

    return amountIn



###########################################################################################
# EXTERNAL FUNCTIONS
###########################################################################################

@external
@view
def get_underlying_spot_price(i: int128) -> uint256:
    """
    @notice Return the spot price of underlying token at index i
    @param i The index of the underlying token in the ETF
    """
    return self._get_underlying_spot_price(i)

@external
def swapExactInputSingle(tokenIn: address, tokenOut: address, amountIn: uint256, amountOutMin: uint256) -> uint256:
    """
    @notice NOT SAFE JUST FOR TESTS - Swap with uniswap router
    @param amountIn amount of token to swap (the amount that the user sends to the AMM)
    """

    assert msg.sender == self.owner

    # Transfer the specified amount of tokenIn to this contract.
    ERC20(tokenIn).transferFrom(msg.sender, self, amountIn)
    return self._swap_exact_input_single(tokenIn, tokenOut, amountIn, amountOutMin)

@external
def swapExactOutputSingle(tokenIn: address, tokenOut: address, amountOut: uint256, amountInMaximum: uint256) -> uint256:
    """
    @notice NOT SAFE JUST FOR TESTS - swapExactOutputSingle swaps a minimum possible amount of tokenIn for a fixed amount of tokenOut.
    @dev The calling address must approve this contract to spend its tokenIn for this function to succeed. As the amount of input tokenIn is variable, 
    the calling address will need to approve for a slightly higher amount, anticipating some variance.
    @param amountOut The exact amount of tokenOut to receive from the swap.
    @param amountInMaximum The amount of tokenIn we are willing to spend to receive the specified amount of tokenOut.
    @return amountIn The amount of tokenIn actually spent in the swap.
    """

    assert msg.sender == self.owner

    # Transfer the maximum amount of tokenIn to this contract.
    ERC20(tokenIn).transferFrom(msg.sender, self, amountInMaximum)
    
    amountIn: uint256 = self._swap_exact_output_single(tokenIn, tokenOut, amountOut, amountInMaximum)

    # For exact output swaps, the amountInMaximum may not have all been spent.
    # If the actual amount spent (amountIn) is less than the specified maximum amount, we must refund the msg.sender and approve the swapRouter to spend 0.
    if amountIn < amountInMaximum:
        ERC20(tokenIn).transfer(msg.sender, amountInMaximum - amountIn)

    return amountIn

@external
@view
def get_amount_out_min(quantity_in: uint256, i: int128) -> uint256:
    return self._get_amount_out_min(quantity_in, i)

@external
def deposit_numeraire(quantity: uint256):
    assert msg.sender == self.owner

    # transfer user's deposit to ETF
    ERC20(NUMERAIRE).transferFrom(msg.sender, self, quantity)

    # compute and swap respecting etf weights
    for i in range(N_COINS):
        numeraire_to_swap: uint256 = PRECISION_WEIGHT * self.policy_weights[i] * quantity / 10 ** 18
        # compute amount out min from oracle's price, 2.5% lower
        amountOutMin: uint256 = 975 * 10 ** 15 * self._get_amount_out_min(numeraire_to_swap, i) / 10 ** 18
        self._swap_exact_input_single(NUMERAIRE, ETF_COINS[i], numeraire_to_swap, amountOutMin)

@external
def flush_tokens(recipient: address):
    """
    @notice Safety method to send all the holdings of the contract to the owner, in case of emergency
    @param recipient address to send the tokens to
    """
    assert msg.sender == self.owner # dev: only owner can flush tokens
    for i in range(N_COINS):
        # transfer the balance to recipient
        token_balance: uint256 = ERC20(ETF_COINS[i]).balanceOf(self)
        ERC20(ETF_COINS[i]).transfer(recipient, token_balance)

    numeraire_balance: uint256 = ERC20(NUMERAIRE).balanceOf(self)
    ERC20(NUMERAIRE).transfer(recipient, numeraire_balance)

@external
@view
def get_nav() -> uint256:
    """
    @notice Return the current NAV of the ETF, expressed in units of numeraire
    """
    return self._get_nav()

@external
@view
def get_nav_token(i: int128) -> uint256:
    """
    @notice Return the NAV of the token at index i in ETF, in units of numeraire
    """
    return self._get_nav_token(i)

@external
@view
def get_effective_weights() -> uint256[N_COINS]:
    """
    @dev To not multiply calls to the oracles, compute NAV token by token
    """
    return self._get_effective_weights()

@external
def rebalance():
    # Compute effective weights
    effective_weights: uint256[N_COINS] = self._get_effective_weights()

    # Compute delta weights
    delta_weights: uint256[N_COINS] = empty(uint256[N_COINS])
    is_delta_positive: bool[N_COINS] = empty(bool[N_COINS])
    for i in range(N_COINS):
        if effective_weights[i] > self.policy_weights[i]:
            delta_weights[i] = effective_weights[i] - self.policy_weights[i]
            is_delta_positive[i] = True
            # Sell the token
            units_to_sell: uint256 = ERC20(ETF_COINS[i]).balanceOf(self) * delta_weights[i] / effective_weights[i]
            # Get min amount of numeraire
            min_amount_numeraire_out: uint256 = 975 * 10**15 * COINS_PRECISIONS[i] * units_to_sell * self._get_underlying_spot_price(i) / 10**18 / NUMERAIRE_PRECISION / 10**18
            self._swap_exact_input_single(ETF_COINS[i], NUMERAIRE, units_to_sell, min_amount_numeraire_out)

        else:
            delta_weights[i] = self.policy_weights[i] - effective_weights[i]
            is_delta_positive[i] = False

    # Now do the buys
    no_more_numeraire: bool = False
    max_amount_numeraire_in: uint256 = 0
    for i in range(N_COINS):
        if is_delta_positive[i]:
            continue
        units_to_buy: uint256 = ERC20(ETF_COINS[i]).balanceOf(self) * delta_weights[i] / effective_weights[i]
        numeraire_to_sell: uint256 = COINS_PRECISIONS[i] * units_to_buy * self._get_underlying_spot_price(i) / 10**18 / NUMERAIRE_PRECISION
        if numeraire_to_sell > ERC20(NUMERAIRE).balanceOf(self):
            numeraire_to_sell = ERC20(NUMERAIRE).balanceOf(self)
            no_more_numeraire = True
        amountOutMin: uint256 = 975 * 10 ** 15 * self._get_amount_out_min(numeraire_to_sell, i) / 10 ** 18
        self._swap_exact_input_single(NUMERAIRE, ETF_COINS[i], numeraire_to_sell, amountOutMin)
        if no_more_numeraire:
            break

    
@external
def set_policy_weights(new_weights: uint256[N_COINS]):
    assert msg.sender == self.owner # dev: only owner can change policy weights
    sum_weights: uint256 = 0
    for weight in new_weights:
        # check weight is greater than 1%
        assert weight >= 10 ** 16
        assert weight < 10 ** 18
        sum_weights += weight

    # normalize weights to 10 ** 18
    sum_new_weights: uint256 = 0
    for i in range(N_COINS):
        self.policy_weights[i] = 10**18 * new_weights[i] / sum_weights
        sum_new_weights += self.policy_weights[i]
    
    # distribute remaining
    diff: uint256 = 10 ** 18 - sum_new_weights
    if diff > 0:
        self.policy_weights[0] += diff

@external
def set_new_owner(new_owner: address):
    assert msg.sender == self.owner
    self.owner = new_owner

@external
def withdraw_numeraire_all(recipient: address):
    """
    @notice Withdraw the ETF to numeraire, and transfer it to the owner
    """
    assert msg.sender == self.owner # dev: only owner can withdraw
    for i in range(N_COINS):
        # Sell the token
        units_to_sell: uint256 = ERC20(ETF_COINS[i]).balanceOf(self)
        # Get min amount of numeraire
        min_amount_numeraire_out: uint256 = 975 * 10**15 * COINS_PRECISIONS[i] * units_to_sell * self._get_underlying_spot_price(i) / 10**18 / NUMERAIRE_PRECISION / 10**18
        self._swap_exact_input_single(ETF_COINS[i], NUMERAIRE, units_to_sell, min_amount_numeraire_out)

    ERC20(NUMERAIRE).transfer(recipient, ERC20(NUMERAIRE).balanceOf(self))

@external
@view
def am_i_the_owner() -> bool:
    """
    @notice Check whether the caller is the owner of the ETF
    """
    if msg.sender == self.owner:
        return True
    else:
        return False