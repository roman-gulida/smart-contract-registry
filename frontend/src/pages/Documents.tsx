import { useEffect, useMemo, useState } from "react";
import { api } from "../services/api";
import type { DocumentSummary, DocClass } from "../types";
import HashDisplay from "../components/HashDisplay";
import ClassBadge from "../components/ClassBadge";
import { Check, FileDown, MoveDown, MoveUp, X } from "lucide-react";

type SortKey = "created_at" | "classification" | "filename";
type SortDir = "asc" | "desc";

const ALL_CLASSES: DocClass[] = [
  "finance",
  "hr",
  "legal",
  "logistics",
  "salary",
];

function SortBtn({
  k,
  label,
  sortKey,
  sortDir,
  onToggle,
}: {
  k: SortKey;
  label: string;
  sortKey: SortKey;
  sortDir: SortDir;
  onToggle: (k: SortKey) => void;
}) {
  return (
    <button
      onClick={() => onToggle(k)}
      className="sort-btn"
      style={{
        color: sortKey === k ? "var(--color-ink)" : "var(--color-ink-faint)",
      }}
    >
      {label}
      {sortKey === k && (
        <span>
          {sortDir === "asc" ? <MoveUp size={12} /> : <MoveDown size={12} />}
        </span>
      )}
    </button>
  );
}

// filename | class | hash | chain | date | open
const COL = "2fr 1fr 1.8fr 0.6fr 1fr 2rem";

export default function Documents() {
  const [docs, setDocs] = useState<DocumentSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [search, setSearch] = useState("");
  const [classFilter, setClassFilter] = useState<DocClass | "all">("all");
  const [chainFilter, setChainFilter] = useState<"all" | "on" | "off">("all");
  const [sortKey, setSortKey] = useState<SortKey>("created_at");
  const [sortDir, setSortDir] = useState<SortDir>("desc");

  useEffect(() => {
    api
      .listDocuments()
      .then(setDocs)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const filtered = useMemo(() => {
    let out = [...docs];

    if (search) {
      const q = search.toLowerCase();
      out = out.filter(
        (d) =>
          d.filename.toLowerCase().includes(q) ||
          d.doc_hash.toLowerCase().includes(q),
      );
    }
    if (classFilter !== "all")
      out = out.filter((d) => d.classification === classFilter);
    if (chainFilter === "on") out = out.filter((d) => d.on_chain);
    if (chainFilter === "off") out = out.filter((d) => !d.on_chain);

    out.sort((a, b) => {
      const av =
        sortKey === "created_at"
          ? new Date(a.created_at).getTime().toString()
          : (a[sortKey] as string);
      const bv =
        sortKey === "created_at"
          ? new Date(b.created_at).getTime().toString()
          : (b[sortKey] as string);
      return sortDir === "asc" ? av.localeCompare(bv) : bv.localeCompare(av);
    });

    return out;
  }, [docs, search, classFilter, chainFilter, sortKey, sortDir]);

  const toggleSort = (key: SortKey) => {
    if (sortKey === key) setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    else {
      setSortKey(key);
      setSortDir("asc");
    }
  };

  return (
    <div className="page max-w-6xl">
      <div className="mb-8">
        <p className="page-label">Document Registry</p>
        <h1 className="page-title">All Documents</h1>
      </div>

      {/* Filters */}
      <div className="filters-bar">
        <input
          type="text"
          placeholder="Search filename or hash…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="search-input min-w-48"
        />
        <select
          value={classFilter}
          onChange={(e) => setClassFilter(e.target.value as DocClass | "all")}
          className="filter-select"
        >
          <option value="all">All classes</option>
          {ALL_CLASSES.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
        <select
          value={chainFilter}
          onChange={(e) =>
            setChainFilter(e.target.value as "all" | "on" | "off")
          }
          className="filter-select"
        >
          <option value="all">All chain status</option>
          <option value="on">On chain</option>
          <option value="off">Pending</option>
        </select>
        <span className="mono-faint ml-auto">
          {filtered.length} result{filtered.length !== 1 ? "s" : ""}
        </span>
      </div>

      {/* Table */}
      {loading ? (
        <p className="mono-faint">Loading…</p>
      ) : error ? (
        <p className="text-error text-sm">{error}</p>
      ) : (
        <div className="table-wrapper">
          {/* Header */}
          <div className="table-header" style={{ gridTemplateColumns: COL }}>
            <SortBtn
              k="filename"
              label="Filename"
              sortKey={sortKey}
              sortDir={sortDir}
              onToggle={toggleSort}
            />
            <SortBtn
              k="classification"
              label="Class"
              sortKey={sortKey}
              sortDir={sortDir}
              onToggle={toggleSort}
            />
            <span className="table-col-label">Hash</span>
            <span className="table-col-label">Chain</span>
            <SortBtn
              k="created_at"
              label="Date"
              sortKey={sortKey}
              sortDir={sortDir}
              onToggle={toggleSort}
            />
            <span className="table-col-label"></span>
          </div>

          {filtered.length === 0 ? (
            <div className="px-5 py-10 text-center text-faint text-sm">
              No documents match your filters.
            </div>
          ) : (
            filtered.map((doc, i) => (
              <div
                key={doc.id}
                style={{
                  display: "grid",
                  gridTemplateColumns: COL,
                  alignItems: "center",
                  padding: "14px 20px",
                  background:
                    i % 2 === 0 ? "var(--color-surface)" : "transparent",
                  borderBottom:
                    i < filtered.length - 1
                      ? "1px solid var(--color-border)"
                      : "none",
                }}
                onMouseEnter={(e) =>
                  (e.currentTarget.style.background = "rgba(0,0,0,0.025)")
                }
                onMouseLeave={(e) =>
                  (e.currentTarget.style.background =
                    i % 2 === 0 ? "var(--color-surface)" : "transparent")
                }
              >
                <span
                  className="text-sm font-medium text-ink truncate pr-4"
                  title={doc.filename}
                >
                  {doc.filename}
                </span>
                <div className="flex">
                  <ClassBadge value={doc.classification} size="sm" />
                </div>
                <HashDisplay hash={doc.doc_hash} />
                <span
                  className={`mono-faint ${doc.on_chain ? "text-success" : ""}`}
                >
                  {doc.on_chain ? <Check size={15} /> : <X size={15} />}
                </span>
                <span className="mono-faint">
                  {new Date(doc.created_at).toLocaleDateString("ro-RO", {
                    timeZone: "Europe/Bucharest",
                  })}
                </span>
                {/* Open PDF */}
                {doc.file_path ? (
                  <a
                    href={api.getDocumentFile(doc.id)}
                    target="_blank"
                    rel="noopener noreferrer"
                    title="Open PDF"
                    className="flex items-center justify-center transition-colors"
                    style={{ color: "var(--color-ink-faint)" }}
                    onMouseEnter={(e) =>
                      (e.currentTarget.style.color = "var(--color-ink)")
                    }
                    onMouseLeave={(e) =>
                      (e.currentTarget.style.color = "var(--color-ink-faint)")
                    }
                  >
                    <FileDown size={16} />
                  </a>
                ) : (
                  <span />
                )}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
