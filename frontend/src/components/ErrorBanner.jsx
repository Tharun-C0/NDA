import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

export default function ErrorBanner({ message, onRetry = null }) {
  if (!message) return null;

  return (
    <div
      style={{
        backgroundColor: 'var(--color-risk-high-bg)',
        color: 'var(--color-risk-high-fg)',
        border: '1px solid var(--color-risk-high-border)',
        borderRadius: 'var(--radius-sm)',
        padding: '1rem 1.25rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        margin: '1rem 0',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <AlertTriangle size={20} flexShrink={0} />
        <span style={{ fontSize: '0.9rem', fontWeight: 500 }}>{message}</span>
      </div>
      {onRetry && (
        <button
          onClick={onRetry}
          className="btn btn-secondary"
          style={{
            padding: '0.35rem 0.75rem',
            fontSize: '0.8rem',
            borderColor: 'var(--color-risk-high-border)',
            color: 'var(--color-risk-high-fg)',
          }}
        >
          <RefreshCw size={14} />
          Retry
        </button>
      )}
    </div>
  );
}
