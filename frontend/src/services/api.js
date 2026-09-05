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

/**
 * Fetch control effectiveness comparison (baseline vs current)
 */
export async function getControlEffectiveness() {
  const response = await fetch(`${API_BASE_URL}/effectiveness`);
  if (!response.ok) {
    throw new Error(`Failed to fetch effectiveness with status: ${response.status}`);
  }
  return response.json();
}

/**
 * Snapshot current audit metrics as baseline
 */
export async function captureBaselineSnapshot(sourceLabel = "batch_1") {
  const response = await fetch(`${API_BASE_URL}/baseline/capture?source_label=${encodeURIComponent(sourceLabel)}`, {
    method: "POST",
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to capture baseline snapshot");
  }
  return response.json();
}

/**
 * Generate preview of synthetic settlement dataset
 */
export async function previewGeneratedDataset(config) {
  const response = await fetch(`${API_BASE_URL}/api/generate/dataset/preview`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(config || {}),
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to generate dataset preview");
  }
  return response.json();
}

/**
 * Generate preview of synthetic MSA contract specification
 */
export async function previewGeneratedMSA(config) {
  const response = await fetch(`${API_BASE_URL}/api/generate/msa/preview`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(config || {}),
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to generate MSA preview");
  }
  return response.json();
}

/**
 * Upload and validate custom settlement CSV file
 */
export async function uploadCustomCSV(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/api/upload/csv`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to validate custom settlement CSV");
  }

  return response.json();
}

/**
 * Upload and validate custom MSA JSON specification
 */
export async function uploadCustomMSA(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/api/upload/msa`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to validate custom MSA JSON");
  }

  return response.json();
}

/**
 * Activate active custom/generated data and execute audit + agent pipeline
 */
export async function activateAuditData(payload) {
  const response = await fetch(`${API_BASE_URL}/api/generate/activate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload || {}),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to run audit with active data");
  }

  return response.json();
}

/**
 * Send query to AI Finance Controller Copilot
 */
export async function sendCopilotMessage(message, history = []) {
  const response = await fetch(`${API_BASE_URL}/api/copilot/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, history }),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || "Copilot service unavailable");
  }

  return response.json();
}

