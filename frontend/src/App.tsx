import { useState } from "react";
import type { Audience, AgeBand } from "./api/client";
import SettingsBar from "./components/SettingsBar";
import HealthIndicator from "./components/HealthIndicator";
import ChatPanel from "./components/ChatPanel";
import "./App.css";

export default function App() {
  const [audience, setAudience] = useState<Audience>("parent");
  const [ageBand, setAgeBand] = useState<AgeBand>("4_years");

  return (
    <div className="app">
      <header>
        <h1>Parent/Teacher Advisor</h1>
        <p className="subtitle">Practical guidance for preschool children (ages 2–5)</p>
        <HealthIndicator />
      </header>
      <SettingsBar
        audience={audience}
        ageBand={ageBand}
        onAudienceChange={setAudience}
        onAgeBandChange={setAgeBand}
      />
      <ChatPanel audience={audience} ageBand={ageBand} />
      <footer>
        <small>
          General educational guidance only — not diagnosis, counselling, or medical advice.
        </small>
      </footer>
    </div>
  );
}
