from web3 import Web3
import json
import os

# Connect to Ganache
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))

# Verify connection
if w3.is_connected():
    print("Connected to Ganache")
else:
    print("Failed to connect to Ganache")

# Your deployed contract address (from Remix)
CONTRACT_ADDRESS = Web3.to_checksum_address("0xd9145CCE52D386f254917e481eB44e9943F39138")

# Load ABI from file
with open(os.path.join(os.path.dirname(__file__), 'contract_abi.json')) as f:
    CONTRACT_ABI = json.load(f)

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

# Use Ganache's first account to send transactions (it has test ETH)
DEFAULT_ACCOUNT = w3.eth.accounts[0]


def store_prediction_on_chain(patient_id, risk_level, confidence, ai_advice):
    """
    Stores a prediction record on the blockchain.
    confidence should be a float like 85.5 (we convert to int for Solidity)
    """
    confidence_int = int(confidence * 100)  # 85.5 -> 8550

    tx_hash = contract.functions.storePrediction(
        patient_id,
        risk_level,
        confidence_int,
        ai_advice
    ).transact({'from': DEFAULT_ACCOUNT})

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return receipt


def get_patient_history(patient_id):
    """
    Returns all stored predictions for a given patient_id.
    """
    records = contract.functions.getPatientHistory(patient_id).call()

    # records is a list of tuples: (patientId, riskLevel, confidence, aiAdvice, timestamp)
    formatted = []
    for r in records:
        formatted.append({
            "patientId": r[0],
            "riskLevel": r[1],
            "confidence": r[2] / 100,  # convert back to e.g. 85.5
            "aiAdvice": r[3],
            "timestamp": r[4]
        })
    return formatted


def get_record_count(patient_id):
    return contract.functions.getRecordCount(patient_id).call()  
