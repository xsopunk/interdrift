const API_BASE_URL = "http://127.0.0.1:8000";

/**
 * Fetch health status of the FastAPI backend
 */
export async function checkHealth() {
  const response = await fetch(`${API_BASE_URL}/health`);
  if (!response.ok) {
    throw new Error(`Health check failed with status: ${response.status}`);
  }
  return response.json();
}

/**
 * Ingest/Upload a settlement CSV file to trigger analysis
 */
export async function uploadSettlementFile(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Failed to upload settlement file");
  }

  return response.json();
}

/**
 * Fetch the aggregated final report (overview, leak_by_category, top_offenders, exceptions)
 */
export async function getFinalReport() {
  const response = await fetch(`${API_BASE_URL}/report`);
  if (!response.ok) {
    throw new Error(`Failed to fetch report with status: ${response.status}`);
  }
  return response.json();
}

/**
 * Fetch the row-level audit trail results with LLM explanations
 */
export async function getAuditTrailResults() {
  const response = await fetch(`${API_BASE_URL}/results`);
  if (!response.ok) {
    throw new Error(`Failed to fetch results with status: ${response.status}`);
  }
  return response.json();
}