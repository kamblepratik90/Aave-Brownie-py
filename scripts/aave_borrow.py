from scripts.helpful_scripts import get_account
from brownie import interface, config, network
from scripts.get_weth import get_weth
from web3 import Web3

amount = Web3.toWei(0.01, "ether")

def main():
    account = get_account()
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    if network.show_active() in ["mainnet-fork"]:
        get_weth()
    lending_pool = get_lending_pool()
    print(lending_pool)
    approve_ERC20(amount, lending_pool.address, erc20_address, account)
    print("depositing")
    tx = lending_pool.deposit(erc20_address, amount, account.address, 0, {"from" : account})
    tx.wait(1)
    print("Deposited!")
    # borrow how much?..
    available_borrow_eth, total_debt_eth = get_borrowable_user_data(lending_pool, account)
    print("lets borrow DAI now")
    # DAI interms of ETH
    dai_eth_price = get_asset_price(config["networks"][network.show_active()]["dai_eth_price_feed"])
    # we multiply by 0.95 as a buffer to make sure the health factor better
    amount_dai_to_boroow = (1/dai_eth_price) * (available_borrow_eth * 0.95)
    # borrowable ETH -> borrowble DAI * 0.95
    print(f"We are going to borrow {amount_dai_to_boroow} DAI")
    # borrow DAI now
    dai_address = config["networks"][network.show_active()]["dai_token"]
    borrow_tx = lending_pool.borrow(dai_address, Web3.toWei(amount_dai_to_boroow, "ether"), 1, 0, account.address, {"from": account})
    borrow_tx.wait(1)
    print("we borrowed DAI success")
    get_borrowable_user_data(lending_pool, account)
    # repay
    repay_all(amount, lending_pool, account, dai_address)
    print("Just Deposited, borrowed and repayed Successfully with AAVE, BROWNIE and CHAINLINK !!!")

def repay_all(amount, lending_pool, account, dai_address):
    approve_ERC20(Web3.toWei(amount, "ether"), lending_pool, dai_address, account)
    repay_tx = lending_pool.repay(dai_address, amount, 1, account.address, {"from": account})
    repay_tx.wait(1)
    print("Repaid!")    


def get_asset_price(price_feed_address):
    # ABI
    # Address
    dai_eth_price = interface.AggregatorV3Interface(price_feed_address)
    latest_price = dai_eth_price.latestRoundData()[1];
    converted_latest_price = Web3.fromWei(latest_price, "ether")
    print(f"the latest DAI/ETH price is {converted_latest_price}")
    return float(converted_latest_price)    


def get_borrowable_user_data(lending_pool, account):
    (total_collatral_eth, total_debt_eth, available_borrow_eth, current_liquidation_threshold, ltv, health_factor) = lending_pool.getUserAccountData(account.address)    
    available_borrow_eth = Web3.fromWei(available_borrow_eth, "ether")
    total_collatral_eth = Web3.fromWei(total_collatral_eth, "ether")
    total_debt_eth = Web3.fromWei(total_debt_eth, "ether")

    print(f"You have {total_collatral_eth} worth of ETH deposited.")
    print(f"You have {total_debt_eth} worth of ETH borrowed.")
    print(f"You can borrow {available_borrow_eth} worth of ETH.")
    return(float(available_borrow_eth), float(total_debt_eth))

def approve_ERC20(amount, spender, erc20_address, account):
    print("Approvinf ERC20")
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(spender, amount, {"from": account})
    tx.wait(1)
        # AIB
        # Address 
    print("Approved!")
    return tx

def get_lending_pool():
    lending_pool_address_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_address_provider"])    
    lending_pool_address = lending_pool_address_provider.getLendingPool()
    lending_pool = interface.ILendingPool(lending_pool_address)
    return lending_pool



