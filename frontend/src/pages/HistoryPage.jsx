import { useState } from 'react';
import './HistoryPage.css';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:5000';

export default function HistoryPage() {
  const [patientId, setPatientId] = useState('');
  const [records, setRecords] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    setError(null);
    setRecords(null);
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/history/${encodeURIComponent(patientId.trim())}`);
      const data = await res.json();

      if (!res.ok) throw new Error(data.error || 'Lookup failed');
      setRecords(data.records || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="history-page">
      <div className="history-header">
        <h1>Patient History</h1>
        <p>Look up every blockchain-logged prediction for a given patient ID.</p>
      </div>

      <form className="search-card" onSubmit={handleSearch}>
        <input
          type="text"
          placeholder="e.g. PT-20240704"
          value={patientId}
          onChange={(e) => setPatientId(e.target.value)}
          required
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Searching…' : 'Search'}
        </button>
      </form>

      {error && <p className="history-error">{error}</p>}

      {records && records.length === 0 && (
        <p className="history-empty">No records found for this patient ID.</p>
      )}

      {records && records.length > 0 && (
        <div className="history-table-wrap">
          <table className="history-table">
            <thead>
              <tr>
                <th>Risk Level</th>
                <th>Confidence</th>
                <th>AI Advice</th>
                <th>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {records.map((r, i) => (
                <tr key={i}>
                  <td>{r.riskLevel}</td>
                  <td>{r.confidence}%</td>
                  <td className="advice-cell">{r.aiAdvice}</td>
                  <td>{new Date(r.timestamp * 1000).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
