import { sendFeedback } from "../api/client";

interface Props {
  onFeedback?: (rating: string) => void;
}

export default function FeedbackBar({ onFeedback }: Props) {
  const handle = async (rating: "helpful" | "not_helpful" | "unsafe") => {
    await sendFeedback(rating);
    onFeedback?.(rating);
  };

  return (
    <div className="feedback-bar">
      <span>Was this helpful?</span>
      <button onClick={() => handle("helpful")}>Helpful</button>
      <button onClick={() => handle("not_helpful")}>Not helpful</button>
      <button className="unsafe" onClick={() => handle("unsafe")}>Unsafe</button>
    </div>
  );
}
