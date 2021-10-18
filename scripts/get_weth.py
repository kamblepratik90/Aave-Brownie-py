from scripts.helpful_scripts import get_account
from brownie import interface, config, network

def main():
    get_weth()

def get_weth():
    """
    mint WETH by depositing ETH
    """
    account = get_account()
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])    
    tx = weth.deposit({"from": account, "value": 0.1 * 10 ** 18})
    tx.wait(1)
    print("received 0.1 WETH ")
    return tx


# def withdraw_weth():
#     """
#     mint WETH by depositing ETH
#     """
#     account = get_account()
#     weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])    
#     tx = weth.withdraw({"from" : account})
#     print("withdraw WETH to account")
#     return tx
