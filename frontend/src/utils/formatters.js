/**
 * Format utilities for NDA Analysis.
 */

export const TAXONOMY_CATEGORIES = [
  { index: 0, roman: 'I', name: 'Party Identification' },
  { index: 1, roman: 'II', name: 'Purpose of Agreement' },
  { index: 2, roman: 'III', name: 'NDA Type' },
  { index: 3, roman: 'IV', name: 'Definition of Confidential Information' },
  { index: 4, roman: 'V', name: 'Confidentiality Obligations' },
  { index: 5, roman: 'VI', name: 'Authorized Disclosure' },
  { index: 6, roman: 'VII', name: 'Non-Confidential Information' },
  { index: 7, roman: 'VIII', name: 'Liability for Damages' },
  { index: 8, roman: 'IX', name: 'Competition Rights & Non-Solicit' },
  { index: 9, roman: 'X', name: 'Term and Termination' },
  { index: 10, roman: 'XI', name: 'Intellectual Property Rights' },
  { index: 11, roman: 'XII', name: 'Employee Obligations' },
  { index: 12, roman: 'XIII', name: 'Governing Law & Jurisdiction' },
  { index: 13, roman: 'XIV', name: 'Additional Information / Miscellaneous' },
];

/**
 * Format file size in human-readable units.
 */
export function formatBytes(bytes, decimals = 1) {
  if (!bytes || bytes === 0) return '0 Bytes';
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

/**
 * Format risk percentage score.
 */
export function formatRiskPercentage(score) {
  if (score === undefined || score === null) return '0.0%';
  return `${Number(score).toFixed(1)}%`;
}

/**
 * Map risk status string to standard Risk Level (HIGH, MEDIUM, LOW).
 */
export function normalizeRiskLevel(levelStr) {
  if (!levelStr) return 'LOW';
  const upper = levelStr.toUpperCase();
  if (upper.includes('HIGH')) return 'HIGH';
  if (upper.includes('MED') || upper.includes('MODERATE')) return 'MEDIUM';
  return 'LOW';
}

/**
 * Format ISO timestamp into readable date string.
 */
export function formatDate(isoString) {
  if (!isoString) return 'N/A';
  try {
    const d = new Date(isoString);
    return d.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch (_) {
    return isoString;
  }
}
