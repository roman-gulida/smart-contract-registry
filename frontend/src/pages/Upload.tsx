import { useCallback, useEffect, useRef, useState } from "react";
import { api } from "../services/api";
import type { DocumentRecord } from "../types";
import ClassBadge from "../components/ClassBadge";
import HashDisplay from "../components/HashDisplay";
import { FileText, MoveLeft, Upload } from "lucide-react";

type State = "idle" | "dragging" | "loading" | "success" | "error";

export default function UploadPage() {
  const [state, setState] = useState<State>("idle");
  const [file, setFile] = useState<File | null>(null);
  const [models, setModels] = useState<Record<string, Record<string, unknown>>>(
    {},
  );
  const [modelName, setModelName] = useState("SVM");
  const [modelVersion, setModelVersion] = useState("1.0");
  const [result, setResult] = useState<DocumentRecord | null>(null);
  const [error, setError] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    api.getModels().then((data) => {
      setModels(data);
      const first = Object.keys(data)[0];
      if (first) {
        setModelName(first);
        setModelVersion(Object.keys(data[first])[0]);
      }
    });
  }, []);

  const handleFile = (f: File) => {
    if (f.type !== "application/pdf") {
      setError("Only PDF files are accepted.");
      setState("error");
      return;
    }
    setFile(f);
    setState("idle");
    setError("");
    setResult(null);
  };

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setState("idle");
    const f = e.dataTransfer.files[0];
    if (f) handleFile(f);
  }, []);

  const submit = async () => {
    if (!file) return;
    setState("loading");
    setError("");
    try {
      const res = await api.uploadDocument(file, modelName, modelVersion);
      setResult(res);
      setState("success");
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Upload failed");
      setState("error");
    }
  };

  const reset = () => {
    setState("idle");
    setFile(null);
    setResult(null);
    setError("");
  };

  return (
    <div className="page max-w-3xl">
      <div className="mb-10">
        <p className="page-label">Document Registry</p>
        <h1 className="page-title mb-2">Upload &amp; Classify</h1>
        <p className="page-description">
          Upload a PDF to classify it using the ML model and register the result
          on the blockchain.
        </p>
      </div>

      {state !== "success" ? (
        <div className="flex flex-col gap-5">
          {/* Drop zone */}
          <div
            onDrop={onDrop}
            onDragOver={(e) => {
              e.preventDefault();
              setState("dragging");
            }}
            onDragLeave={() => setState("idle")}
            onClick={() => inputRef.current?.click()}
            className={`dropzone ${state === "dragging" ? "dropzone-dragging" : ""}`}
          >
            <input
              ref={inputRef}
              type="file"
              accept="application/pdf"
              className="hidden"
              onChange={(e) =>
                e.target.files?.[0] && handleFile(e.target.files[0])
              }
            />
            {file ? (
              <div className="flex flex-col items-center gap-2">
                <FileText size={36} />
                <span className="font-medium text-sm text-ink">
                  {file.name}
                </span>
                <span className="mono-faint">
                  {(file.size / 1024).toFixed(1)} KB
                </span>
              </div>
            ) : (
              <div className="flex flex-col items-center gap-3">
                <span className="text-faint">
                  <Upload size={36} />
                </span>
                <div>
                  <p className="text-sm font-medium text-ink">
                    Drop a PDF here
                  </p>
                  <p className="text-xs mt-1 text-faint">or click to browse</p>
                </div>
              </div>
            )}
          </div>

          {/* Model fields */}
          <div className="card p-5 flex flex-col gap-4">
            <p className="card-header-label">Model Info</p>
            <div className="grid grid-cols-2 gap-4">
              <label className="flex flex-col gap-1.5">
                <span className="field-label">Model</span>
                <select
                  value={modelName}
                  onChange={(e) => {
                    setModelName(e.target.value);
                    const versions = Object.keys(models[e.target.value] ?? {});
                    setModelVersion(versions[0] ?? "1.0");
                  }}
                  className="field-input"
                >
                  {Object.keys(models).map((m) => (
                    <option key={m} value={m}>
                      {m}
                    </option>
                  ))}
                </select>
              </label>
              <label className="flex flex-col gap-1.5">
                <span className="field-label">Version</span>
                <select
                  value={modelVersion}
                  onChange={(e) => setModelVersion(e.target.value)}
                  className="field-input"
                >
                  {Object.keys(models[modelName] ?? { "1.0": {} }).map((v) => (
                    <option key={v} value={v}>
                      {v}
                    </option>
                  ))}
                </select>
              </label>
            </div>
          </div>

          {state === "error" && <p className="alert-error">{error}</p>}

          <button
            onClick={submit}
            disabled={!file || state === "loading"}
            className="btn-primary self-start"
          >
            {state === "loading" ? "Classifying…" : "Classify Document"}
          </button>
        </div>
      ) : (
        result && (
          <div className="card">
            <div className="result-topbar">
              <span className="result-topbar-label">Classification Result</span>
              <ClassBadge value={result.classification} />
            </div>

            <div>
              <Row label="Filename" value={result.filename} />
              <Row label="Classification">
                <ClassBadge value={result.classification} />
              </Row>
              <Row label="Document Hash">
                <HashDisplay hash={result.doc_hash} truncate={false} />
              </Row>
              <Row label="Model Hash">
                <HashDisplay hash={result.model_hash} />
              </Row>
              <Row
                label="On Chain"
                value={result.on_chain ? "Registered" : "Pending"}
                valueClass={
                  result.on_chain
                    ? "text-success mono-sm"
                    : "text-warning mono-sm"
                }
              />
              {result.blockchain_tx && (
                <Row label="Tx Hash">
                  <HashDisplay hash={result.blockchain_tx} />
                </Row>
              )}
              {result.uploader_address && (
                <Row label="Uploader">
                  <HashDisplay
                    hash={result.uploader_address}
                    truncate={false}
                  />
                </Row>
              )}
              <Row
                label="Registered"
                value={new Date(result.created_at).toLocaleString("ro-RO", {
                  timeZone: "Europe/Bucharest",
                })}
                valueClass="mono-sm"
              />
            </div>

            <div className="card-footer">
              <button onClick={reset} className="btn-ghost">
                <span className="flex justify-center items-center gap-1">
                  <MoveLeft size={16} />
                  Upload another
                </span>
              </button>
            </div>
          </div>
        )
      )}
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
      <span className="card-row-label" style={{ width: 120 }}>
        {label}
      </span>
      {children ?? (
        <span
          className={`text-sm text-right ${valueClass ?? "text-ink"}`}
          style={{ wordBreak: "break-all" }}
        >
          {value}
        </span>
      )}
    </div>
  );
}
