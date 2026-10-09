import React, { useState } from 'react';
import { FileCheck, Download, Printer, FileCode, ShieldAlert, CheckCircle2, AlertTriangle, FileText } from 'lucide-react';
import { downloadReportBlob } from '../services/api';
import RiskBadge from '../components/RiskBadge';
import EmptyState from '../components/EmptyState';
import ErrorBanner from '../components/ErrorBanner';
import { formatRiskPercentage } from '../utils/formatters';

export default function ExportReport({ analysisData = null }) {
  if (!analysisData) {
    return <EmptyState title="No Report Available" subtitle="Upload an NDA PDF contract to generate an executive PDF risk audit report." />;
  }

  const {
    document_id,
    filename,
    overall_risk_index,
    risk_status,
    high_risk_clause_count,
    medium_risk_clause_count,
    total_clauses,
    recommendation,
    detected_categories = [],
    clauses = [],
  } = analysisData;

  const [selectedPreset, setSelectedPreset] = useState('executive'); // 'executive', 'full', 'redline'
  const [includeWatermark, setIncludeWatermark] = useState(false);
  const [paperFormat, setPaperFormat] = useState('us_letter');
  const [isDownloadingPdf, setIsDownloadingPdf] = useState(false);
  const [pdfError, setPdfError] = useState(null);

  const handleDownloadPdf = async () => {
    setIsDownloadingPdf(true);
    setPdfError(null);
    try {
      await downloadReportBlob(document_id, `NDA_Executive_Risk_Report_${filename}`);
    } catch (err) {
      setPdfError(err.message || 'Failed to download PDF report from backend server.');
    } finally {
      setIsDownloadingPdf(false);
    }
  };

  const handleExportJson = () => {
    const jsonStr = JSON.stringify(analysisData, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const blobUrl = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = blobUrl;
    a.download = `NDA_Analysis_Metadata_${document_id}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(blobUrl);
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className={includeWatermark ? 'watermark-confidential' : ''} style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      {/* Target Document Card */}
      <div className="parchment-card-elevated">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', marginBottom: '0.35rem' }}>
              <h2 style={{ fontSize: '1.5rem', fontWeight: 700, margin: 0, color: 'var(--color-espresso)' }}>
                {filename}
              </h2>
              <RiskBadge level={risk_status} />
            </div>
            <span style={{ fontSize: '0.8rem', color: 'var(--color-taupe)' }}>
              Document ID: <code>{document_id}</code> • Risk Index: <strong>{formatRiskPercentage(overall_risk_index)}</strong>
            </span>
          </div>

          <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
            <button
              onClick={handleDownloadPdf}
              disabled={isDownloadingPdf}
              className="btn btn-primary"
            >
              <Download size={18} />
              {isDownloadingPdf ? 'Generating PDF...' : 'Download Executive PDF'}
            </button>

            <button onClick={handleExportJson} className="btn btn-secondary">
              <FileCode size={18} />
              Export JSON Metadata
            </button>

            <button onClick={handlePrint} className="btn btn-secondary">
              <Printer size={18} />
              Print Report
            </button>
          </div>
        </div>
      </div>

      <ErrorBanner message={pdfError} />

      {/* Report Presets Grid */}
      <div className="parchment-card">
        <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--color-espresso)', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <FileText size={20} color="var(--color-coffee)" />
          Select Report Compilation Format
        </h3>

        <div className="grid-3">
          {/* Executive Brief */}
          <div
            onClick={() => setSelectedPreset('executive')}
            style={{
              padding: '1.25rem',
              borderRadius: 'var(--radius-md)',
              border: '2px solid',
              borderColor: selectedPreset === 'executive' ? 'var(--color-coffee)' : 'var(--color-border)',
              backgroundColor: selectedPreset === 'executive' ? 'var(--color-paper-white)' : 'var(--color-ivory)',
              cursor: 'pointer',
              transition: 'all 0.15s ease',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
              <h4 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--color-espresso)', margin: 0 }}>
                Executive Brief
              </h4>
              <span className="category-badge">PyMuPDF Standard</span>
            </div>
            <p style={{ fontSize: '0.825rem', color: 'var(--color-taupe)', lineHeight: 1.4 }}>
              High-level risk index summary, document metadata profile, and triaged high-risk category breakdown.
            </p>
          </div>

          {/* Full Legal Audit */}
          <div
            onClick={() => setSelectedPreset('full')}
            style={{
              padding: '1.25rem',
              borderRadius: 'var(--radius-md)',
              border: '2px solid',
              borderColor: selectedPreset === 'full' ? 'var(--color-coffee)' : 'var(--color-border)',
              backgroundColor: selectedPreset === 'full' ? 'var(--color-paper-white)' : 'var(--color-ivory)',
              cursor: 'pointer',
              transition: 'all 0.15s ease',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
              <h4 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--color-espresso)', margin: 0 }}>
                Full Legal Audit
              </h4>
              <span style={{ fontSize: '0.7rem', color: 'var(--color-taupe)' }}>Detailed</span>
            </div>
            <p style={{ fontSize: '0.825rem', color: 'var(--color-taupe)', lineHeight: 1.4 }}>
              Comprehensive clause-by-clause classification analysis across all 14 taxonomy categories.
            </p>
          </div>

          {/* Redline Summary */}
          <div
            onClick={() => setSelectedPreset('redline')}
            style={{
              padding: '1.25rem',
              borderRadius: 'var(--radius-md)',
              border: '2px solid',
              borderColor: selectedPreset === 'redline' ? 'var(--color-coffee)' : 'var(--color-border)',
              backgroundColor: selectedPreset === 'redline' ? 'var(--color-paper-white)' : 'var(--color-ivory)',
              cursor: 'pointer',
              transition: 'all 0.15s ease',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
              <h4 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--color-espresso)', margin: 0 }}>
                Redline Summary
              </h4>
              <span style={{ fontSize: '0.7rem', color: 'var(--color-taupe)' }}>Draft Proposal</span>
            </div>
            <p style={{ fontSize: '0.825rem', color: 'var(--color-taupe)', lineHeight: 1.4 }}>
              Focused summary of flagged high-risk terms and suggested counter-clause proposals.
            </p>
          </div>
        </div>
      </div>

      {/* Report Formatting Controls */}
      <div className="parchment-card">
        <h3 style={{ fontSize: '1.05rem', fontWeight: 600, color: 'var(--color-espresso)', marginBottom: '1rem' }}>
          Document Export Options & Watermarks
        </h3>

        <div className="grid-2">
          {/* Watermark Toggle */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.75rem 1rem', background: 'var(--color-paper-white)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-sm)' }}>
            <input
              type="checkbox"
              id="watermark-toggle"
              checked={includeWatermark}
              onChange={(e) => setIncludeWatermark(e.target.checked)}
              style={{ width: '18px', height: '18px', accentColor: 'var(--color-coffee)', cursor: 'pointer' }}
            />
            <div>
              <label htmlFor="watermark-toggle" style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--color-espresso)', cursor: 'pointer' }}>
                Include Confidential Watermark Label
              </label>
              <p style={{ fontSize: '0.775rem', color: 'var(--color-taupe)', margin: 0 }}>
                Applies optional "ATTORNEY-CLIENT PRIVILEGED & CONFIDENTIAL" watermark to print output.
              </p>
            </div>
          </div>

          {/* Paper Format Selector */}
          <div className="form-group">
            <label className="form-label">Paper Target Layout Format</label>
            <select
              value={paperFormat}
              onChange={(e) => setPaperFormat(e.target.value)}
              className="form-select"
            >
              <option value="us_letter">US Letter (8.5 × 11 in)</option>
              <option value="a4">ISO A4 (210 × 297 mm)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Executive Brief Preview Box */}
      <div className="double-border-box">
        <div className="double-border-inner">
          <div style={{ textAlign: 'center', borderBottom: '1px solid var(--color-border)', paddingBottom: '1rem', marginBottom: '1rem' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--color-coffee)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              EXECUTIVE BRIEF SUMMARY AUDIT
            </span>
            <h3 style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--color-espresso)', marginTop: '0.25rem' }}>
              {filename}
            </h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--color-taupe)', margin: 0 }}>
              Risk Index: {formatRiskPercentage(overall_risk_index)} • {risk_status}
            </p>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.9rem', lineHeight: 1.6 }}>
            <div>
              <strong>Key Finding & Recommendation:</strong>
              <p style={{ color: 'var(--color-walnut)' }}>{recommendation}</p>
            </div>

            <div>
              <strong>Taxonomy Categories Flagged ({detected_categories.length}):</strong>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem', marginTop: '0.35rem' }}>
                {detected_categories.map((cat, i) => (
                  <span key={i} className="category-badge">{cat}</span>
                ))}
              </div>
            </div>

            <div>
              <strong>Clause Risk Distribution:</strong>
              <p style={{ color: 'var(--color-walnut)' }}>
                Out of {total_clauses} total clauses analyzed, {high_risk_clause_count} high-risk and {medium_risk_clause_count} medium-risk clauses were flagged for attorney review.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Mandatory Legal Disclaimer */}
      <div
        style={{
          backgroundColor: 'var(--color-brass-light)',
          border: '1px solid var(--color-latte)',
          borderRadius: 'var(--radius-md)',
          padding: '1.25rem',
          display: 'flex',
          gap: '1rem',
          alignItems: 'flex-start',
        }}
      >
        <AlertTriangle size={22} color="var(--color-coffee)" flexShrink={0} style={{ marginTop: '0.15rem' }} />
        <div>
          <h4 style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--color-coffee)', marginBottom: '0.25rem' }}>
            Legal Disclaimer & Notice
          </h4>
          <p style={{ fontSize: '0.825rem', color: 'var(--color-walnut)', lineHeight: 1.5, margin: 0 }}>
            NDA Analysis provides automated contract analysis and risk indicators for informational purposes only. Results are not legal advice and do not determine enforceability or whether a contract is safe to sign. Consult qualified legal counsel before making legal decisions.
          </p>
        </div>
      </div>
    </div>
  );
}
