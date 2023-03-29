import os
from web3 import Web3
from web3.middleware import geth_poa_middleware

import deploy


# Set up web3 connection
provider_url = os.environ.get("CELO_PROVIDER_URL")
w3 = Web3(Web3.HTTPProvider(provider_url))
assert w3.is_connected(), "Not connected to a Celo node"

# Add PoA middleware to web3.py instance
w3.middleware_onion.inject(geth_poa_middleware, layer=0)


abi = deploy.abi
contract_address = deploy.contract_address
account_address = deploy.deployer
private_key = deploy.private_key

contract = w3.eth.contract(address=contract_address, abi=abi)


# Stake tokens
def stake(amount):
    nonce = w3.eth.get_transaction_count(account_address)
    txn = contract.functions.stake(amount).build_transaction({
        'from': account_address,
        'gas': 200000,
        'gasPrice': w3.eth.gas_price,
        'nonce': nonce
    })

    signed_txn = w3.eth.account.sign_transaction(txn, private_key)
    txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    txn_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
    print("Staked:", amount, "cUSD")



# Unstake tokens
def unstake():
    nonce = w3.eth.get_transaction_count(account_address)
    txn = contract.functions.unstake().build_transaction({
        'from': account_address,
        'gas': 200000,
        'gasPrice': w3.eth.gas_price,
        'nonce': nonce
    })

    signed_txn = w3.eth.account.sign_transaction(txn, private_key)
    txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    txn_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
    print("Unstaked and claimed rewards")



# Check staking information for a user
def get_staking_info(user_address):
    info = contract.functions.stakingInfo(user_address).call()
    print("Staking Info for", user_address)
    print("Amount:", info[0])
    print("Start Time:", info[1])
    print("Claimed:", info[2])


# Replace this with the desired action
action = 'stake'  # 'unstake' or 'get_staking_info'

if action == 'stake':
    stake_amount = 100  # Replace with the desired staking amount
    stake(stake_amount)
elif action == 'unstake':
    unstake()
elif action == 'get_staking_info':
    user_address = account_address  # Replace with the desired user's address
    get_staking_info(user_address)
