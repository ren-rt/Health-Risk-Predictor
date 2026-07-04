import os
import json
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

GANACHE_URL = os.getenv("GANACHE_URL", "http://127.0.0.1:7545")
CONTRACT_ADDRESS_RAW = os.getenv("CONTRACT_ADDRESS")

if not CONTRACT_ADDRESS_RAW:
    raise RuntimeError(
        "CONTRACT_ADDRESS not set. Copy .env.example to .env and fill in "
        "the address from your own Ganache deployment."
    )

w3 = Web3(Web3.HTTPProvider(GANACHE_URL))

if w3.is_connected():
    print(f"Connected to Ganache at {GANACHE_URL}")
else:
    print(f"Failed to connect to Ganache at {GANACHE_URL}")

CONTRACT_ADDRESS = Web3.to_checksum_address(CONTRACT_ADDRESS_RAW)

ABI_PATH = os.path.join(os.path.dirname(__file__), "contract_abi.json")
with open(ABI_PATH) as f:
    CONTRACT_ABI = json.load(f)

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

# Ganache's first pre-funded account sends the transactions
DEFAULT_ACCOUNT = w3.eth.accounts[0]


def store_prediction_on_chain(patient_id, risk_level, confidence, ai_advice):
    """
    Stores a prediction record on the blockchain.
    confidence should be a float like 85.5 (converted to int for Solidity).
    """
    confidence_int = int(confidence * 100)  # 85.5 -> 8550

    print(f"[blockchain] Sending storePrediction to {CONTRACT_ADDRESS} "
          f"from {DEFAULT_ACCOUNT} for patient {patient_id}")

    tx_hash = contract.functions.storePrediction(
        patient_id,
        risk_level,
        confidence_int,
        ai_advice,
    ).transact({"from": DEFAULT_ACCOUNT})

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    print(f"[blockchain] tx hash: {tx_hash.hex()}")
    print(f"[blockchain] tx to: {receipt['to']}")
    print(f"[blockchain] status: {receipt.status}")
    print(f"[blockchain] logs: {receipt.logs}")

    if receipt.status != 1:
        raise RuntimeError(f"Transaction reverted on-chain: {tx_hash.hex()}")

    if len(receipt.logs) == 0:
        raise RuntimeError(
            f"Transaction mined but emitted no events (tx: {tx_hash.hex()}). "
            "storePrediction should always emit RecordStored — something is wrong."
        )

    return receipt


def get_patient_history(patient_id):
    """Returns all stored predictions for a given patient_id."""
    records = contract.functions.getPatientHistory(patient_id).call()

    formatted = []
    for r in records:
        formatted.append({
            "patientId": r[0],
            "riskLevel": r[1],
            "confidence": r[2] / 100,  # back to e.g. 85.5
            "aiAdvice": r[3],
            "timestamp": r[4],
        })
    return formatted


def get_record_count(patient_id):
    return contract.functions.getRecordCount(patient_id).call()