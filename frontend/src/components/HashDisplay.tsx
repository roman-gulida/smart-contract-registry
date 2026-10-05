import { useState } from "react";
import { Check, Copy } from "lucide-react";

interface Props {
  hash: string;
  truncate?: boolean;
}

export default function HashDisplay({ hash, truncate = true }: Props) {
  const [copied, setCopied] = useState(false);

  const display = truncate ? `${hash.slice(0, 10)}…${hash.slice(-6)}` : hash;

  const copy = () => {
    navigator.clipboard.writeText(hash);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <span className="inline-flex items-center gap-1.5 group">
      <span className="hash-text">{display}</span>
      <button
        onClick={copy}
        title="Copy hash"
        className="transition-opacity opacity-0 group-hover:opacity-100 cursor-pointer bg-transparent border-none p-0 leading-none"
      >
        {copied ? (
          <Check size={12} className="text-success" />
        ) : (
          <Copy size={12} className="text-faint" />
        )}
      </button>
    </span>
  );
}
