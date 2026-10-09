import React, { useState } from 'react';
import Header from './components/Header';
import BottomNav from './components/BottomNav';
import DocumentHistoryModal from './components/DocumentHistoryModal';

import UploadNDA from './pages/UploadNDA';
import ProcessingScreen from './pages/ProcessingScreen';
import ContractAudit from './pages/ContractAudit';
import ClauseAnalysis from './pages/ClauseAnalysis';
import CategoriesOverview from './pages/CategoriesOverview';
import ExportReport from './pages/ExportReport';

import { analyzeDocument, getDocumentById } from './services/api';

export default function App() {
  const [activeScreen, setActiveScreen] = useState('upload');
  const [activeDocument, setActiveDocument] = useState(null);

  // Model & Threshold state
  const [selectedModel, setSelectedModel] = useState('legal_roberta');
  const [threshold, setThreshold] = useState(0.60);

  // History Modal State
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);

  // Processing Screen State
  const [stagedFileName, setStagedFileName] = useState('');
  const [processingStage, setProcessingStage] = useState(1);
  const [processingError, setProcessingError] = useState(null);
  const [currentFileObject, setCurrentFileObject] = useState(null);

  // Handle uploading and starting real analysis
  const handleStartAnalysis = async (fileObj) => {
    if (!fileObj) return;

    setCurrentFileObject(fileObj);
    setStagedFileName(fileObj.name);
    setActiveScreen('processing');
    setProcessingStage(1);
    setProcessingError(null);

    try {
      // Stage 1: Extraction & Segmentation
      setProcessingStage(1);

      // Trigger FastAPI call
      setProcessingStage(2); // Transformer classification

      const response = await analyzeDocument(fileObj, selectedModel, threshold);

      setProcessingStage(3); // Risk synthesis & report storage

      // Small pause for smooth UI transition
      setTimeout(() => {
        setActiveDocument(response);
        setProcessingStage(4); // Completed
      }, 500);
    } catch (err) {
      setProcessingError(err.message || 'An error occurred during document analysis.');
    }
  };

  // Handle retrying failed analysis
  const handleRetryAnalysis = () => {
    if (currentFileObject) {
      handleStartAnalysis(currentFileObject);
    } else {
      setActiveScreen('upload');
    }
  };

  // Handle selecting document from history
  const handleSelectHistoryDocument = async (documentId) => {
    try {
      const docData = await getDocumentById(documentId);
      setActiveDocument(docData);
      setActiveScreen('audit');
    } catch (err) {
      alert(`Failed to load historical document analysis: ${err.message}`);
    }
  };

  // Handle New Contract reset
  const handleNewContract = () => {
    setActiveDocument(null);
    setCurrentFileObject(null);
    setStagedFileName('');
    setActiveScreen('upload');
  };

  return (
    <div className="app-container">
      {/* Header */}
      <Header
        activeScreen={activeScreen}
        activeDocument={activeDocument}
        onNewContract={handleNewContract}
        onOpenHistory={() => setIsHistoryOpen(true)}
      />

      {/* Main Page Content */}
      <main className="main-content">
        {activeScreen === 'upload' && (
          <UploadNDA
            onStartAnalysis={handleStartAnalysis}
            selectedModel={selectedModel}
            setSelectedModel={setSelectedModel}
            threshold={threshold}
            setThreshold={setThreshold}
          />
        )}

        {activeScreen === 'processing' && (
          <ProcessingScreen
            filename={stagedFileName}
            selectedModel={selectedModel}
            threshold={threshold}
            currentStage={processingStage}
            error={processingError}
            onRetry={handleRetryAnalysis}
            onComplete={() => setActiveScreen('audit')}
          />
        )}

        {activeScreen === 'audit' && (
          <ContractAudit
            analysisData={activeDocument}
            onNavigateWorkbench={() => setActiveScreen('workbench')}
            onSelectCategory={() => setActiveScreen('categories')}
          />
        )}

        {activeScreen === 'workbench' && (
          <ClauseAnalysis analysisData={activeDocument} />
        )}

        {activeScreen === 'categories' && (
          <CategoriesOverview analysisData={activeDocument} />
        )}

        {activeScreen === 'export' && (
          <ExportReport analysisData={activeDocument} />
        )}
      </main>

      {/* Persistent Bottom Navigation */}
      <BottomNav
        activeScreen={activeScreen}
        onSelectScreen={(screenId) => setActiveScreen(screenId)}
      />

      {/* Analysis History Modal */}
      <DocumentHistoryModal
        isOpen={isHistoryOpen}
        onClose={() => setIsHistoryOpen(false)}
        onSelectDocument={handleSelectHistoryDocument}
      />
    </div>
  );
}
