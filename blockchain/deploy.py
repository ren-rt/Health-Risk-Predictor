"""
Compiles MedicalRecords.sol and deploys it to whatever Ganache is
running at GANACHE_URL, then writes the resulting contract address
to a shared file so the Flask app can pick it up automatically.

Run once, at startup, before the Flask app starts (see docker-compose.yml).
"""
import os
import json
import time

from web3 import Web3
from solcx import compile_standard, install_solc

GANACHE_URL = os.getenv("GANACHE_URL", "http://127.0.0.1:7545")
OUTPUT_PATH = os.getenv("DEPLOY_OUTPUT_PATH", "/shared/contract_address.txt")
SOL_PATH = os.path.join(os.path.dirname(__file__), "MedicalRecords.sol")

# --- 1. Wait for Ganache to actually be ready ---
w3 = Web3(Web3.HTTPProvider(GANACHE_URL))
for attempt in range(30):
    if w3.is_connected():
        print(f"[deploy] Connected to Ganache at {GANACHE_URL}")
        break
    print(f"[deploy] Waiting for Ganache... ({attempt + 1}/30)")
    time.sleep(1)
else:
    raise RuntimeError(f"Could not connect to Ganache at {GANACHE_URL}")

# --- 2. Compile the contract fresh ---
install_solc("0.8.19")

with open(SOL_PATH, "r") as f:
    source_code = f.read()

compiled = compile_standard(
    {
        "language": "Solidity",
        "sources": {"MedicalRecords.sol": {"content": source_code}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "evm.bytecode.object"]}
            }
        },
    },
    solc_version="0.8.19",
)

contract_data = compiled["contracts"]["MedicalRecords.sol"]["MedicalRecords"]
abi = contract_data["abi"]
bytecode = contract_data["evm"]["bytecode"]["object"]

# --- 3. Deploy using Ganache's first pre-funded account ---
account = w3.eth.accounts[0]
Contract = w3.eth.contract(abi=abi, bytecode=bytecode)

tx_hash = Contract.constructor().transact({"from": account})
receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
contract_address = receipt.contractAddress

print(f"[deploy] Deployed MedicalRecords at {contract_address}")

# --- 4. Write the address (and fresh ABI, for good measure) so Flask can read it ---
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
with open(OUTPUT_PATH, "w") as f:
    f.write(contract_address)

abi_out_path = os.path.join(os.path.dirname(OUTPUT_PATH), "contract_abi.json")
with open(abi_out_path, "w") as f:
    json.dump(abi, f)

print(f"[deploy] Wrote address to {OUTPUT_PATH}")
print("[deploy] Done.")