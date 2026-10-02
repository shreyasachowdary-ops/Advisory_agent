import type { Audience, AgeBand } from "../api/client";

interface Props {
  audience: Audience;
  ageBand: AgeBand;
  onAudienceChange: (a: Audience) => void;
  onAgeBandChange: (a: AgeBand) => void;
}

const AGE_OPTIONS: { value: AgeBand; label: string }[] = [
  { value: "2_years", label: "2 years" },
  { value: "3_years", label: "3 years" },
  { value: "4_years", label: "4 years" },
  { value: "5_years", label: "5 years" },
];

export default function SettingsBar({
  audience,
  ageBand,
  onAudienceChange,
  onAgeBandChange,
}: Props) {
  return (
    <div className="settings-bar">
      <div className="toggle-group">
        <button
          className={audience === "parent" ? "active" : ""}
          onClick={() => onAudienceChange("parent")}
        >
          Parent
        </button>
        <button
          className={audience === "teacher" ? "active" : ""}
          onClick={() => onAudienceChange("teacher")}
        >
          Teacher
        </button>
      </div>
      <select
        value={ageBand}
        onChange={(e) => onAgeBandChange(e.target.value as AgeBand)}
      >
        {AGE_OPTIONS.map((o) => (
          <option key={o.value} value={o.value}>{o.label}</option>
        ))}
      </select>
    </div>
  );
}
