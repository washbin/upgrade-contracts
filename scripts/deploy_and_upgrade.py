from brownie import (
    Box,
    BoxV2,
    Contract,
    ProxyAdmin,
    TransparentUpgradeableProxy,
    network,
)

from scripts.helpers import encode_function_data, get_account, upgrade


def main():
    account = get_account()
    print(f"Deploying to {network.show_active()}")
    box = Box.deploy(
        {"from": account},
    )
    print(box.retrieve())

    proxy_admin = ProxyAdmin.deploy(
        {"from": account},
    )

    # initializer = box.store, 1
    box_encoded_initializer = encode_function_data()

    proxy = TransparentUpgradeableProxy.deploy(
        box.address,
        proxy_admin.address,
        box_encoded_initializer,
        {"from": account, "gas_limit": 1_000_000},
    )
    print(f"Proxy deployed to {proxy}, you can now upgrade to v2!")
    proxy_box = Contract.from_abi("Box", proxy.address, Box.abi)
    proxy_box.store(18, {"from": account})
    print(proxy_box.retrieve())

    # upgrade
    box_v2 = BoxV2.deploy(
        {"from": account},
    )
    upgrade_tx = upgrade(
        account, proxy, box_v2.address, proxy_admin_contract=proxy_admin
    )
    upgrade_tx.wait(1)
    print("Proxy has been upgraded!")
    proxy_box = Contract.from_abi("Box2", proxy.address, BoxV2.abi)
    proxy_box.increment({"from": account})
    print(proxy_box.retrieve())
