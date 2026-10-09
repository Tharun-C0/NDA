import React from 'react';
import RiskBadge from './RiskBadge';

export default function ClauseCard({
  clause,
  isSelected = false,
  onClick = () => {},
}) {
  if (!clause) return null;

  return (
    <div
      onClick={onClick}
      style={{
        backgroundColor: isSelected ? 'var(--color-paper-white)' : 'var(--color-ivory)',
        border: '1px solid',
        borderColor: isSelected ? 'var(--color-brass)' : 'var(--color-border)',
        borderLeft: isSelected ? '4px solid var(--color-coffee)' : '1px solid var(--color-border)',
        borderRadius: 'var(--radius-sm)',
        padding: '1rem',
        cursor: 'pointer',
        transition: 'all 0.15s ease',
        boxShadow: isSelected ? 'var(--shadow-md)' : 'var(--shadow-sm)',
        marginBottom: '0.75rem',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span style={{ fontSize: '0.825rem', fontWeight: 700, color: 'var(--color-coffee)', letterSpacing: '0.02em' }}>
            {clause.clause_id}
          </span>
          {clause.segment_type && (
            <span style={{ fontSize: '0.7rem', color: 'var(--color-taupe)', background: 'var(--color-parchment)', padding: '0.1rem 0.4rem', borderRadius: '3px' }}>
              {clause.segment_type}
            </span>
          )}
        </div>
        <RiskBadge level={clause.risk_level} />
      </div>

      <p
        style={{
          fontSize: '0.875rem',
          color: 'var(--color-espresso)',
          lineHeight: 1.5,
          margin: '0.5rem 0',
          display: '-webkit-box',
          WebkitLineClamp: 3,
          WebkitBoxOrient: 'vertical',
          overflow: 'hidden',
          fontFamily: 'serif',
        }}
      >
        "{clause.text}"
      </p>

      {/* Category Pills */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem', marginTop: '0.5rem' }}>
        {clause.predicted_categories && clause.predicted_categories.length > 0 ? (
          clause.predicted_categories.map((cat, idx) => (
            <span key={idx} className="category-badge">
              {cat.category} ({(cat.confidence * 100).toFixed(0)}%)
            </span>
          ))
        ) : (
          <span style={{ fontSize: '0.75rem', color: 'var(--color-taupe)', italic: 'true' }}>
            No category flagged
          </span>
        )}
      </div>
    </div>
  );
}
