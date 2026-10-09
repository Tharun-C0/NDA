import React from 'react';
import { formatRiskPercentage, normalizeRiskLevel } from '../utils/formatters';

/**
 * Circular Parchment Risk Index Meter with rock-solid alignment.
 */
export default function RiskMeter({ score = 0, riskStatus = 'LOW RISK' }) {
  const normalizedLevel = normalizeRiskLevel(riskStatus);
  const percentage = Math.min(100, Math.max(0, score));

  // Circle gauge math
  const size = 180;
  const strokeWidth = 12;
  const center = size / 2;
  const radius = center - strokeWidth;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  let strokeColor = '#47664E'; // Low Risk Green
  if (normalizedLevel === 'HIGH') {
    strokeColor = '#8B2626'; // High Risk Red
  } else if (normalizedLevel === 'MEDIUM') {
    strokeColor = '#A66A25'; // Medium Risk Amber
  }

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        width: '100%',
      }}
    >
      <div
        style={{
          position: 'relative',
          width: `${size}px`,
          height: `${size}px`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        {/* SVG Circle Gauge */}
        <svg
          width={size}
          height={size}
          viewBox={`0 0 ${size} ${size}`}
          style={{ transform: 'rotate(-90deg)', overflow: 'visible' }}
        >
          {/* Track Circle */}
          <circle
            cx={center}
            cy={center}
            r={radius}
            fill="none"
            stroke="var(--color-latte)"
            strokeWidth={strokeWidth}
          />
          {/* Progress Meter Arc */}
          <circle
            cx={center}
            cy={center}
            r={radius}
            fill="none"
            stroke={strokeColor}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            style={{ transition: 'stroke-dashoffset 0.8s ease-in-out' }}
          />
        </svg>

        {/* Center Text Alignment Box */}
        <div
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: `${size}px`,
            height: `${size}px`,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            textAlign: 'center',
            padding: '0.5rem',
            pointerEvents: 'none',
          }}
        >
          <span
            style={{
              fontSize: '0.7rem',
              fontWeight: 700,
              color: 'var(--color-taupe)',
              textTransform: 'uppercase',
              letterSpacing: '0.06em',
              lineHeight: 1,
              marginBottom: '0.2rem',
            }}
          >
            RISK INDEX
          </span>

          <span
            style={{
              fontSize: '1.85rem',
              fontWeight: 700,
              color: strokeColor,
              lineHeight: 1.1,
              margin: '0.1rem 0',
            }}
          >
            {formatRiskPercentage(score)}
          </span>

          <span
            style={{
              fontSize: '0.725rem',
              fontWeight: 700,
              color: 'var(--color-espresso)',
              letterSpacing: '0.04em',
              lineHeight: 1,
              marginTop: '0.2rem',
            }}
          >
            {riskStatus}
          </span>
        </div>
      </div>

      <p
        style={{
          fontSize: '0.775rem',
          color: 'var(--color-taupe)',
          marginTop: '0.85rem',
          textAlign: 'center',
          maxWidth: '220px',
          lineHeight: 1.3,
        }}
      >
        Rule-based Weighted Risk Index
      </p>
    </div>
  );
}
