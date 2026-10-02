export type Audience = "parent" | "teacher";
export type AgeBand = "2_years" | "3_years" | "4_years" | "5_years";

export interface ChatRequest {
  message: string;
  audience: Audience;
  age_band: AgeBand;
  language: "en";
}

export interface SourceCitation {
  title: string;
  url: string;
  chunk_id: string;
}

export interface ChatResponse {
  answer: string;
  risk_level: "normal" | "referral" | "urgent";
  sources: SourceCitation[];
  suggested_follow_up?: string;
  requires_human_review: boolean;
}

export async function sendChat(payload: ChatRequest): Promise<ChatResponse> {
  const res = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Chat request failed");
  return res.json();
}

export async function getHealth() {
  const res = await fetch("/api/health");
  return res.json();
}

export async function sendFeedback(rating: "helpful" | "not_helpful" | "unsafe") {
  await fetch("/api/feedback", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ rating }),
  });
}
