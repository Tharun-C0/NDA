import React, { useEffect, useState } from 'react';
import { X, Clock, FileText, ChevronRight, RefreshCw, AlertCircle } from 'lucide-react';
import { getDocuments } from '../services/api';
import { formatDate, formatRiskPercentage } from '../utils/formatters';
import RiskBadge from './RiskBadge';

export default function DocumentHistoryModal({ isOpen, onClose, onSelectDocument }) {
  const [historyItems, setHistoryItems] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchHistory = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getDocuments(0, 50);
      setHistoryItems(data.items || []);
      setTotalCount(data.total_count || 0);
    } catch (err) {
      setError(err.message || 'Failed to load document history database.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchHistory();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div
      style={{
        position: 'fixed',
        top: 0, left: 0, right: 0, bottom: 0,
        backgroundColor: 'rgba(48, 37, 31, 0.5)',
        backdropFilter: 'blur(3px)',
        zIndex: 100,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '1rem',
      }}
    >
      <div
        className="parchment-card-elevated"
        style={{
          maxWidth: '750px',
          width: '100%',
          maxHeight: '85vh',
          display: 'flex',
          flexDirection: 'column',
          padding: 0,
          overflow: 'hidden',
        }}
      >
        {/* Header */}
        <div
          style={{
            padding: '1.25rem 1.5rem',
            borderBottom: '1px solid var(--color-border)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            backgroundColor: 'var(--color-ivory)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Clock size={20} color="var(--color-coffee)" />
            <h2 style={{ fontSize: '1.2rem', fontWeight: 700, margin: 0 }}>
              Analysis History Database ({totalCount})
            </h2>
          </div>
          <button
            onClick={onClose}
            className="btn btn-secondary"
            style={{ padding: '0.35rem 0.5rem', border: 'none' }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Body List */}
        <div style={{ padding: '1.5rem', overflowY: 'auto', flex: 1, backgroundColor: 'var(--color-paper-white)' }}>
          {isLoading ? (
            <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--color-taupe)' }}>
              <RefreshCw className="spin" size={24} style={{ marginBottom: '0.5rem' }} />
              <p>Fetching database history...</p>
            </div>
          ) : error ? (
            <div style={{ padding: '1rem', background: 'var(--color-risk-high-bg)', color: 'var(--color-risk-high-fg)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--color-risk-high-border)' }}>
              <AlertCircle size={18} style={{ marginRight: '0.5rem' }} />
              {error}
            </div>
          ) : historyItems.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '2.5rem', color: 'var(--color-taupe)' }}>
              <FileText size={36} color="var(--color-latte)" style={{ marginBottom: '0.5rem' }} />
              <p style={{ fontWeight: 500 }}>No document analyses recorded yet.</p>
              <p style={{ fontSize: '0.8rem' }}>Upload an NDA PDF to perform your first analysis.</p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {historyItems.map((item) => (
                <div
                  key={item.document_id}
                  onClick={() => {
                    onSelectDocument(item.document_id);
                    onClose();
                  }}
                  style={{
                    padding: '1rem',
                    backgroundColor: 'var(--color-ivory)',
                    border: '1px solid var(--color-border)',
                    borderRadius: 'var(--radius-md)',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    transition: 'all 0.15s ease',
                  }}
                  className="history-row"
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
                    <div
                      style={{
                        padding: '0.65rem',
                        backgroundColor: 'var(--color-brass-light)',
                        borderRadius: 'var(--radius-sm)',
                        color: 'var(--color-coffee)',
                      }}
                    >
                      <FileText size={20} />
                    </div>
                    <div>
                      <h4 style={{ fontSize: '0.95rem', fontWeight: 600, margin: 0, color: 'var(--color-espresso)' }}>
                        {item.filename}
                      </h4>
                      <div style={{ display: 'flex', gap: '0.75rem', fontSize: '0.775rem', color: 'var(--color-taupe)', marginTop: '0.2rem' }}>
                        <span>{formatDate(item.upload_timestamp)}</span>
                        <span>•</span>
                        <span>{item.model_choice}</span>
                        <span>•</span>
                        <span>{item.total_clauses} clauses</span>
                      </div>
                    </div>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <div style={{ textAlign: 'right' }}>
                      <RiskBadge level={item.risk_status} />
                      <div style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--color-espresso)', marginTop: '0.2rem' }}>
                        {formatRiskPercentage(item.overall_risk_index)}
                      </div>
                    </div>
                    <ChevronRight size={18} color="var(--color-taupe)" />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
