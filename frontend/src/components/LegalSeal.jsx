import React from 'react';

/**
 * Circular LX Legal Seal Monogram Motif.
 */
export default function LegalSeal({ size = 'md', className = '' }) {
  const sizeClass = size === 'lg' ? 'legal-seal-lg' : '';
  return (
    <div className={`legal-seal ${sizeClass} ${className}`} title="NDA Analysis Legal Seal">
      LX
    </div>
  );
}
