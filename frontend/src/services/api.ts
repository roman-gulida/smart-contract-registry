import type {
  AuditResponse,
  DocumentRecord,
  DocumentSummary,
  HealthResponse,
} from "../types";

const BASE = "http://localhost:8000";

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(BASE + url, options);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail ?? `HTTP ${res.status}`);
  }
  return res.json();
}

export const api = {
  getModels: () =>
    request<Record<string, Record<string, { file: string; hash: string; accuracy: number; f1_score: number }>>>("/api/models"),

  getDocumentFile: (id: number) =>
    `${BASE}/api/documents/${id}/file`,

  auditVerify: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return request<AuditResponse>("/api/audit/verify", {
      method: "POST",
      body: form,
    });
  },

  health: () => request<HealthResponse>("/health"),

  uploadDocument: (file: File, modelName: string, modelVersion: string) => {
    const form = new FormData();
    form.append("file", file);
    form.append("model_name", modelName);
    form.append("model_version", modelVersion);
    return request<DocumentRecord>("/api/documents/upload", {
      method: "POST",
      body: form,
    });
  },

  listDocuments: (skip = 0, limit = 100) =>
    request<DocumentSummary[]>(`/api/documents?skip=${skip}&limit=${limit}`),

  getDocument: (id: number) =>
    request<DocumentRecord>(`/api/documents/${id}`),

  getDocumentByHash: (hash: string) =>
    request<DocumentRecord>(`/api/documents/hash/${hash}`),

  auditDocument: (hash: string) =>
    request<AuditResponse>(`/api/audit/${hash}`),

  getStats: () =>
    request<{
      total_documents_db: number;
      on_chain_count: number;
      pending_chain: number;
      total_documents_chain: number | null;
      classification_breakdown: Record<string, number>;
      blockchain_connected: boolean;
    }>("/api/audit/stats/summary"),
};