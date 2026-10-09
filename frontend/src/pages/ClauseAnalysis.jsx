import React, { useState, useMemo } from 'react';
import { Search, Filter, Copy, Check, ChevronLeft, ChevronRight, FileText, Tag } from 'lucide-react';
import ClauseCard from '../components/ClauseCard';
import RiskBadge from '../components/RiskBadge';
import EmptyState from '../components/EmptyState';
import { TAXONOMY_CATEGORIES } from '../utils/formatters';

export default function ClauseAnalysis({ analysisData = null }) {
  if (!analysisData || !analysisData.clauses || analysisData.clauses.length === 0) {
    return <EmptyState title="No Clause Data Available" subtitle="Upload an NDA PDF contract to perform clause extraction and interactive legal analysis." />;
  }

  const { clauses } = analysisData;

  const [searchTerm, setSearchTerm] = useState('');
  const [riskFilter, setRiskFilter] = useState('ALL'); // ALL, HIGH, MEDIUM, LOW
  const [categoryFilter, setCategoryFilter] = useState('ALL');
  const [selectedClauseIndex, setSelectedClauseIndex] = useState(0);
  const [isCopied, setIsCopied] = useState(false);

  // Filter clauses based on search and filters
  const filteredClauses = useMemo(() => {
    return clauses.filter((c) => {
      // Risk filter check
      if (riskFilter !== 'ALL' && c.risk_level.toUpperCase() !== riskFilter) {
        return false;
      }
      // Category filter check
      if (categoryFilter !== 'ALL') {
        const hasCat = c.predicted_categories?.some(
          (p) => p.category.toLowerCase().trim() === categoryFilter.toLowerCase().trim()
        );
        if (!hasCat) return false;
      }
      // Text search check
      if (searchTerm.trim()) {
        const query = searchTerm.toLowerCase();
        const matchesText = c.text.toLowerCase().includes(query);
        const matchesId = c.clause_id.toLowerCase().includes(query);
        if (!matchesText && !matchesId) return false;
      }
      return true;
    });
  }, [clauses, riskFilter, categoryFilter, searchTerm]);

  // Active selected clause from filtered array or fallback
  const activeClause = filteredClauses[selectedClauseIndex] || filteredClauses[0] || clauses[0];

  const handleCopyClause = () => {
    if (!activeClause) return;
    navigator.clipboard.writeText(activeClause.text);
    setIsCopied(true);
    setTimeout(() => setIsCopied(false), 2000);
  };

  const handleNextClause = () => {
    if (selectedClauseIndex < filteredClauses.length - 1) {
      setSelectedClauseIndex((prev) => prev + 1);
    }
  };

  const handlePrevClause = () => {
    if (selectedClauseIndex > 0) {
      setSelectedClauseIndex((prev) => prev - 1);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Header & Filter Toolbar */}
      <div className="parchment-card" style={{ padding: '1.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem', marginBottom: '1rem' }}>
          <div>
            <h2 style={{ fontSize: '1.3rem', fontWeight: 700, margin: 0, color: 'var(--color-espresso)' }}>
              Interactive Legal Workbench
            </h2>
            <span style={{ fontSize: '0.8rem', color: 'var(--color-taupe)' }}>
              Showing {filteredClauses.length} of {clauses.length} total clauses
            </span>
          </div>

          {/* Search bar */}
          <div style={{ position: 'relative', minWidth: '280px', flex: 1, maxWidth: '400px' }}>
            <Search size={16} color="var(--color-taupe)" style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)' }} />
            <input
              type="text"
              placeholder="Search clause text or ID..."
              value={searchTerm}
              onChange={(e) => { setSearchTerm(e.target.value); setSelectedClauseIndex(0); }}
              className="form-input"
              style={{ width: '100%', paddingLeft: '2.3rem' }}
            />
          </div>
        </div>

        {/* Filter Pills & Selects */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.75rem', paddingTop: '0.75rem', borderTop: '1px solid var(--color-border)' }}>
          {/* Risk Level Filter Pills */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
            <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--color-espresso)', marginRight: '0.35rem' }}>
              Risk Level:
            </span>
            {['ALL', 'HIGH', 'MEDIUM', 'LOW'].map((lvl) => (
              <button
                key={lvl}
                onClick={() => { setRiskFilter(lvl); setSelectedClauseIndex(0); }}
                style={{
                  padding: '0.25rem 0.65rem',
                  fontSize: '0.775rem',
                  fontWeight: 600,
                  borderRadius: '9999px',
                  border: '1px solid',
                  cursor: 'pointer',
                  backgroundColor: riskFilter === lvl ? 'var(--color-coffee)' : 'var(--color-paper-white)',
                  color: riskFilter === lvl ? 'var(--color-paper-white)' : 'var(--color-espresso)',
                  borderColor: riskFilter === lvl ? 'var(--color-coffee)' : 'var(--color-border)',
                  transition: 'all 0.15s ease',
                }}
              >
                {lvl}
              </button>
            ))}
          </div>

          {/* Category Dropdown Filter */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--color-espresso)' }}>
              Category:
            </span>
            <select
              value={categoryFilter}
              onChange={(e) => { setCategoryFilter(e.target.value); setSelectedClauseIndex(0); }}
              className="form-select"
              style={{ padding: '0.25rem 0.65rem', fontSize: '0.8rem' }}
            >
              <option value="ALL">All 14 Taxonomy Categories</option>
              {TAXONOMY_CATEGORIES.map((cat) => (
                <option key={cat.index} value={cat.name}>
                  {cat.roman}. {cat.name}
                </option>
              ))}
            </select>

            {(riskFilter !== 'ALL' || categoryFilter !== 'ALL' || searchTerm !== '') && (
              <button
                onClick={() => { setRiskFilter('ALL'); setCategoryFilter('ALL'); setSearchTerm(''); setSelectedClauseIndex(0); }}
                className="btn btn-secondary"
                style={{ padding: '0.25rem 0.55rem', fontSize: '0.75rem' }}
              >
                Clear Filters
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Two-Pane Workspace */}
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(320px, 1fr) minmax(420px, 1.4fr)', gap: '1.25rem' }}>
        {/* Left Pane — Clause List */}
        <div style={{ maxHeight: '720px', overflowY: 'auto', paddingRight: '0.25rem' }}>
          {filteredClauses.length === 0 ? (
            <div className="parchment-card" style={{ textAlign: 'center', padding: '2rem', color: 'var(--color-taupe)' }}>
              <p>No clauses match your current filter settings.</p>
            </div>
          ) : (
            filteredClauses.map((item, idx) => (
              <ClauseCard
                key={item.clause_id}
                clause={item}
                isSelected={activeClause && activeClause.clause_id === item.clause_id}
                onClick={() => setSelectedClauseIndex(idx)}
              />
            ))
          )}
        </div>

        {/* Right Pane — Legal Intelligence Detail */}
        {activeClause ? (
          <div className="parchment-card-elevated" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            {/* Clause Heading & Nav */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid var(--color-border)', paddingBottom: '0.75rem' }}>
              <div>
                <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--color-taupe)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  Clause Identifier
                </span>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--color-espresso)', margin: 0 }}>
                  {activeClause.clause_id}
                </h3>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <RiskBadge level={activeClause.risk_level} />
                <div style={{ display: 'flex', gap: '0.25rem' }}>
                  <button
                    onClick={handlePrevClause}
                    disabled={selectedClauseIndex <= 0}
                    className="btn btn-secondary"
                    style={{ padding: '0.35rem 0.5rem' }}
                    title="Previous Clause"
                  >
                    <ChevronLeft size={16} />
                  </button>
                  <button
                    onClick={handleNextClause}
                    disabled={selectedClauseIndex >= filteredClauses.length - 1}
                    className="btn btn-secondary"
                    style={{ padding: '0.35rem 0.5rem' }}
                    title="Next Clause"
                  >
                    <ChevronRight size={16} />
                  </button>
                </div>
              </div>
            </div>

            {/* Model Classifications */}
            <div>
              <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--color-coffee)', display: 'flex', alignItems: 'center', gap: '0.35rem', marginBottom: '0.4rem' }}>
                <Tag size={14} />
                Multi-Label Classifier Predictions
              </span>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                {activeClause.predicted_categories && activeClause.predicted_categories.length > 0 ? (
                  activeClause.predicted_categories.map((cat, i) => (
                    <span key={i} className="category-badge" style={{ fontSize: '0.825rem', padding: '0.3rem 0.65rem' }}>
                      <strong>{cat.category}</strong>: {(cat.confidence * 100).toFixed(1)}% Sigmoid
                    </span>
                  ))
                ) : (
                  <span style={{ fontSize: '0.825rem', color: 'var(--color-taupe)' }}>
                    No legal taxonomy category flagged above threshold 0.60
                  </span>
                )}
              </div>
            </div>

            {/* Verbatim Excerpt */}
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.35rem' }}>
                <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--color-espresso)' }}>
                  Verbatim Contract Text
                </span>
                <button
                  onClick={handleCopyClause}
                  className="btn btn-secondary"
                  style={{ padding: '0.25rem 0.55rem', fontSize: '0.75rem' }}
                >
                  {isCopied ? <Check size={12} color="green" /> : <Copy size={12} />}
                  {isCopied ? 'Copied to Clipboard' : 'Copy Excerpt'}
                </button>
              </div>

              <div
                style={{
                  backgroundColor: 'var(--color-ivory)',
                  border: '1px solid var(--color-latte)',
                  borderRadius: 'var(--radius-sm)',
                  padding: '1.25rem',
                  fontFamily: 'serif',
                  fontSize: '0.95rem',
                  color: 'var(--color-espresso)',
                  lineHeight: 1.6,
                }}
              >
                "{activeClause.text}"
              </div>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}
