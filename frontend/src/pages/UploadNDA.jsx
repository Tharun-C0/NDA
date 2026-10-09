import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, CheckCircle2, ShieldAlert, Cpu, Scale, AlertCircle } from 'lucide-react';
import LegalSeal from '../components/LegalSeal';
import ErrorBanner from '../components/ErrorBanner';
import { formatBytes } from '../utils/formatters';

export default function UploadNDA({
  onStartAnalysis = () => {},
  selectedModel = 'legal_roberta',
  setSelectedModel = () => {},
  threshold = 0.60,
  setThreshold = () => {},
}) {
  const [stagedFile, setStagedFile] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);
  const fileInputRef = useRef(null);

  const validateAndStageFile = (file) => {
    setErrorMessage(null);
    if (!file) return;

    if (file.type !== 'application/pdf' && !file.name.toLowerCase().endsWith('.pdf')) {
      setErrorMessage('Invalid file format. Please upload an official NDA PDF document.');
      return;
    }

    if (file.size > 20 * 1024 * 1024) { // 20 MB limit
      setErrorMessage('File size exceeds the 20 MB maximum limit.');
      return;
    }

    setStagedFile(file);
  };

  const handleFileDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndStageFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      validateAndStageFile(e.target.files[0]);
    }
  };

  const handleLoadSample = async () => {
    setErrorMessage(null);
    try {
      // Fetch local sample PDF file 25f2299_1.pdf from root
      const response = await fetch('/25f2299_1.pdf');
      if (!response.ok) {
        throw new Error('Sample NDA document 25f2299_1.pdf is not accessible on dev server.');
      }
      const blob = await response.blob();
      const sampleFile = new File([blob], '25f2299_1_Commercial_NDA_Sample.pdf', { type: 'application/pdf' });
      setStagedFile(sampleFile);
    } catch (err) {
      setErrorMessage('Could not load sample NDA PDF: ' + err.message);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Hero Header */}
      <div style={{ textAlign: 'center', maxWidth: '750px', margin: '0 auto' }}>
        <h1 style={{ fontSize: '2.1rem', fontWeight: 700, color: 'var(--color-espresso)', marginBottom: '0.5rem' }}>
          Deposit Non-Disclosure Agreement
        </h1>
        <p style={{ fontSize: '1rem', color: 'var(--color-walnut)', lineHeight: 1.6 }}>
          Upload a contract to extract clauses, identify legal categories across 14 NDA taxonomy topics, and assess potential contractual risks.
        </p>
      </div>

      <ErrorBanner message={errorMessage} />

      {/* Model & Threshold Configuration Card */}
      <div className="parchment-card" style={{ maxWidth: '850px', margin: '0 auto', width: '100%' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem', borderBottom: '1px solid var(--color-border)', paddingBottom: '0.75rem' }}>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 600, color: 'var(--color-espresso)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Cpu size={18} color="var(--color-coffee)" />
            Classifier Configuration
          </h3>
          <span style={{ fontSize: '0.75rem', color: 'var(--color-taupe)' }}>Phase 3 Verified Weights</span>
        </div>

        <div className="grid-2">
          {/* Model selection */}
          <div className="form-group">
            <label className="form-label">Transformer Model Architecture</label>
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              className="form-select"
            >
              <option value="legal_roberta">Legal-RoBERTa (Recommended · F1: 89.4%)</option>
              <option value="legal_bert">Legal-BERT (F1: 87.2%)</option>
              <option value="deberta_v3">DeBERTa-v3 (F1: 88.6%)</option>
            </select>
          </div>

          {/* Decision threshold */}
          <div className="form-group">
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <label className="form-label">Sigmoid Probability Threshold</label>
              <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--color-coffee)' }}>
                {Number(threshold).toFixed(2)}
              </span>
            </div>
            <input
              type="range"
              min="0.10"
              max="0.90"
              step="0.05"
              value={threshold}
              onChange={(e) => setThreshold(parseFloat(e.target.value))}
              style={{ accentColor: 'var(--color-coffee)', cursor: 'pointer', marginTop: '0.4rem' }}
            />
          </div>
        </div>
      </div>

      {/* Deposit Dropzone Card */}
      <div style={{ maxWidth: '850px', margin: '0 auto', width: '100%' }}>
        <div className="double-border-box">
          <div
            className="double-border-inner"
            onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
            onDragLeave={() => setIsDragOver(false)}
            onDrop={handleFileDrop}
            style={{
              backgroundColor: isDragOver ? 'var(--color-brass-light)' : 'var(--color-ivory)',
              textAlign: 'center',
              padding: '3rem 2rem',
              transition: 'all 0.2s ease',
            }}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,application/pdf"
              onChange={handleFileChange}
              style={{ display: 'none' }}
              id="nda-file-input"
            />

            <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '1.25rem' }}>
              <LegalSeal size="lg" />
            </div>

            <h3 style={{ fontSize: '1.25rem', fontWeight: 600, color: 'var(--color-espresso)', marginBottom: '0.5rem' }}>
              Drag & Drop PDF Agreement Here
            </h3>
            <p style={{ fontSize: '0.875rem', color: 'var(--color-taupe)', marginBottom: '1.5rem' }}>
              Supported format: PDF contracts up to 20 MB
            </p>

            <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
              <button
                onClick={() => fileInputRef.current?.click()}
                className="btn btn-primary"
              >
                <UploadCloud size={18} />
                Browse Local PDF File
              </button>

              <button
                onClick={handleLoadSample}
                className="btn btn-secondary"
                title="Load sample commercial NDA document"
              >
                <FileText size={18} />
                Load Sample Commercial NDA
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Staged File Panel */}
      {stagedFile && (
        <div
          className="parchment-card-elevated"
          style={{
            maxWidth: '850px',
            margin: '0 auto',
            width: '100%',
            borderColor: 'var(--color-brass)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <div
                style={{
                  width: '48px',
                  height: '48px',
                  borderRadius: 'var(--radius-sm)',
                  backgroundColor: 'var(--color-brass-light)',
                  color: 'var(--color-coffee)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <FileText size={28} />
              </div>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <h4 style={{ fontSize: '1.05rem', fontWeight: 600, margin: 0, color: 'var(--color-espresso)' }}>
                    {stagedFile.name}
                  </h4>
                  <span
                    style={{
                      fontSize: '0.7rem',
                      fontWeight: 700,
                      backgroundColor: 'var(--color-risk-low-bg)',
                      color: 'var(--color-risk-low-fg)',
                      border: '1px solid var(--color-risk-low-border)',
                      padding: '0.15rem 0.45rem',
                      borderRadius: '9999px',
                    }}
                  >
                    STAGED FOR ANALYSIS
                  </span>
                </div>
                <span style={{ fontSize: '0.8rem', color: 'var(--color-taupe)' }}>
                  Size: {formatBytes(stagedFile.size)} • Model: {selectedModel} (Threshold: {threshold})
                </span>
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <button
                onClick={() => setStagedFile(null)}
                className="btn btn-secondary"
                style={{ fontSize: '0.85rem' }}
              >
                Choose Different File
              </button>
              <button
                onClick={() => onStartAnalysis(stagedFile)}
                className="btn btn-primary"
                style={{ padding: '0.75rem 1.5rem', fontSize: '0.95rem' }}
              >
                <Scale size={18} />
                Begin Risk Assessment
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Process Overview Cards */}
      <div style={{ maxWidth: '1100px', margin: '1rem auto 0 auto', width: '100%' }}>
        <h3 style={{ fontSize: '1.1rem', fontWeight: 600, textAlign: 'center', marginBottom: '1.25rem', color: 'var(--color-walnut)' }}>
          Legal Intelligence Processing Architecture
        </h3>
        <div className="grid-3">
          <div className="parchment-card">
            <div style={{ color: 'var(--color-coffee)', marginBottom: '0.75rem' }}>
              <FileText size={28} />
            </div>
            <h4 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.35rem' }}>
              1. Clause Segmentation & Parsing
            </h4>
            <p style={{ fontSize: '0.85rem', color: 'var(--color-taupe)', lineHeight: 1.5 }}>
              Extracts raw text from PDF documents and segments contract paragraphs into discrete, indexed legal clauses.
            </p>
          </div>

          <div className="parchment-card">
            <div style={{ color: 'var(--color-brass)', marginBottom: '0.75rem' }}>
              <Cpu size={28} />
            </div>
            <h4 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.35rem' }}>
              2. Multi-Label Transformer Classification
            </h4>
            <p style={{ fontSize: '0.85rem', color: 'var(--color-taupe)', lineHeight: 1.5 }}>
              Applies fine-tuned Legal-RoBERTa neural models to map clauses across 14 NDA taxonomy categories.
            </p>
          </div>

          <div className="parchment-card">
            <div style={{ color: 'var(--color-dark-walnut)', marginBottom: '0.75rem' }}>
              <Scale size={28} />
            </div>
            <h4 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.35rem' }}>
              3. Risk Triage & Reporting
            </h4>
            <p style={{ fontSize: '0.85rem', color: 'var(--color-taupe)', lineHeight: 1.5 }}>
              Calculates a weighted document risk index, highlights high-risk terms, and compiles executive PDF audit briefs.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
