import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Copy, Check, ShieldAlert, CheckCircle2 } from 'lucide-react';
import RiskBadge from './RiskBadge';

export default function CategoryAccordion({ categoryInfo, matchingClauses = [] }) {
  const [isOpen, setIsOpen] = useState(false);
  const [copiedId, setCopiedId] = useState(null);

  const isDetected = matchingClauses.length > 0;

  const handleCopy = (text, id) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div
      style={{
        backgroundColor: 'var(--color-ivory)',
        border: '1px solid var(--color-border)',
        borderRadius: 'var(--radius-md)',
        marginBottom: '0.75rem',
        overflow: 'hidden',
        boxShadow: 'var(--shadow-sm)',
      }}
    >
      {/* Header Bar */}
      <div
        onClick={() => setIsOpen(!isOpen)}
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '1rem 1.25rem',
          cursor: 'pointer',
          backgroundColor: isDetected ? 'var(--color-ivory)' : 'var(--color-parchment)',
          transition: 'background-color 0.2s ease',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
          <span
            style={{
              fontFamily: 'serif',
              fontWeight: 700,
              fontSize: '1rem',
              color: 'var(--color-coffee)',
              minWidth: '2.5rem',
            }}
          >
            {categoryInfo.roman}.
          </span>
          <div>
            <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--color-espresso)' }}>
              {categoryInfo.name}
            </h3>
            <span style={{ fontSize: '0.775rem', color: 'var(--color-taupe)' }}>
              {isDetected
                ? `${matchingClauses.length} clause${matchingClauses.length > 1 ? 's' : ''} detected in document`
                : 'Not detected by model'}
            </span>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          {isDetected ? (
            <span
              style={{
                fontSize: '0.75rem',
                fontWeight: 700,
                color: 'var(--color-coffee)',
                backgroundColor: 'var(--color-brass-light)',
                border: '1px solid var(--color-latte)',
                padding: '0.2rem 0.55rem',
                borderRadius: '9999px',
              }}
            >
              DETECTED ({matchingClauses.length})
            </span>
          ) : (
            <span
              style={{
                fontSize: '0.75rem',
                color: 'var(--color-taupe)',
                backgroundColor: 'var(--color-paper-white)',
                border: '1px solid var(--color-border)',
                padding: '0.2rem 0.55rem',
                borderRadius: '9999px',
              }}
            >
              NOT DETECTED
            </span>
          )}

          {isOpen ? <ChevronUp size={18} color="var(--color-coffee)" /> : <ChevronDown size={18} color="var(--color-taupe)" />}
        </div>
      </div>

      {/* Accordion Body */}
      {isOpen && (
        <div
          style={{
            padding: '1.25rem',
            borderTop: '1px solid var(--color-border)',
            backgroundColor: 'var(--color-paper-white)',
          }}
        >
          {isDetected ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {matchingClauses.map((clauseItem) => {
                const catPred = clauseItem.predicted_categories.find(
                  (p) => p.category.toLowerCase().trim() === categoryInfo.name.toLowerCase().trim()
                );
                const confidence = catPred ? (catPred.confidence * 100).toFixed(1) : null;

                return (
                  <div
                    key={clauseItem.clause_id}
                    style={{
                      border: '1px solid var(--color-latte)',
                      borderRadius: 'var(--radius-sm)',
                      padding: '1rem',
                      backgroundColor: 'var(--color-ivory)',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span style={{ fontWeight: 700, fontSize: '0.85rem', color: 'var(--color-coffee)' }}>
                          {clauseItem.clause_id}
                        </span>
                        {confidence && (
                          <span style={{ fontSize: '0.75rem', color: 'var(--color-taupe)' }}>
                            Model Sigmoid Confidence: <strong>{confidence}%</strong>
                          </span>
                        )}
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <RiskBadge level={clauseItem.risk_level} />
                        <button
                          onClick={() => handleCopy(clauseItem.text, clauseItem.clause_id)}
                          className="btn btn-secondary"
                          style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}
                          title="Copy Clause Text"
                        >
                          {copiedId === clauseItem.clause_id ? <Check size={12} color="green" /> : <Copy size={12} />}
                          {copiedId === clauseItem.clause_id ? 'Copied' : 'Copy'}
                        </button>
                      </div>
                    </div>

                    <p style={{ fontFamily: 'serif', fontSize: '0.9rem', color: 'var(--color-espresso)', lineHeight: 1.6, margin: '0.5rem 0' }}>
                      "{clauseItem.text}"
                    </p>
                  </div>
                );
              })}
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '1rem', color: 'var(--color-taupe)', fontSize: '0.85rem' }}>
              <CheckCircle2 size={24} color="var(--color-taupe)" style={{ marginBottom: '0.35rem' }} />
              <p>No clauses in this document were classified under <strong>{categoryInfo.name}</strong> at threshold 0.60.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
