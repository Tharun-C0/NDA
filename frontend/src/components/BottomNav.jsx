import React from 'react';
import { UploadCloud, Scale, FileText, Grid, FileCheck } from 'lucide-react';

const NAV_ITEMS = [
  { id: 'upload', label: 'Deposit Contract', icon: UploadCloud },
  { id: 'audit', label: 'Risk Summary', icon: Scale },
  { id: 'workbench', label: 'Legal Workbench', icon: FileText },
  { id: 'categories', label: '14 Categories', icon: Grid },
  { id: 'export', label: 'Executive Brief', icon: FileCheck },
];

export default function BottomNav({ activeScreen = 'upload', onSelectScreen = () => {} }) {
  return (
    <nav
      className="bottom-nav"
      aria-label="Application Main Navigation"
      style={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        right: 0,
        height: '64px',
        backgroundColor: 'var(--color-ivory)',
        borderTop: '1px solid var(--color-border)',
        boxShadow: '0 -4px 16px rgba(48, 37, 31, 0.08)',
        zIndex: 50,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <div
        style={{
          width: '100%',
          maxWidth: '800px',
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-around',
          padding: '0 0.5rem',
        }}
      >
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = activeScreen === item.id;

          return (
            <button
              key={item.id}
              onClick={() => onSelectScreen(item.id)}
              className="nav-item-btn"
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.15rem',
                height: '100%',
                flex: 1,
                border: 'none',
                background: 'none',
                cursor: 'pointer',
                color: isActive ? 'var(--color-coffee)' : 'var(--color-taupe)',
                fontWeight: isActive ? 700 : 400,
                transition: 'all 0.15s ease',
                position: 'relative',
              }}
            >
              {/* Active Indicator Line */}
              {isActive && (
                <div
                  style={{
                    position: 'absolute',
                    top: 0,
                    left: '20%',
                    right: '20%',
                    height: '3px',
                    backgroundColor: 'var(--color-brass)',
                    borderBottomLeftRadius: '2px',
                    borderBottomRightRadius: '2px',
                  }}
                />
              )}

              <Icon size={20} strokeWidth={isActive ? 2.3 : 1.8} color={isActive ? 'var(--color-coffee)' : 'var(--color-taupe)'} />
              <span
                style={{
                  fontSize: '0.725rem',
                  lineHeight: 1.1,
                  textAlign: 'center',
                  whiteSpace: 'nowrap',
                }}
              >
                {item.label}
              </span>
            </button>
          );
        })}
      </div>
    </nav>
  );
}
