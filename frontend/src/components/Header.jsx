import React from 'react';
import { PlusCircle, History, FileText } from 'lucide-react';
import LegalSeal from './LegalSeal';

const SCREEN_SUBTITLES = {
  upload: 'Document Ingestion',
  processing: 'Processing Pipeline',
  audit: 'Executive Risk Assessment',
  workbench: 'Interactive Legal Workbench',
  categories: 'Category Analysis',
  export: 'Executive Brief & Export',
};

export default function Header({
  activeScreen = 'upload',
  activeDocument = null,
  onNewContract = () => {},
  onOpenHistory = () => {},
}) {
  const moduleSubtitle = SCREEN_SUBTITLES[activeScreen] || 'Legal Intelligence System';

  return (
    <header
      style={{
        backgroundColor: 'var(--color-ivory)',
        borderBottom: '1px solid var(--color-border)',
        boxShadow: 'var(--shadow-sm)',
        padding: '1rem 1.25rem',
        position: 'sticky',
        top: 0,
        zIndex: 40,
      }}
    >
      <div
        style={{
          maxWidth: '1280px',
          margin: '0 auto',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '1rem',
        }}
      >
        {/* Brand & Seal Identification */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
          <LegalSeal size="md" />
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
              <h1 style={{ fontSize: '1.35rem', fontWeight: 700, margin: 0, color: 'var(--color-espresso)' }}>
                NDA Analysis
              </h1>
              <span
                style={{
                  fontSize: '0.75rem',
                  fontWeight: 700,
                  backgroundColor: 'var(--color-brass-light)',
                  color: 'var(--color-coffee)',
                  padding: '0.15rem 0.5rem',
                  borderRadius: 'var(--radius-sm)',
                  border: '1px solid var(--color-latte)',
                  textTransform: 'uppercase',
                  letterSpacing: '0.04em',
                }}
              >
                Legal Intelligence
              </span>
            </div>
            <p style={{ fontSize: '0.775rem', color: 'var(--color-taupe)', margin: 0 }}>
              AI-Powered Legal Contract Analysis & Risk Assessment
            </p>
          </div>
        </div>

        {/* Dynamic Module Subtitle & Document Metadata */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
          <div style={{ textAlign: 'right', display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
            <span
              style={{
                fontSize: '0.85rem',
                fontWeight: 600,
                color: 'var(--color-coffee)',
                letterSpacing: '0.02em',
              }}
            >
              {moduleSubtitle}
            </span>
            {activeDocument ? (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.75rem', color: 'var(--color-walnut)' }}>
                <FileText size={12} color="var(--color-brass)" />
                <span style={{ fontWeight: 500, maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {activeDocument.filename}
                </span>
                <span>•</span>
                <span style={{ color: 'var(--color-taupe)' }}>Taxonomy v3.0 · 14 Categories</span>
              </div>
            ) : (
              <span style={{ fontSize: '0.75rem', color: 'var(--color-taupe)' }}>
                Taxonomy v3.0 · 14 Categories
              </span>
            )}
          </div>

          {/* Action Buttons */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <button
              onClick={onOpenHistory}
              className="btn btn-secondary"
              title="View History Database"
              style={{ padding: '0.5rem 0.75rem', fontSize: '0.85rem' }}
            >
              <History size={16} />
              <span className="hide-mobile">History</span>
            </button>

            <button
              onClick={onNewContract}
              className="btn btn-primary"
              style={{ padding: '0.5rem 0.9rem', fontSize: '0.85rem' }}
            >
              <PlusCircle size={16} />
              <span>New Contract</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
