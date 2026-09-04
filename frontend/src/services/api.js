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

/**
 * Fetch all agent control cases with summary
 */
export async function getAgentCases() {
  const response = await fetch(`${API_BASE_URL}/cases`);
  if (!response.ok) {
    throw new Error(`Failed to fetch cases with status: ${response.status}`);
  }
  return response.json();
}

/**
 * Approve a case's recommended action (human-in-the-loop)
 */
export async function approveCase(caseId) {
  const response = await fetch(`${API_BASE_URL}/cases/${caseId}/approve`, {
    method: "POST",
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to approve case");
  }
  return response.json();
}

/**
 * Reject a case's recommended action
 */
export async function rejectCase(caseId, reason = "Rejected by operator") {
  const response = await fetch(`${API_BASE_URL}/cases/${caseId}/reject?reason=${encodeURIComponent(reason)}`, {
    method: "POST",
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to reject case");
  }
  return response.json();
}