import React from 'react';
import { FileSearch, UploadCloud } from 'lucide-react';

export default function EmptyState({
  title = 'No Document Analyzed Yet',
  subtitle = 'Please deposit an NDA PDF contract on the Upload screen to generate AI risk assessment and clause classification.',
  onAction = null,
  actionLabel = 'Deposit Contract',
}) {
  return (
    <div
      className="parchment-card"
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '4rem 2rem',
        textAlign: 'center',
        margin: '2rem 0',
      }}
    >
      <div
        style={{
          width: '64px',
          height: '64px',
          borderRadius: '50%',
          backgroundColor: 'var(--color-brass-light)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          marginBottom: '1rem',
          color: 'var(--color-coffee)',
        }}
      >
        <FileSearch size={32} />
      </div>
      <h3 style={{ fontSize: '1.25rem', fontWeight: 600, color: 'var(--color-espresso)', marginBottom: '0.5rem' }}>
        {title}
      </h3>
      <p style={{ fontSize: '0.9rem', color: 'var(--color-taupe)', maxWidth: '450px', marginBottom: '1.5rem' }}>
        {subtitle}
      </p>
      {onAction && (
        <button onClick={onAction} className="btn btn-primary">
          <UploadCloud size={18} />
          {actionLabel}
        </button>
      )}
    </div>
  );
}
