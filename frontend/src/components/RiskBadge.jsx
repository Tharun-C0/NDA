import React from 'react';
import { AlertTriangle, AlertCircle, CheckCircle2 } from 'lucide-react';
import { normalizeRiskLevel } from '../utils/formatters';

/**
 * Reusable Risk Badge Component.
 */
export default function RiskBadge({ level = 'LOW', label = null }) {
  const normalized = normalizeRiskLevel(level);
  const displayLabel = label || `${normalized} RISK`;

  let badgeClass = 'risk-badge-low';
  let Icon = CheckCircle2;

  if (normalized === 'HIGH') {
    badgeClass = 'risk-badge-high';
    Icon = AlertTriangle;
  } else if (normalized === 'MEDIUM') {
    badgeClass = 'risk-badge-medium';
    Icon = AlertCircle;
  }

  return (
    <span className={`risk-badge ${badgeClass}`}>
      <Icon size={13} strokeWidth={2.5} />
      {displayLabel}
    </span>
  );
}
