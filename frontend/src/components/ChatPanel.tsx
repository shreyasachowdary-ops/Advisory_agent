import { useState } from "react";
import type { Audience, AgeBand, ChatResponse } from "../api/client";
import { sendChat } from "../api/client";
import EscalationBanner from "./EscalationBanner";
import SourceList from "./SourceList";
import FeedbackBar from "./FeedbackBar";

interface Message {
  role: "user" | "assistant";
  content: string;
  response?: ChatResponse;
}

interface Props {
  audience: Audience;
  ageBand: AgeBand;
}

export default function ChatPanel({ audience, ageBand }: Props) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMsg = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMsg }]);
    setLoading(true);

    try {
      const response = await sendChat({
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
        { role: "assistant", content: "Sorry, something went wrong. Please try again." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleFollowUp = (text: string) => {
    setInput(text);
  };

  return (
    <div className="chat-panel">
      <div className="messages">
        {messages.length === 0 && (
          <p className="placeholder">
            Ask about routines, behaviour, play-based learning, or parent–teacher communication.
          </p>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            {msg.role === "assistant" && msg.response && msg.response.risk_level !== "normal" && (
              <EscalationBanner riskLevel={msg.response.risk_level as "urgent" | "referral"} />
            )}
            <div className="message-content">{msg.content}</div>
            {msg.response && (
              <>
                <SourceList sources={msg.response.sources} />
                {msg.response.suggested_follow_up && msg.response.risk_level === "normal" && (
                  <button
                    className="follow-up-btn"
                    onClick={() => handleFollowUp(msg.response!.suggested_follow_up!)}
                  >
                    {msg.response.suggested_follow_up}
                  </button>
                )}
                <FeedbackBar />
              </>
            )}
          </div>
        ))}
        {loading && <div className="message assistant"><div className="loading">Thinking...</div></div>}
      </div>
      <form onSubmit={handleSubmit} className="chat-input">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your question..."
          disabled={loading}
        />
        <button type="submit" disabled={loading || !input.trim()}>Send</button>
      </form>
    </div>
  );
}
