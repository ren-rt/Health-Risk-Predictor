import pickle
import numpy as np
import os
import sys
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # React dev server runs on a different port (e.g. localhost:3000)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, '..', 'model')

# Make the sibling blockchain/ folder importable
sys.path.insert(0, os.path.join(BASE_DIR, '..', 'blockchain'))
import blockchain  # noqa: E402

from ollama_client import get_ai_advice

# Load model, scaler, and label encoder
with open(os.path.join(MODEL_DIR, 'maternal_model.pkl'), 'rb') as f:
    model = pickle.load(f)

with open(os.path.join(MODEL_DIR, 'scaler.pkl'), 'rb') as f:
    scaler = pickle.load(f)

with open(os.path.join(MODEL_DIR, 'label_encoder.pkl'), 'rb') as f:
    le = pickle.load(f)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({'error': 'JSON body required'}), 400

        patient_id = str(data.get('patient_id', '')).strip()
        if not patient_id:
            return jsonify({'error': 'patient_id is required'}), 400

        vitals_dict = {
            'age': float(data['age']),
            'systolic_bp': float(data['systolic_bp']),
            'diastolic_bp': float(data['diastolic_bp']),
            'bs': float(data['bs']),
            'body_temp': float(data['body_temp']),
            'heart_rate': float(data['heart_rate']),
        }
        features = np.array([list(vitals_dict.values())])

        scaled = scaler.transform(features)
        prediction = model.predict(scaled)
        probability = model.predict_proba(scaled).max() * 100
        risk_label = le.inverse_transform(prediction)[0]

        # --- AI advice (optional, degrades gracefully if Ollama is down) ---
        ai_advice = get_ai_advice(vitals_dict, risk_label)

        # --- Blockchain logging ---
        try:
            blockchain.store_prediction_on_chain(
                patient_id, str(risk_label), probability, ai_advice
            )
            chain_status = 'logged'
        except Exception as e:
            chain_status = f'failed ({e.__class__.__name__})'

        return jsonify({
            'patient_id': patient_id,
            'risk': risk_label,
            'confidence': round(probability, 2),
            'ai_advice': ai_advice,
            'blockchain_status': chain_status,
            'timestamp': datetime.utcnow().isoformat(),
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/history/<patient_id>')
def get_history(patient_id):
    try:
        records = blockchain.get_patient_history(patient_id)
        return jsonify({'patient_id': patient_id, 'records': records})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)