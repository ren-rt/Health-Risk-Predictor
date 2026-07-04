import { useState } from 'react';
import './PredictorPage.css';

const FIELDS = [
  { id: 'patient_id', label: 'Patient ID', placeholder: 'e.g. PT-20240704', unit: null, type: 'text' },
  { id: 'age', label: 'Age', placeholder: 'e.g. 28', unit: 'yrs', type: 'number' },
  { id: 'systolic_bp', label: 'Systolic Blood Pressure', placeholder: 'e.g. 118', unit: 'mmHg', type: 'number' },
  { id: 'diastolic_bp', label: 'Diastolic Blood Pressure', placeholder: 'e.g. 76', unit: 'mmHg', type: 'number' },
  { id: 'bs', label: 'Blood Sugar (BS)', placeholder: 'e.g. 6.5', unit: 'mmol/L', type: 'number' },
  { id: 'body_temp', label: 'Body Temperature', placeholder: 'e.g. 37.0', unit: '°C', type: 'number' },
  { id: 'heart_rate', label: 'Heart Rate', placeholder: 'e.g. 72', unit: 'bpm', type: 'number' },
];

const STAT_ORDER = [
  { key: 'systolic_bp', label: 'SBP', unit: 'mmHg' },
  { key: 'diastolic_bp', label: 'DBP', unit: 'mmHg' },
  { key: 'bs', label: 'BS', unit: 'mmol' },
  { key: 'body_temp', label: 'Temp', unit: '°C' },
  { key: 'heart_rate', label: 'HR', unit: 'bpm' },
  { key: 'age', label: 'Age', unit: 'yrs' },
];

const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:5000';

function riskTier(risk) {
  const r = risk.toLowerCase();
  if (r.includes('high')) return 'high';
  if (r.includes('mid')) return 'mid';
  return 'low';
}

export default function PredictorPage() {
  const [values, setValues] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const handleChange = (id, val) => {
    setValues((prev) => ({ ...prev, [id]: val }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    setResult(null);

    try {
      const res = await fetch(`${API_BASE}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(values),
      });
      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.error || 'Prediction failed');
      }

      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="predictor-page">
      <section className="hero">
        <h1 className="hero-title">
          Maternal Health <span className="hero-title-accent">Risk Predictor</span>
        </h1>
        <p className="hero-subtitle">
          Analyzes maternal vital signs using a trained ML model to predict risk levels,
          generates plain-English clinical guidance, and securely logs every prediction to
          an immutable blockchain for tamper-proof medical history.
        </p>

        <div className="feature-grid">
          <div className="feature-card">
            <h3>ML-Powered Prediction</h3>
            <p>Real-time risk scoring from validated clinical features across seven vital parameters.</p>
          </div>
          <div className="feature-card">
            <h3>AI Health Advice</h3>
            <p>Plain-English guidance generated for each patient's specific vital profile.</p>
          </div>
          <div className="feature-card">
            <h3>Blockchain-Secured Records</h3>
            <p>Every prediction is cryptographically logged and independently verifiable.</p>
          </div>
        </div>
      </section>

      <section className="form-section">
        <form className="vitals-card" onSubmit={handleSubmit}>
          <div className="vitals-card-header">
            <h2>Enter Patient Vitals</h2>
            <p>All fields required for accurate risk assessment</p>
          </div>

          <div className="vitals-grid">
            {FIELDS.map((field) => (
              <div className="field" key={field.id}>
                <label htmlFor={field.id}>{field.label}</label>
                <div className="field-input-wrap">
                  <input
                    id={field.id}
                    type={field.type}
                    step={field.type === 'number' ? 'any' : undefined}
                    placeholder={field.placeholder}
                    required
                    value={values[field.id] || ''}
                    onChange={(e) => handleChange(field.id, e.target.value)}
                  />
                  {field.unit && <span className="field-unit">{field.unit}</span>}
                </div>
              </div>
            ))}
          </div>

          <button type="submit" className="predict-btn" disabled={loading}>
            {loading ? 'Predicting…' : 'Predict Risk'} {!loading && <span aria-hidden="true">→</span>}
          </button>

          {error && <p className="form-error">{error}</p>}
        </form>
      </section>

      {result && <ResultSection result={result} vitals={values} />}

      <footer className="page-footer">
        For clinical decision support only — not a substitute for professional medical judgment.
      </footer>
    </div>
  );
}

function ResultSection({ result, vitals }) {
  const tier = riskTier(result.risk);
  const chainOk = result.blockchain_status === 'logged';

  return (
    <section className="result-section">
      <div className={`result-card tier-${tier}`}>
        <div className="result-header">
          <div>
            <p className="result-eyebrow">Prediction Result</p>
            <p className="result-patient">
              Patient <strong>{result.patient_id}</strong>, {vitals.age} yrs
            </p>
          </div>
          <div className={`risk-badge tier-${tier}`}>
            <span className="risk-badge-icon" aria-hidden="true">✓</span>
            {result.risk.toUpperCase()}
            <span className="risk-badge-conf">{Math.round(result.confidence)}% conf.</span>
          </div>
        </div>

        <div className="result-divider" />

        <div className="stat-grid">
          {STAT_ORDER.map((s) => (
            <div className="stat" key={s.key}>
              <span className="stat-label">{s.label}</span>
              <span className="stat-value">{vitals[s.key]}</span>
              <span className="stat-unit">{s.unit}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="advice-card">
        <div className="advice-card-header">
          <span className="advice-icon" aria-hidden="true">⊕</span>
          <h3>AI Health Advice</h3>
        </div>
        <p className="advice-text">{result.ai_advice}</p>
      </div>

      <div className={`chain-strip ${chainOk ? 'ok' : 'warn'}`}>
        <span className="chain-icon" aria-hidden="true">▦</span>
        <div>
          <p className="chain-status">
            {chainOk ? 'Logged to Blockchain' : `Blockchain: ${result.blockchain_status}`}
          </p>
          {result.tx_hash && <p className="chain-hash">{result.tx_hash}</p>}
        </div>
      </div>
    </section>
  );
}