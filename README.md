# Health Risk Predictor

A maternal health risk assessment tool that combines a machine learning model, an optional local LLM for plain-English advice, and a blockchain-backed audit trail for patient records.

Given six basic vitals (age, blood pressure, blood sugar, body temperature, heart rate), the app predicts whether a patient is **low**, **mid**, or **high** risk, generates a short AI explanation of that result, and logs the prediction on-chain so patient history can be retrieved and verified later.

## How it works

1. **Predict** — A Flask API loads a trained scikit-learn model (plus scaler and label encoder) and classifies the submitted vitals into a risk level with a confidence score.
2. **Explain** — The predicted risk and vitals are passed to a local [Ollama](https://ollama.com/) model, which returns a short, plain-English summary and suggested next steps. If Ollama isn't running, the app falls back gracefully and the rest of the flow still works.
3. **Log** — The prediction, confidence, and AI advice are written to a `MedicalRecords` smart contract on a local Ganache blockchain, keyed by patient ID, so a full history can be queried per patient.
4. **Review** — A React frontend lets you submit new predictions and browse a patient's stored history.

## Model

Trained on the [Maternal Health Risk Data (Kaggle)](https://www.kaggle.com/datasets/csafrit2/maternal-health-risk-data), comparing Logistic Regression against a Random Forest classifier (with SMOTE to handle class imbalance). Random Forest was selected as the final model:

| Model | Accuracy |
|---|---|
| Logistic Regression | 0.61 |
| Random Forest | 0.88 |

See `notebooks/maternal_health_risk.ipynb` for the full EDA, preprocessing, and evaluation.

## Project structure

```
app/                  Flask backend (API, templates, Ollama client)
frontend/             React + Vite frontend
blockchain/           Solidity contract, deploy script, Web3 client
model/                Trained model, scaler, label encoder (pickled)
notebooks/            Training notebook + dataset
Dockerfile            Backend image
Dockerfile.frontend   Frontend image
docker-compose.yml    Full stack: Ganache, contract deployer, Ollama, backend, frontend
requirements.txt      Python dependencies
```

## Tech stack

- **ML**: scikit-learn, imbalanced-learn, pandas, numpy
- **Backend**: Flask, Flask-CORS
- **AI advice**: Ollama (default model `llama3.2:1b`)
- **Blockchain**: Solidity, Web3.py, py-solc-x, Ganache
- **Frontend**: React 19, React Router, Vite

## Running with Docker (recommended)

This spins up everything — a local blockchain (Ganache), automatic smart contract deployment, Ollama with the model pre-pulled, the Flask API, and the React frontend.

```bash
docker compose up --build
```

- Frontend: [http://localhost:5173](http://localhost:5173)
- Backend API: [http://localhost:5000](http://localhost:5000)
- Ganache RPC: `http://localhost:7545`
- Ollama: `http://localhost:11434`

The `deployer` service compiles and deploys `MedicalRecords.sol` to Ganache and writes the resulting contract address to a shared volume, which the backend reads on startup — no manual contract setup needed.

## Running locally (without Docker)

**Backend**

```bash
pip install -r requirements.txt
# Ganache must be running locally (e.g. via the Ganache app or `npx ganache`)
python blockchain/deploy.py
python app/app.py
```

**Frontend**

```bash
cd frontend
npm install
npm run dev
```

**Ollama (optional, for AI advice)**

```bash
ollama pull llama3.2:1b
ollama serve
```

If Ollama isn't running, predictions still work — the `ai_advice` field just returns a fallback message noting it was unavailable.

### Environment variables

| Variable | Default | Description |
|---|---|---|
| `GANACHE_URL` | `http://127.0.0.1:7545` | RPC endpoint for the blockchain |
| `DEPLOY_OUTPUT_PATH` | `/shared/contract_address.txt` | Where the deployed contract address is written/read |
| `CONTRACT_ADDRESS` | — | Skip auto-detection and point directly at a deployed contract |
| `OLLAMA_URL` | `http://127.0.0.1:11434` | Ollama server endpoint |
| `OLLAMA_MODEL` | `llama3` | Model used for AI advice |

## API

**`POST /predict`**

```json
{
  "patient_id": "p001",
  "age": 29,
  "systolic_bp": 120,
  "diastolic_bp": 80,
  "bs": 7.2,
  "body_temp": 98.6,
  "heart_rate": 76
}
```

Returns the predicted risk level, confidence, AI advice, and blockchain transaction status.

**`GET /history/<patient_id>`**

Returns all predictions previously stored on-chain for that patient.

## Disclaimer

This tool is for educational purposes and is not a substitute for professional medical advice, diagnosis, or treatment. The AI-generated advice explicitly avoids providing a definitive diagnosis.
