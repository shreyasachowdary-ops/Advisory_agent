interface Props {
  riskLevel: "referral" | "urgent";
}

export default function EscalationBanner({ riskLevel }: Props) {
  const label = riskLevel === "urgent" ? "Urgent — Safeguarding" : "Referral Recommended";
  return (
    <div className={`escalation-banner ${riskLevel}`}>
      <strong>{label}</strong>
      <p>
        This response requires attention from a trained professional.
        Please do not rely on general advice for this concern.
      </p>
    </div>
  );
}
