from typing import Optional

import eth_utils
from brownie import accounts, network
from brownie.network.contract import ContractTx

LOCAL_BLOCKCHAIN_ENVIRONMENTS = {
    "development",
    "ganache-local",
    "mainnet-fork",
}


def get_account(index: Optional[int] = None, id: Optional[str] = None):
    if index:
        return accounts[index]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]
    if id:
        return accounts.load(id)
    else:
        return accounts.load("meta")


def encode_function_data(initializer: ContractTx = None, *args) -> bytes:
    """
    Encodes the function call so we can work with an initialzier

    Args:
        initializer ([brownie.network.contract.ContractTx], optional):
        The initializer function we want to call. Example: `box.store`.
        Defaults to None.

        args (Any, optional):
        The arguments to pass to the initializer function

    Returns:
        [bytes]: Return the encoded bytes
    """
    if len(args) == 0 or not initializer:
        return eth_utils.to_bytes(hexstr="0x")
    return initializer.encode_input(*args)


def upgrade(
    account,
    proxy,
    new_implementation_address,
    proxy_admin_contract=None,
    initializer=None,
    *args,
):
    if proxy_admin_contract:
        if initializer:
            encoded_function_call = encode_function_data(initializer, *args)
            transaction = proxy_admin_contract.upgardeAndCall(
                proxy.address,
                new_implementation_address,
                encode_function_data,
                {"from": account},
            )
        else:
            transaction = proxy_admin_contract.upgrade(
                proxy.address, new_implementation_address, {"from": account}
            )
    else:
        if initializer:
            encoded_function_call = encode_function_data(initializer, *args)
            transaction = proxy.upgradeToAndCall(
                new_implementation_address, encoded_function_call, {"from": account}
            )
        else:
            transaction = proxy.upgradeTo(new_implementation_address, {"from": account})
    return transaction
