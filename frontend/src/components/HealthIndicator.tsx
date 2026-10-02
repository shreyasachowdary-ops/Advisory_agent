import { useEffect, useState } from "react";
import { getHealth } from "../api/client";

export default function HealthIndicator() {
  const [status, setStatus] = useState<string>("checking...");
  const [ollama, setOllama] = useState<boolean | null>(null);

  useEffect(() => {
    getHealth()
      .then((data) => {
        setStatus(data.status);
        setOllama(data.ollama);
      })
      .catch(() => setStatus("offline"));
  }, []);

  return (
    <div className="health-indicator">
      <span className={`dot ${status === "ok" ? "ok" : "warn"}`} />
      API: {status}
      {ollama !== null && (
        <span className="ollama-status">
          {ollama ? " · Ollama connected" : " · Ollama offline (fallback mode)"}
        </span>
      )}
    </div>
  );
}
