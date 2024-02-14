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

N_COINS: constant(int128) = 1   # number of coins in ETF
ETF_COINS: constant(address[N_COINS]) = [
    0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599,
]
COINS_PRECISIONS: constant(uint256[N_COINS]) = [
    10000000000,
]
COINS_WEIGHT: constant(uint256[N_COINS]) = [
    1000000000000000000
]
PRECISION_WEIGHT: constant(uint256) = 1

## NUMERAIRE

NUMERAIRE: constant(address) = 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48
NUMERAIRE_PRECISION: constant(uint256) = 1000000000000


## POOL FEE
POOL_FEE: constant(uint24) = 3000   # fee of 0.3%


## UNISWAP ROUTER
UNISWAP_ROUTER: constant(address) = 0xE592427A0AEce92De3Edee1F18E0157C05861564


## CHAINLINK ORACLES
CHAINLINK_ORACLES: constant(address[N_COINS]) = [
    0xF4030086522a5bEEa4988F8cA5B36dbC97BeE88c
    ]
ORACLES_PRECISIONS: constant(uint256[N_COINS]) = [
    10000000000
]


# ===> STATE VARIABLES <=== #

uniswap_swap_router: public(SwapRouter)
owner: public(address)


@external
def __init__():
    self.owner = msg.sender
    self.uniswap_swap_router = SwapRouter(UNISWAP_ROUTER)

@internal
@view
def _get_underlying_spot_price(i: int128) -> uint256:
    return ORACLES_PRECISIONS[i] * convert(ChainlinkPriceOracle(CHAINLINK_ORACLES[i]).latestAnswer(), uint256)

@internal
@view
def _get_amount_out_min(quantity_in: uint256, i: int128) -> uint256:
    return 10 ** 18 * NUMERAIRE_PRECISION * quantity_in / self._get_underlying_spot_price(i) / COINS_PRECISIONS[i]

@internal
def _swap_exact_input_single(tokenIn: address, tokenOut: address, amountIn: uint256, amountOutMin: uint256) -> uint256:
    
    # Approve for uni rooter to spend the tokenIn
    ERC20(tokenIn).approve(UNISWAP_ROUTER, amountIn)

    # make the swap
    amountOut: uint256 = self.uniswap_swap_router.exactInputSingle((
        tokenIn,
        tokenOut,
        POOL_FEE,
        msg.sender,
        block.timestamp,
        amountIn,
        amountOutMin,
        convert(0, uint160)
    ))

    log Swap(tokenIn, tokenOut, amountIn, amountOut)

    return amountOut


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
    @notice Swap with uniswap router
    @param amountIn amount of token to swap (the amount that the user sends to the AMM)
    """

    # Transfer the specified amount of tokenIn to this contract.
    ERC20(tokenIn).transferFrom(msg.sender, self, amountIn)
    return self._swap_exact_input_single(tokenIn, tokenOut, amountIn, amountOutMin)

@external
def swapExactOutputSingle(tokenIn: address, tokenOut: address, amountOut: uint256, amountInMaximum: uint256) -> uint256:
    """
    @notice swapExactOutputSingle swaps a minimum possible amount of tokenIn for a fixed amount of tokenOut.
    @dev The calling address must approve this contract to spend its tokenIn for this function to succeed. As the amount of input tokenIn is variable, 
    the calling address will need to approve for a slightly higher amount, anticipating some variance.
    @param amountOut The exact amount of tokenOut to receive from the swap.
    @param amountInMaximum The amount of tokenIn we are willing to spend to receive the specified amount of tokenOut.
    @return amountIn The amount of tokenIn actually spent in the swap.
    """
    # msg.sender must approve the contract to spend tokenIn
    assert ERC20(tokenIn).allowance(msg.sender, self) >= amountInMaximum, "Allowance insufficient"

    # Transfer the specified amount of tokenIn to this contract.
    ERC20(tokenIn).transferFrom(msg.sender, self, amountInMaximum)
    ERC20(tokenIn).approve(UNISWAP_ROUTER, amountInMaximum)

    # make the swap
    amountIn: uint256 = self.uniswap_swap_router.exactOutputSingle((
        tokenIn,
        tokenOut,
        POOL_FEE,
        msg.sender,
        block.timestamp,
        amountOut,
        amountInMaximum,
        convert(0, uint160)
    ))
    # For exact output swaps, the amountInMaximum may not have all been spent.
    # If the actual amount spent (amountIn) is less than the specified maximum amount, we must refund the msg.sender and approve the swapRouter to spend 0.
    if amountIn < amountInMaximum:
        # ERC20(USDC).approve(UNISWAP_ROUTER, 0)
        ERC20(tokenIn).transfer(msg.sender, amountInMaximum - amountIn)

    return amountIn

@external
@view
def get_amount_out_min(quantity_in: uint256, i: int128) -> uint256:
    return self._get_amount_out_min(quantity_in, i)

@external
def deposit_numeraire(quantity: uint256):

    # transfer user's deposit to ETF
    ERC20(NUMERAIRE).transferFrom(msg.sender, self, quantity)

    # compute and swap respecting etf weights
    for i in range(N_COINS):
        numeraire_to_swap: uint256 = PRECISION_WEIGHT * COINS_WEIGHT[i] * quantity / 10 ** 18
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
