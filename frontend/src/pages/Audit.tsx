import { useCallback, useRef, useState } from "react";
import { api } from "../services/api";
import type { AuditResponse } from "../types";
import ClassBadge from "../components/ClassBadge";
import HashDisplay from "../components/HashDisplay";
import { CircleAlert, CircleCheck, Info, Upload } from "lucide-react";

type Mode = "hash" | "file";

export default function AuditPage() {
  const [mode, setMode] = useState<Mode>("hash");

  // Hash mode
  const [hash, setHash] = useState("");

  // File mode
  const [file, setFile] = useState<File | null>(null);
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AuditResponse | null>(null);
  const [error, setError] = useState("");

  const searchByHash = async () => {
    const q = hash.trim();
    if (!q) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      setResult(await api.auditDocument(q));
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Lookup failed");
    } finally {
      setLoading(false);
    }
  };

  const searchByFile = async () => {
    if (!file) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      setResult(await api.auditVerify(file));
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Verification failed");
    } finally {
      setLoading(false);
    }
  };

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const f = e.dataTransfer.files[0];
    if (f?.type === "application/pdf") {
      setFile(f);
      setResult(null);
      setError("");
    }
  }, []);

  const doc = result?.db_record;
  const chain = result?.chain_record;
  const v = result?.verification;

  const allPass =
    v && v.doc_hash_matches && v.model_hash_matches && v.classification_matches;

  const bannerClass =
    result?.hashes_match === true
      ? "banner banner-success"
      : result?.hashes_match === false
        ? "banner banner-error"
        : result
          ? "banner banner-neutral"
          : "";

  const bannerTextClass =
    result?.hashes_match === true
      ? "text-sm font-medium text-success"
      : result?.hashes_match === false
        ? "text-sm font-medium text-error"
        : "text-sm font-medium text-muted";

  return (
    <div className="page max-w-3xl">
      <div className="mb-10">
        <p className="page-label">Document Registry</p>
        <h1 className="page-title mb-2">Audit</h1>
        <p className="page-description">
          Search by hash to view the blockchain record, or upload a PDF to run a
          full verification - reclassifying the document and comparing hashes.
        </p>
      </div>

      {/* Mode toggle */}
      <div
        className="flex mb-6 rounded overflow-hidden"
        style={{
          border: "1px solid var(--color-border)",
          width: "fit-content",
        }}
      >
        {(["hash", "file"] as Mode[]).map((m) => (
          <button
            key={m}
            onClick={() => {
              setMode(m);
              setResult(null);
              setError("");
            }}
            className="px-5 py-2 text-sm font-medium transition-colors border-none cursor-pointer"
            style={{
              background:
                mode === m ? "var(--color-ink)" : "var(--color-surface)",
              color: mode === m ? "#fff" : "var(--color-ink-muted)",
            }}
          >
            {m === "hash" ? "Search by Hash" : "Upload to Verify"}
          </button>
        ))}
      </div>

      {/* Hash mode */}
      {mode === "hash" && (
        <div className="flex gap-2 mb-8">
          <input
            type="text"
            placeholder="0x…"
            value={hash}
            onChange={(e) => setHash(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && searchByHash()}
            spellCheck={false}
            className="hash-search-input"
          />
          <button
            onClick={searchByHash}
            disabled={!hash.trim() || loading}
            className="btn-primary"
          >
            {loading ? "…" : "Verify"}
          </button>
        </div>
      )}

      {/* File mode */}
      {mode === "file" && (
        <div className="flex flex-col gap-4 mb-8">
          <div
            onDrop={onDrop}
            onDragOver={(e) => {
              e.preventDefault();
              setDragging(true);
            }}
            onDragLeave={() => setDragging(false)}
            onClick={() => inputRef.current?.click()}
            className={`dropzone ${dragging ? "dropzone-dragging" : ""}`}
          >
            <input
              ref={inputRef}
              type="file"
              accept="application/pdf"
              className="hidden"
              onChange={(e) => {
                const f = e.target.files?.[0];
                if (f) {
                  setFile(f);
                  setResult(null);
                  setError("");
                }
              }}
            />
            {file ? (
              <div className="flex flex-col items-center gap-2">
                <span className="text-ink font-medium text-sm">
                  {file.name}
                </span>
                <span className="mono-faint">
                  {(file.size / 1024).toFixed(1)} KB
                </span>
              </div>
            ) : (
              <div className="flex flex-col items-center gap-3">
                <span className="text-faint">
                  <Upload size={28} />
                </span>
                <p className="text-sm text-ink font-medium">
                  Drop the PDF to verify
                </p>
                <p className="text-xs text-faint">or click to browse</p>
              </div>
            )}
          </div>
          <button
            onClick={searchByFile}
            disabled={!file || loading}
            className="btn-primary self-start"
          >
            {loading ? "Verifying…" : "Run Verification"}
          </button>
        </div>
      )}

      {error && <p className="alert-error mb-6">{error}</p>}

      {result && (
        <div className="flex flex-col gap-5">
          {/* Verification result (file mode only) */}
          {v && (
            <div
              className="rounded p-5 flex flex-col gap-3"
              style={{
                background: allPass
                  ? "var(--color-success-bg)"
                  : "var(--color-error-bg)",
                border: `1px solid ${allPass ? "var(--color-success-border)" : "var(--color-error-border)"}`,
              }}
            >
              <div className="flex items-center gap-2">
                {allPass ? (
                  <CircleCheck size={18} className="text-success" />
                ) : (
                  <CircleAlert size={18} className="text-error" />
                )}
                <span
                  className={`text-sm font-semibold ${allPass ? "text-success" : "text-error"}`}
                >
                  {v.verdict}
                </span>
              </div>
              <div className="flex flex-col gap-1.5">
                <CheckLine
                  ok={v.doc_hash_matches}
                  label="Document hash matches original"
                />
                <CheckLine
                  ok={v.model_hash_matches}
                  label="Model hash matches original"
                />
                <CheckLine
                  ok={v.classification_matches}
                  label={
                    v.classification_matches
                      ? `Classification consistent: ${v.rerun_classification}`
                      : `Classification changed: was '${v.stored_classification}', now '${v.rerun_classification}'`
                  }
                />
              </div>
            </div>
          )}

          {/* DB vs Chain banner (hash mode) */}
          {result.hashes_match !== null && (
            <div className={bannerClass}>
              <span className="text-lg flex items-center">
                {result.hashes_match === true ? (
                  <CircleCheck size={18} className="text-success" />
                ) : (
                  <CircleAlert size={18} className="text-error" />
                )}
              </span>
              <span className={bannerTextClass}>{result.message}</span>
            </div>
          )}

          {/* Neutral info banner */}
          {result.hashes_match === null && !v && (
            <div className="banner banner-neutral">
              <Info size={18} />
              <span className="text-sm font-medium text-muted">
                {result.message}
              </span>
            </div>
          )}

          {/* DB Record */}
          {doc && (
            <Section title="Database Record">
              <Row label="Filename" value={doc.filename} />
              <Row label="Classification">
                <ClassBadge value={doc.classification} />
              </Row>
              <Row label="Document Hash">
                <HashDisplay hash={doc.doc_hash} truncate={false} />
              </Row>
              <Row label="Model Hash">
                <HashDisplay hash={doc.model_hash} />
              </Row>
              <Row
                label="On Chain"
                value={doc.on_chain ? "Registered" : "Pending"}
                valueClass={
                  doc.on_chain ? "text-success mono-sm" : "text-warning mono-sm"
                }
              />
              {doc.blockchain_tx && (
                <Row label="Tx Hash">
                  <HashDisplay hash={doc.blockchain_tx} />
                </Row>
              )}
              <Row
                label="Registered"
                value={new Date(doc.created_at).toLocaleString("ro-RO", {
                  timeZone: "Europe/Bucharest",
                })}
                valueClass="mono-sm"
              />
            </Section>
          )}

          {/* Chain Record */}
          {chain && (
            <Section title="Blockchain Record">
              <Row label="Decision">
                <ClassBadge value={chain.decision} />
              </Row>
              <Row label="Document Hash">
                <HashDisplay hash={chain.doc_hash} truncate={false} />
              </Row>
              <Row label="Model Hash">
                <HashDisplay hash={chain.model_hash} />
              </Row>
              <Row label="Uploader">
                <HashDisplay hash={chain.uploader} truncate={false} />
              </Row>
              <Row
                label="Timestamp"
                value={new Date(chain.timestamp * 1000).toLocaleString(
                  "ro-RO",
                  { timeZone: "Europe/Bucharest" },
                )}
                valueClass="mono-sm"
              />
            </Section>
          )}

          {!doc && !chain && (
            <p className="text-faint text-sm">No record found for this hash.</p>
          )}
        </div>
      )}
    </div>
  );
}

function CheckLine({ ok, label }: { ok: boolean; label: string }) {
  return (
    <div className="flex items-center gap-2">
      <span className={ok ? "text-success" : "text-error"}>
        {ok ? <CircleCheck size={14} /> : <CircleAlert size={14} />}
      </span>
      <span
        className="text-sm"
        style={{ color: ok ? "var(--color-success)" : "var(--color-error)" }}
      >
        {label}
      </span>
    </div>
  );
}

function Section({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="card">
      <div className="card-header">
        <span className="card-header-label">{title}</span>
      </div>
      <div>{children}</div>
    </div>
  );
}

function Row({
  label,
  value,
  valueClass,
  children,
}: {
  label: string;
  value?: string;
  valueClass?: string;
  children?: React.ReactNode;
}) {
  return (
    <div className="card-row">
      <span className="card-row-label">{label}</span>
      <div className="flex items-center gap-2 flex-wrap justify-end">
        {children ?? (
          <span className={`text-sm ${valueClass ?? "text-ink"}`}>{value}</span>
        )}
      </div>
    </div>
  );
}
