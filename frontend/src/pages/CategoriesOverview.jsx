import React, { useState } from 'react';
import { Search, Grid, CheckCircle2 } from 'lucide-react';
import CategoryAccordion from '../components/CategoryAccordion';
import EmptyState from '../components/EmptyState';
import { TAXONOMY_CATEGORIES } from '../utils/formatters';

export default function CategoriesOverview({ analysisData = null }) {
  if (!analysisData || !analysisData.clauses) {
    return <EmptyState title="No Taxonomy Analysis Available" subtitle="Upload an NDA PDF contract to classify document contents across all 14 legal categories." />;
  }

  const { clauses, detected_categories = [] } = analysisData;
  const [searchTerm, setSearchTerm] = useState('');

  // Filter 14 categories based on search query
  const filteredCategories = TAXONOMY_CATEGORIES.filter((cat) => {
    if (!searchTerm.trim()) return true;
    const q = searchTerm.toLowerCase();
    return (
      cat.name.toLowerCase().includes(q) ||
      cat.roman.toLowerCase().includes(q)
    );
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Header */}
      <div className="parchment-card" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 700, margin: 0, color: 'var(--color-espresso)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Grid size={22} color="var(--color-coffee)" />
            14-Category Legal Taxonomy Analysis
          </h2>
          <p style={{ fontSize: '0.875rem', color: 'var(--color-taupe)', margin: 0 }}>
            Fine-tuned multi-label classification results mapped to standard NDA taxonomy topics.
          </p>
        </div>

        {/* Search Input */}
        <div style={{ position: 'relative', minWidth: '250px' }}>
          <Search size={16} color="var(--color-taupe)" style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)' }} />
          <input
            type="text"
            placeholder="Filter 14 categories..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="form-input"
            style={{ width: '100%', paddingLeft: '2.3rem' }}
          />
        </div>
      </div>

      {/* Categories Accordion List */}
      <div>
        {filteredCategories.map((catInfo) => {
          // Find matching clauses for this category
          const matchingClauses = clauses.filter((c) =>
            c.predicted_categories?.some(
              (p) => p.category.toLowerCase().trim() === catInfo.name.toLowerCase().trim()
            )
          );

          return (
            <CategoryAccordion
              key={catInfo.index}
              categoryInfo={catInfo}
              matchingClauses={matchingClauses}
            />
          );
        })}
      </div>
    </div>
  );
}
