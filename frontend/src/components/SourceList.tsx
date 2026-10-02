import type { SourceCitation } from "../api/client";

interface Props {
  sources: SourceCitation[];
}

export default function SourceList({ sources }: Props) {
  if (!sources.length) return null;
  return (
    <div className="source-list">
      <h4>Sources</h4>
      <ul>
        {sources.map((s) => (
          <li key={s.chunk_id}>
            <a href={s.url} target="_blank" rel="noopener noreferrer">
              {s.title}
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
}
