#!/usr/bin/python3

from ape import Contract, accounts
import eth_utils
import pytest

wbtc_addresses_to_steal = ['0x5Ee5bf7ae06D1Be5997A1A72006FE6C607eC6DE8', '0x9ff58f4fFB29fA2266Ab25e75e2A8b3503311656', '0xa3A7B6F88361F48403514059F1F16C8E78d60EeC', '0xccF4429DB6322D5C611ee964527D42E5d685DD6a', '0xc3d688B66703497DAA19211EEdff47f25384cdc3', '0x40ec5B33f54e0E8A33A975908C5BA1c14e5BbbDf', '0x4197ba364AE6698015AE5c1468f54087602715b2', '0x7f62f9592b823331E012D3c5DdF2A7714CfB9de2', '0xBF72Da2Bd84c5170618Fbe5914B0ECA9638d5eb5', '0xfA8c996e158B80D77FbD0082BB437556A65B96E0', '0x6daB3bCbFb336b29d06B9C793AEF7eaA57888922', '0x99C9fc46f92E8a1c0deC1b1747d010903E884bE1', '0xE0438Eb3703bF871E31Ce639bd351109c88666ea', '0x77134cbC06cB00b66F4c7e623D5fdBF6777635EC', '0xCBCdF9626bC03E24f779434178A73a0B4bad62eD', '0xA489e9daf10cEd86811d59e4D00ce1b0DEC95f5e', '0x051d091B254EcdBBB4eB8E6311b7939829380b27', '0x8EB8a3b98659Cce290402893d0123abb75E3ab28', '0x1E227979f0b5BC691a70DEAed2e0F39a6F538FD5', '0x3ee18B2214AFF97000D974cf647E7C347E8fa585', '0x1Cb17a66DC606a52785f69F08F4256526aBd4943', '0x4F4495243837681061C4743b74B3eEdf548D56A5', '0x652356478073bA1D38b310850446d0A4C3Cad4BD', '0xe74b28c2eAe8679e3cCc3a94d5d0dE83CCB84705', '0x9cb4706e20A18E59a48ffa7616d700A3891e1861', '0x4bb7f4c3d47C4b431cb0658F44287d52006fb506', '0x693942887922785105088f04E9906D16188E9388', '0xbfE5E57Fa7A851F1F404e33A57E8FC5bf182DF06', '0xADc842a26b185897aC22042c99961F854Ca4395F', '0x28C6c06298d514Db089934071355E5743bf21d60', '0xCFFAd3200574698b78f32232aa9D63eABD290703', '0x000000000dFDe7deaF24138722987c9a6991e2D4', '0xD51a44d3FaE010294C616388b506AcdA1bfAAE46', '0x1d5A591EebB5BcB20F440D121e4f62e8d1689997', '0x4585FE77225b41b697C938B018E2Ac67Ac5a20c0', '0x33eeCc48943aAeabb5328A25ff28eb85F67945C2', '0x1d0C2555A0002A54dE13749af384223691bCb4d6', '0x292008a92060e038dd8C76F18346FA8bE6081717', '0xf5f5B97624542D72A9E06f04804Bf81baA15e2B4', '0x9Db9e0e53058C89e5B94e29621a205198648425B', '0xaB7b99998206D1ccf8B13b02b7566C267F4e2313', '0xCEfF51756c56CeFFCA006cD410B03FFC46dd3a58', '0x32467a5fc2d72D21E8DCe990906547A2b012f382', '0xC882b111A75C0c657fC507C04FbFcD2cC984F071', '0x21AA30C357D4102372Be8F32F7A3104c853BBe22', '0x98C3d3183C4b8A650614ad179A1a98be0a8d6B8E', '0x7576Fb92972796F0d7647F46B21755466d7a3bfA', '0xDFd5293D8e347dFe59E90eFd55b2956a1343963d', '0x7F86Bf177Dd4F3494b841a37e810A34dD56c829B', '0x5680b3FcBB64FB161adbD347BC92e8DDEDA97008']
usdc_addresses_to_steal = ['0xD6153F5af5679a75cC85D8974463545181f48772', '0x47ac0Fb4F2D84898e4D9E7b4DaB3C24507a6D503', '0xcEe284F754E854890e311e3280b767F80797180d', '0x0A59649758aa4d66E25f08Dd01271e891fe52199', '0x40ec5B33f54e0E8A33A975908C5BA1c14e5BbbDf', '0x5B541d54e79052B34188db9A43F7b00ea8E2C4B1', '0xAFAaDfa18D9d63d09F19a5445e29CEc601054C5e', '0x28C6c06298d514Db089934071355E5743bf21d60', '0xF977814e90dA44bFA03b6295A0616a897441aceC', '0xD54f502e184B6B739d7D27a6410a67dc462D69c8', '0x3ee18B2214AFF97000D974cf647E7C347E8fa585', '0x51eDF02152EBfb338e03E30d65C15fBf06cc9ECC', '0x68A99f89E475a078645f4BAC491360aFe255Dff1', '0xDa9CE944a37d218c3302F6B82a094844C6ECEb17', '0x99C9fc46f92E8a1c0deC1b1747d010903E884bE1', '0x7713974908Be4BEd47172370115e8b1219F4A5f0', '0xA9D1e08C7793af67e9d92fe308d5697FB81d3E43', '0xDFd5293D8e347dFe59E90eFd55b2956a1343963d', '0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640', '0x21a31Ee1afC51d94C2eFcCAa2092aD1028285549', '0x7eb6c83AB7D8D9B8618c0Ed973cbEF71d1921EF2', '0x5041ed759Dd4aFc3a72b8192C143F72f4724081A', '0x075C8071871130116ee08e7AE095101FB4b1BFB5', '0x57891966931Eb4Bb6FB81430E6cE0A03AAbDe063', '0x6F4565c9D673DBDD379ABa0b13f8088d1AF3Bb0C', '0x55FE002aefF02F77364de339a1292923A15844B8', '0x29a6B9807b327f656082D2e8b72dD07F275793f9', '0xdd442dC4D10eB9E86b8B462ed0959BEd85A48888', '0x9beb4656220a6e95176a8412EE641Ea5724E91ba', '0xD8D7377EB56Cf99b9f49337e88b284A0b648c69e', '0xC8e04176F9adcF973eBa4b35AeFfbf495501e6b3', '0xf4392E751FCE0ac172F871f2799657EDF89eaCA7', '0x4D8193D235A74aA191197Edf8C5Bde5489B1Ab00', '0x6aC8305620256719006C51779a0794A1911550a6', '0x66d856B36E058B2D1399D15D5909D7680C2747D0', '0xC3017993D708DD2c17726b08046Ff58955b6fBb3', '0xae2809B006B9305386B2b20f661355E427bc992C', '0xa44DfAb175f57Ef58eAE7b8b7Ed2472640fd4610', '0x73f3f1E7E422B31E3A9bf0D05c73782fE2A19188', '0xC288621786e5E75d00acbbf47EE0B2705e24eD2B', '0xAe2D4617c862309A3d75A0fFB358c7a5009c673F', '0x59a0f98345f54bAB245A043488ECE7FCecD7B596', '0x756D64Dc5eDb56740fC617628dC832DDBCfd373c', '0x78605Df79524164911C144801f41e9811B7DB73D', '0xf89d7b9c864f589bbF53a82105107622B35EaA40', '0x504e06927D7146210aB05CE0165DbcD7206b782F', '0xC44DF5b832a734A2eEfd04F45e450FB20e4e6B62', '0xBe5115b02739c3Ab3e7d9521D552122917f0B038', '0x497299e27C89Ec78AA9Fc24A0f60EdE28fD511C2', '0xCdC10753b8Ee96873105790EDCdD50efc4991927']

