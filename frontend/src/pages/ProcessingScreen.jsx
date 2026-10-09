import React from 'react';
import { CheckCircle2, Loader2, AlertTriangle, ArrowRight, ShieldCheck } from 'lucide-react';

export default function ProcessingScreen({
  filename = 'Uploaded_Contract.pdf',
  selectedModel = 'legal_roberta',
  threshold = 0.60,
  currentStage = 1, // 1: Extraction, 2: Classification, 3: Risk Synthesis, 4: Done
  error = null,
  onRetry = () => {},
  onComplete = () => {},
}) {
  const stages = [
    {
      num: 'I',
      title: 'Document Extraction & Clause Segmentation',
      desc: 'Extracting raw PDF text, removing layout noise, and segmenting structural contract clauses.',
    },
    {
      num: 'II',
      title: 'Multi-Label Transformer Classification',
      desc: `Evaluating clause text against ${selectedModel} model weights at classification threshold ${threshold}.`,
    },
    {
      num: 'III',
      title: 'Risk Synthesis & Report Preparation',
      desc: 'Calculating weighted document risk index, triaging high-risk terms, and storing analysis in SQLite database.',
    },
  ];

  const getStageStatus = (stageIdx) => {
    if (error) return 'error';
    if (currentStage > stageIdx + 1) return 'completed';
    if (currentStage === stageIdx + 1) return 'active';
    return 'queued';
  };

  return (
    <div style={{ maxWidth: '800px', margin: '2rem auto', width: '100%' }}>
      <div className="parchment-card-elevated" style={{ padding: '2.5rem 2rem' }}>
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <span
            style={{
              fontSize: '0.75rem',
              fontWeight: 700,
              color: 'var(--color-coffee)',
              backgroundColor: 'var(--color-brass-light)',
              padding: '0.2rem 0.6rem',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--color-latte)',
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
            }}
          >
            Processing Pipeline
          </span>
          <h2 style={{ fontSize: '1.6rem', fontWeight: 700, color: 'var(--color-espresso)', marginTop: '0.5rem', marginBottom: '0.25rem' }}>
            Analyzing Legal Agreement
          </h2>
          <p style={{ fontSize: '0.9rem', color: 'var(--color-taupe)' }}>
            Target: <strong>{filename}</strong>
          </p>
        </div>

        {/* Error State */}
        {error ? (
          <div
            style={{
              backgroundColor: 'var(--color-risk-high-bg)',
              color: 'var(--color-risk-high-fg)',
              border: '1px solid var(--color-risk-high-border)',
              borderRadius: 'var(--radius-md)',
              padding: '1.5rem',
              marginBottom: '2rem',
              textAlign: 'center',
            }}
          >
            <AlertTriangle size={36} style={{ marginBottom: '0.5rem' }} />
            <h4 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '0.5rem' }}>Analysis Pipeline Error</h4>
            <p style={{ fontSize: '0.875rem', marginBottom: '1rem', lineHeight: 1.5 }}>{error}</p>
            <button onClick={onRetry} className="btn btn-primary">
              Retry Document Analysis
            </button>
          </div>
        ) : (
          /* Progress Stepper */
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', marginBottom: '2.5rem' }}>
            {stages.map((stage, idx) => {
              const status = getStageStatus(idx);

              let bgColor = 'var(--color-ivory)';
              let borderColor = 'var(--color-border)';
              let badgeBg = 'var(--color-parchment)';
              let badgeColor = 'var(--color-taupe)';

              if (status === 'completed') {
                bgColor = 'var(--color-paper-white)';
                borderColor = 'var(--color-risk-low-border)';
                badgeBg = 'var(--color-risk-low-bg)';
                badgeColor = 'var(--color-risk-low-fg)';
              } else if (status === 'active') {
                bgColor = 'var(--color-paper-white)';
                borderColor = 'var(--color-brass)';
                badgeBg = 'var(--color-coffee)';
                badgeColor = 'var(--color-paper-white)';
              }

              return (
                <div
                  key={idx}
                  style={{
                    backgroundColor: bgColor,
                    border: '1px solid',
                    borderColor: borderColor,
                    borderRadius: 'var(--radius-md)',
                    padding: '1.25rem',
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '1rem',
                    boxShadow: status === 'active' ? 'var(--shadow-md)' : 'none',
                    transition: 'all 0.2s ease',
                  }}
                >
                  <div
                    style={{
                      width: '40px',
                      height: '40px',
                      borderRadius: '50%',
                      backgroundColor: badgeBg,
                      color: badgeColor,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontWeight: 700,
                      fontFamily: 'serif',
                      fontSize: '1rem',
                      flexShrink: 0,
                    }}
                  >
                    {status === 'completed' ? <CheckCircle2 size={22} color="var(--color-risk-low-fg)" /> : stage.num}
                  </div>

                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <h4 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--color-espresso)' }}>
                        {stage.title}
                      </h4>
                      {status === 'active' && (
                        <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-coffee)' }}>
                          <Loader2 size={14} className="spin" />
                          IN PROGRESS
                        </span>
                      )}
                      {status === 'completed' && (
                        <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--color-risk-low-fg)' }}>
                          COMPLETE
                        </span>
                      )}
                      {status === 'queued' && (
                        <span style={{ fontSize: '0.75rem', color: 'var(--color-taupe)' }}>
                          QUEUED
                        </span>
                      )}
                    </div>
                    <p style={{ fontSize: '0.85rem', color: 'var(--color-walnut)', marginTop: '0.25rem', margin: 0 }}>
                      {stage.desc}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Completion Action */}
        {currentStage >= 4 && !error && (
          <div style={{ textAlign: 'center', paddingTop: '1rem', borderTop: '1px solid var(--color-border)' }}>
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', color: 'var(--color-risk-low-fg)', fontWeight: 600, marginBottom: '1rem' }}>
              <ShieldCheck size={22} />
              Analysis Successfully Completed & Saved to Database
            </div>
            <div>
              <button
                onClick={onComplete}
                className="btn btn-primary"
                style={{ padding: '0.85rem 2rem', fontSize: '1rem' }}
              >
                View Executive Risk Summary & Workbench
                <ArrowRight size={18} />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
