import React from 'react';
import { Loader2 } from 'lucide-react';

export default function LoadingState({ title = 'Processing Document...', subtitle = 'Please wait while AI analyzes the contract.' }) {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '3rem 1.5rem',
        textAlign: 'center',
      }}
    >
      <Loader2
        size={44}
        color="var(--color-coffee)"
        style={{
          animation: 'spin 1.2s linear infinite',
          marginBottom: '1rem',
        }}
      />
      <h3 style={{ fontSize: '1.2rem', fontWeight: 600, color: 'var(--color-espresso)', marginBottom: '0.35rem' }}>
        {title}
      </h3>
      <p style={{ fontSize: '0.875rem', color: 'var(--color-taupe)', maxWidth: '400px' }}>
        {subtitle}
      </p>
      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
