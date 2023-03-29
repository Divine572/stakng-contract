import json
import os
from web3 import Web3
from dotenv import load_dotenv
from solcx import compile_standard, install_solc

load_dotenv()

# Install specific Solidity compiler version
install_solc("0.8.0")


# Set up web3 connection
provider_url = os.environ.get("CELO_PROVIDER_URL")
w3 = Web3(Web3.HTTPProvider(provider_url))
assert w3.is_connected(), "Not connected to a Celo node"

# Set deployer account and private key
deployer = os.environ.get("CELO_DEPLOYER_ADDRESS")
private_key = os.environ.get("CELO_DEPLOYER_PRIVATE_KEY")


with open("Staking.sol", "r") as file:
    contract_source_code = file.read()


# Compile the contract
compiled_sol = compile_standard({
    "language": "Solidity",
    "sources": {
        "Staking.sol": {
            "content": contract_source_code
        }
    },
    "settings": {
        "outputSelection": {
            "*": {
                "*": ["metadata", "evm.bytecode", "evm.sourceMap"]
            }
        }
    }
})

# Extract the contract data
contract_data = compiled_sol['contracts']['Staking.sol']['Staking']
bytecode = contract_data['evm']['bytecode']['object']
abi = json.loads(contract_data['metadata'])['output']['abi']


# Deploy the contract

# Prepare the contract object
contract = w3.eth.contract(abi=abi, bytecode=bytecode)

cUSDToken = "0x874069Fa1Eb16D44d622F2e0Ca25eeA172369bC1"
CELOToken = "0xF194afDf50B03e69Bd7D057c1Aa9e10c9954E4C9"
stakingPeriod = 30 * 24 * 60 * 60  # 30 days

# Estimate gas for contract deployment
gas_estimate = contract.constructor(cUSDToken, CELOToken, stakingPeriod).estimate_gas()

nonce = w3.eth.get_transaction_count(deployer)

# Prepare the transaction
transaction = {
    'from': deployer,
    'gas': gas_estimate,
    'gasPrice': w3.eth.gas_price,
    'nonce': nonce,
    'data': bytecode
}


signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
transaction_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
transaction_receipt = w3.eth.wait_for_transaction_receipt(transaction_hash)

# Get the contract address
contract_address = transaction_receipt['contractAddress']
print(f"Contract deployed at address: {contract_address}")

