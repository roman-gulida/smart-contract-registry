import type { DocClass } from "../types";

interface Props {
  value: string;
  size?: "sm" | "md";
}

export default function ClassBadge({ value, size = "md" }: Props) {
  const key = value.toLowerCase() as DocClass;
  return (
    <span className={`badge-base badge-${size} badge-${key}`}>
      {value.toLowerCase()}
    </span>
  );
}
