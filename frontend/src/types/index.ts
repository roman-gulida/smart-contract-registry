export type DocClass = "finance" | "hr" | "legal" | "logistics" | "salary";

export interface DocumentRecord {
  id: number;
  filename: string;
  doc_hash: string;
  classification: DocClass;
  model_hash: string;
  blockchain_tx: string | null;
  on_chain: boolean;
  uploader_address: string | null;
  created_at: string;
}

export interface DocumentSummary {
  id: number;
  filename: string;
  doc_hash: string;
  classification: DocClass;
  on_chain: boolean;
  file_path: string | null;
  created_at: string;
}

export interface AuditVerification {
  doc_hash_matches: boolean;
  model_hash_matches: boolean;
  classification_matches: boolean;
  rerun_classification: string;
  stored_classification: string;
  stored_model_hash: string;
  current_model_hash: string;
  verdict: string;
}

export interface AuditResponse {
  db_record: DocumentRecord | null;
  chain_record: {
    doc_hash: string;
    model_hash: string;
    decision: string;
    decision_index: number;
    timestamp: number;
    uploader: string;
  } | null;
  hashes_match: boolean | null;
  verification: AuditVerification | null;
  message: string;
}

export interface HealthResponse {
  status: string;
  model_loaded: boolean;
  blockchain_connected: boolean;
  contract_address: string | null;
  total_documents_db: number;
  total_documents_chain: number | null;
}