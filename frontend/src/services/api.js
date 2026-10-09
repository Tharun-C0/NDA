/**
 * Centralized API client for NDA Analysis FastAPI backend.
 */

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

/**
 * Handle API responses and throw standardized error objects.
 */
async function handleResponse(response) {
  if (!response.ok) {
    let errorDetail = `HTTP Error ${response.status}: ${response.statusText}`;
    try {
      const errorJson = await response.json();
      if (errorJson.detail) {
        errorDetail = typeof errorJson.detail === 'string' 
          ? errorJson.detail 
          : JSON.stringify(errorJson.detail);
      }
    } catch (_) {
      // Response was not JSON
    }
    throw new Error(errorDetail);
  }
  return response.json();
}

/**
 * Upload and analyze an NDA PDF document.
 * @param {File} file - The PDF file object
 * @param {string} modelChoice - 'legal_roberta', 'legal_bert', or 'deberta_v3'
 * @param {number} threshold - Decision threshold (0.10 - 0.90)
 */
export async function analyzeDocument(file, modelChoice = 'legal_roberta', threshold = 0.60) {
  const formData = new FormData();
  formData.append('file', file);

  const url = `${BASE_URL}/api/v1/documents/analyze?model_choice=${encodeURIComponent(modelChoice)}&threshold=${encodeURIComponent(threshold)}`;

  const response = await fetch(url, {
    method: 'POST',
    body: formData,
  });

  return handleResponse(response);
}

/**
 * Get paginated list of analyzed documents from SQLite history.
 * @param {number} skip - Offset skip
 * @param {number} limit - Limit per page
 */
export async function getDocuments(skip = 0, limit = 20) {
  const url = `${BASE_URL}/api/v1/documents?skip=${skip}&limit=${limit}`;
  const response = await fetch(url);
  return handleResponse(response);
}

/**
 * Get full analysis details for a single document by ID.
 * @param {string} documentId - The document UUID
 */
export async function getDocumentById(documentId) {
  const url = `${BASE_URL}/api/v1/documents/${encodeURIComponent(documentId)}`;
  const response = await fetch(url);
  return handleResponse(response);
}

/**
 * Download executive PDF risk report for a given document.
 * @param {string} documentId - Document UUID
 * @param {string} filename - Filename for saved file
 */
export async function downloadReportBlob(documentId, filename = null) {
  const url = `${BASE_URL}/api/v1/documents/${encodeURIComponent(documentId)}/report`;
  const response = await fetch(url);
  
  if (!response.ok) {
    let errorDetail = `Failed to download PDF report (${response.status})`;
    try {
      const errorJson = await response.json();
      if (errorJson.detail) errorDetail = errorJson.detail;
    } catch (_) {}
    throw new Error(errorDetail);
  }

  const blob = await response.blob();
  const blobUrl = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = blobUrl;
  a.download = filename || `NDA_Risk_Report_${documentId}.pdf`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(blobUrl);
}

/**
 * Check backend API health status.
 */
export async function checkHealth() {
  const url = `${BASE_URL}/api/v1/health`;
  const response = await fetch(url);
  return handleResponse(response);
}

export { BASE_URL };