@pytest.fixture(scope="module")
def owner(accounts):
    return accounts[0]

@pytest.fixture(scope="module")
def receiver(accounts):
    return accounts[1]

@pytest.fixture(scope="module")
def hacker(accounts):
    return accounts[2]

@pytest.fixture(scope="module")
def is_forked():
    return True

@pytest.fixture(scope="module")
def wbtc(owner, project):
    if is_forked:
        wbtc = Contract('0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599')
        amount = 0 * 10 ** 8
        for address in wbtc_addresses_to_steal:
            address = eth_utils.to_checksum_address(address)
            balance = wbtc.balanceOf(address)
            if not balance:
                continue
            if amount > balance:
                with accounts.use_sender(address):
                    try:
                        wbtc.transfer(owner, balance, sender=address)
                    except Exception as e:
                        print(address, e)
                amount -= balance
            else:
                with accounts.use_sender(address):
                    try:
                        wbtc.transfer(owner, amount, sender=address)
                    except Exception as e:
                        print(address, e)
                    else:
                        break
    else:
        wbtc = owner.deploy(project.Token, "Dummy WBTC", "WBTC", 8, 10 ** 8)
    return wbtc

@pytest.fixture(scope="module")
def usdc(owner, project):
    if is_forked:
        usdc = Contract('0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48')
        amount = 10000 * 10 ** 6
        for address in usdc_addresses_to_steal:
            address = eth_utils.to_checksum_address(address)
            balance = usdc.balanceOf(address)
            if not balance:
                continue
            if amount > balance:
                with accounts.use_sender(address):
                    try:
                        usdc.transfer(owner, balance, sender=address)
                    except Exception as e:
                        print(address, e)
                amount -= balance
            else:
                with accounts.use_sender(address):
                    try:
                        usdc.transfer(owner, amount, sender=address)
                    except Exception as e:
                        print(address, e)
                    else:
                        break
    else:
        usdc = owner.deploy(project.Token, "Dummy USDC", "USDC", 6, 100000 ** 6)
    return usdc

@pytest.fixture(scope="module")
def single_swap(owner, project):
    return owner.deploy(project.SingleSwap)

