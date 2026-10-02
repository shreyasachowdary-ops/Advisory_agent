/**
 * Parent/Teacher Agentic Advisor page for lnpl_erp_dev_v1
 * Copy to: lnpl_erp_dev_v1/Pages/AdvisorPage.js
 * Also copy to: lnpl_erp_dev_v1/src/Pages/AdvisorPage.js (if App.js imports from src/Pages)
 */
import React, { useState, useEffect, useRef } from "react";
import Navbar from "../components/navbar";
import { getConfig } from "../components/contexts/config";

const DEFAULT_ADVISOR_API = "http://127.0.0.1:8787";

function getAdvisorApiBase() {
  try {
    const { api } = getConfig();
    return api.advisor_base_url || DEFAULT_ADVISOR_API;
  } catch {
    return DEFAULT_ADVISOR_API;
  }
}

async function sendChat(apiBase, payload) {
  const res = await fetch(`${apiBase}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Chat request failed");
  return res.json();
}

async function sendFeedback(apiBase, rating) {
  await fetch(`${apiBase}/api/feedback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ rating }),
  });
}

function AdvisorChat() {
  const [apiBase] = useState(getAdvisorApiBase);
  const [audience, setAudience] = useState("parent");
  const [ageBand, setAgeBand] = useState("4_years");
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [apiStatus, setApiStatus] = useState("checking");
  const bottomRef = useRef(null);

  useEffect(() => {
    fetch(`${apiBase}/api/health`)
      .then((r) => r.json())
      .then((d) => setApiStatus(d.status === "ok" ? "online" : "offline"))
      .catch(() => setApiStatus("offline"));
  }, [apiBase]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMsg = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMsg }]);
    setLoading(true);

    try {
      const response = await sendChat(apiBase, {
        message: userMsg,
        audience,
        age_band: ageBand,
        language: "en",
      });
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: response.answer, response },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "Could not reach the advisor service. Ensure the backend is running on port 8787.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const ageOptions = [
    { value: "2_years", label: "2 years" },
    { value: "3_years", label: "3 years" },
    { value: "4_years", label: "4 years" },
    { value: "5_years", label: "5 years" },
  ];

  return (
    <div className="max-w-4xl mx-auto p-4">
      <div className="mb-4">
        <h2 className="text-2xl font-bold text-indigo-800">
          Parent / Teacher Advisor
        </h2>
        <p className="text-sm text-gray-600">
          Practical guidance for preschool children (ages 2–5). General educational
          advice only — not diagnosis or counselling.
        </p>
        <p className="text-xs text-gray-500 mt-1">
          API: {apiStatus === "online" ? "Connected" : "Offline — start advisor backend"}
        </p>
      </div>

      <div className="flex flex-wrap gap-4 mb-4 p-3 bg-white rounded shadow">
        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => setAudience("parent")}
            className={`px-4 py-1 rounded ${
              audience === "parent"
                ? "bg-indigo-600 text-white"
                : "bg-gray-200 text-gray-700"
            }`}
          >
            Parent
          </button>
          <button
            type="button"
            onClick={() => setAudience("teacher")}
            className={`px-4 py-1 rounded ${
              audience === "teacher"
                ? "bg-indigo-600 text-white"
                : "bg-gray-200 text-gray-700"
            }`}
          >
            Teacher
          </button>
        </div>
        <select
          value={ageBand}
          onChange={(e) => setAgeBand(e.target.value)}
          className="border rounded px-2 py-1"
        >
          {ageOptions.map((o) => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>
      </div>

      <div className="bg-white rounded shadow min-h-[320px] max-h-[480px] overflow-y-auto p-4 mb-4">
        {messages.length === 0 && (
          <p className="text-gray-400 text-center mt-8">
            Ask about routines, behaviour, play-based learning, or parent–teacher communication.
          </p>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`mb-4 ${msg.role === "user" ? "text-right" : ""}`}>
            {msg.response && msg.response.risk_level !== "normal" && (
              <div
                className={`p-3 rounded mb-2 text-sm ${
                  msg.response.risk_level === "urgent"
                    ? "bg-red-50 border border-red-300 text-red-900"
                    : "bg-yellow-50 border border-yellow-300 text-yellow-900"
                }`}
              >
                <strong>
                  {msg.response.risk_level === "urgent"
                    ? "Urgent — Safeguarding"
                    : "Referral Recommended"}
                </strong>
                <p className="mt-1">
                  Please contact your school safeguarding lead or a trained professional.
                </p>
              </div>
            )}
            <div
              className={`inline-block p-3 rounded max-w-[85%] text-left whitespace-pre-wrap ${
                msg.role === "user" ? "bg-indigo-100" : "bg-gray-50"
              }`}
            >
              {msg.content}
            </div>
            {msg.response && msg.response.sources && msg.response.sources.length > 0 && (
              <div className="mt-2 text-xs text-gray-600 text-left">
                <strong>Sources:</strong>
                <ul className="list-disc pl-4">
                  {msg.response.sources.map((s) => (
                    <li key={s.chunk_id}>
                      <a href={s.url} target="_blank" rel="noopener noreferrer" className="text-indigo-600 underline">
                        {s.title}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {msg.response && msg.response.suggested_follow_up && msg.response.risk_level === "normal" && (
              <button
                type="button"
                onClick={() => setInput(msg.response.suggested_follow_up)}
                className="mt-2 text-xs text-indigo-600 underline block"
              >
                {msg.response.suggested_follow_up}
              </button>
            )}
            {msg.response && (
              <div className="mt-2 flex gap-2 text-xs">
                <span className="text-gray-500">Helpful?</span>
                <button type="button" onClick={() => sendFeedback(apiBase, "helpful")} className="text-green-700">Yes</button>
                <button type="button" onClick={() => sendFeedback(apiBase, "not_helpful")} className="text-gray-700">No</button>
                <button type="button" onClick={() => sendFeedback(apiBase, "unsafe")} className="text-red-700">Unsafe</button>
              </div>
            )}
          </div>
        ))}
        {loading && <p className="text-gray-400 italic">Thinking...</p>}
        <div ref={bottomRef} />
      </div>

      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your question..."
          disabled={loading}
          className="flex-1 border rounded px-3 py-2"
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="bg-indigo-600 text-white px-4 py-2 rounded disabled:opacity-50"
        >
          Send
        </button>
      </form>
    </div>
  );
}

function AdvisorPage() {
  return (
    <>
      <Navbar />
      <AdvisorChat />
    </>
  );
}

export default AdvisorPage;
