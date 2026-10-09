import React from 'react';
import { Scale, ArrowRight, ShieldAlert, FileText, Layers, Tag, CheckCircle2, ChevronRight } from 'lucide-react';
import RiskMeter from '../components/RiskMeter';
import RiskBadge from '../components/RiskBadge';
import EmptyState from '../components/EmptyState';

export default function ContractAudit({
  analysisData = null,
  onNavigateWorkbench = () => {},
  onSelectCategory = () => {},
}) {
  if (!analysisData) {
    return <EmptyState title="No Active Contract Analysis" />;
  }

  const {
    filename,
    page_count,
    character_count,
    word_count,
    total_clauses,
    high_risk_clause_count,
    medium_risk_clause_count,
    overall_risk_index,
    risk_status,
    recommendation,
    advice,
    detected_categories = [],
    clauses = [],
  } = analysisData;

  const lowRiskClauseCount = Math.max(0, total_clauses - (high_risk_clause_count + medium_risk_clause_count));

  // Priority categories list
  const PRIORITY_CATS = [
    'Liability for Damages',
    'Competition Rights & Non-Solicit',
    'Intellectual Property Rights',
    'Term and Termination',
    'Governing Law & Jurisdiction',
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      {/* Executive Heading */}
      <div
        className="parchment-card-elevated"
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '1.25rem',
        }}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', marginBottom: '0.35rem' }}>
            <h1 style={{ fontSize: '1.75rem', fontWeight: 700, margin: 0, color: 'var(--color-espresso)' }}>
              {filename}
            </h1>
            <RiskBadge level={risk_status} />
          </div>
          <p style={{ fontSize: '0.925rem', color: 'var(--color-walnut)', margin: 0, maxWidth: '750px' }}>
            {recommendation || 'Executive legal analysis generated from fine-tuned multi-label neural classifiers.'}
          </p>
        </div>

        <button onClick={onNavigateWorkbench} className="btn btn-primary">
          <FileText size={18} />
          Inspect Legal Workbench
          <ArrowRight size={16} />
        </button>
      </div>

      {/* Main Grid: Risk Meter + Metrics */}
      <div className="grid-3">
        {/* Risk Index Dial Card */}
        <div className="parchment-card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 600, color: 'var(--color-espresso)', marginBottom: '1rem', width: '100%', textAlign: 'center' }}>
            Document Risk Index
          </h3>
          <RiskMeter score={overall_risk_index} riskStatus={risk_status} />
        </div>

        {/* Risk Breakdown Cards */}
        <div className="parchment-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 600, color: 'var(--color-espresso)', marginBottom: '1rem' }}>
            Clause Risk Triage Breakdown
          </h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', flex: 1, justifyContent: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.75rem 1rem', background: 'var(--color-risk-high-bg)', border: '1px solid var(--color-risk-high-border)', borderRadius: 'var(--radius-sm)' }}>
              <span style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--color-risk-high-fg)' }}>High Risk Clauses</span>
              <span style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--color-risk-high-fg)' }}>{high_risk_clause_count}</span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.75rem 1rem', background: 'var(--color-risk-med-bg)', border: '1px solid var(--color-risk-med-border)', borderRadius: 'var(--radius-sm)' }}>
              <span style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--color-risk-med-fg)' }}>Medium Risk Clauses</span>
              <span style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--color-risk-med-fg)' }}>{medium_risk_clause_count}</span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.75rem 1rem', background: 'var(--color-risk-low-bg)', border: '1px solid var(--color-risk-low-border)', borderRadius: 'var(--radius-sm)' }}>
              <span style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--color-risk-low-fg)' }}>Low Risk Clauses</span>
              <span style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--color-risk-low-fg)' }}>{lowRiskClauseCount}</span>
            </div>
          </div>
        </div>

        {/* Contract Metadata Card */}
        <div className="parchment-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 600, color: 'var(--color-espresso)', marginBottom: '1rem' }}>
            Document Structural Profile
          </h3>

          <div className="grid-2" style={{ gap: '0.75rem' }}>
            <div style={{ padding: '0.75rem', background: 'var(--color-paper-white)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-sm)' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--color-taupe)', textTransform: 'uppercase' }}>Page Count</span>
              <div style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--color-espresso)' }}>{page_count || 1}</div>
            </div>

            <div style={{ padding: '0.75rem', background: 'var(--color-paper-white)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-sm)' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--color-taupe)', textTransform: 'uppercase' }}>Total Clauses</span>
              <div style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--color-espresso)' }}>{total_clauses}</div>
            </div>

            <div style={{ padding: '0.75rem', background: 'var(--color-paper-white)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-sm)' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--color-taupe)', textTransform: 'uppercase' }}>Character Count</span>
              <div style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--color-espresso)' }}>{character_count?.toLocaleString() || 'N/A'}</div>
            </div>

            <div style={{ padding: '0.75rem', background: 'var(--color-paper-white)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-sm)' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--color-taupe)', textTransform: 'uppercase' }}>Word Count</span>
              <div style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--color-espresso)' }}>{word_count?.toLocaleString() || 'N/A'}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Priority Categories Section */}
      <div className="parchment-card">
        <h3 style={{ fontSize: '1.15rem', fontWeight: 600, color: 'var(--color-espresso)', marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Tag size={20} color="var(--color-coffee)" />
          Priority Legal Category Assessment
        </h3>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {PRIORITY_CATS.map((catName) => {
            // Find matching clauses in document
            const matching = clauses.filter((c) =>
              c.predicted_categories?.some((p) => p.category.toLowerCase().trim() === catName.toLowerCase().trim())
            );

            const isPresent = matching.length > 0;
            const highestConf = isPresent
              ? Math.max(
                  ...matching.map((c) => {
                    const p = c.predicted_categories.find((x) => x.category.toLowerCase().trim() === catName.toLowerCase().trim());
                    return p ? p.confidence : 0;
                  })
                )
              : 0;

            return (
              <div
                key={catName}
                style={{
                  padding: '1rem 1.25rem',
                  backgroundColor: 'var(--color-paper-white)',
                  border: '1px solid var(--color-border)',
                  borderRadius: 'var(--radius-sm)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  flexWrap: 'wrap',
                  gap: '0.75rem',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
                  <div style={{ color: isPresent ? 'var(--color-coffee)' : 'var(--color-taupe)' }}>
                    {isPresent ? <ShieldAlert size={20} /> : <CheckCircle2 size={20} />}
                  </div>
                  <div>
                    <h4 style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--color-espresso)', margin: 0 }}>
                      {catName}
                    </h4>
                    <span style={{ fontSize: '0.775rem', color: 'var(--color-taupe)' }}>
                      {isPresent
                        ? `${matching.length} clause${matching.length > 1 ? 's' : ''} flagged • Peak confidence: ${(highestConf * 100).toFixed(0)}%`
                        : 'Not flagged at current classification threshold'}
                    </span>
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                  {isPresent ? (
                    <span className="risk-badge risk-badge-medium">
                      DETECTED
                    </span>
                  ) : (
                    <span style={{ fontSize: '0.75rem', color: 'var(--color-taupe)' }}>
                      ABSENT
                    </span>
                  )}

                  <button
                    onClick={() => onSelectCategory(catName)}
                    className="btn btn-secondary"
                    style={{ padding: '0.35rem 0.65rem', fontSize: '0.8rem' }}
                  >
                    Inspect Category
                    <ChevronRight size={14} />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
