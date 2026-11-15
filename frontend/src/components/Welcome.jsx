// The empty-conversation screen. Example questions are drawn from the evaluation bank
// and grouped by the kind of work the agent does for them.

const EXAMPLES = [
  {
    kind: "Look something up",
    questions: [
      "Who is the project manager for PRJ-024?",
      "What technologies were used on PRJ-024?",
    ],
  },
  {
    kind: "Calculate across the portfolio",
    questions: [
      "Which risk category occurs most often, and what share of those risks were realized?",
      "What is the average customer satisfaction score by project type?",
    ],
  },
  {
    kind: "Investigate what happened",
    questions: [
      "What caused the schedule delay on PRJ-003?",
      "Why does PRJ-030 combine strong ROI with low adoption?",
    ],
  },
  {
    kind: "Get a recommendation",
    questions: ["Should NexaAI keep offering Data-First Transformation? Under what conditions?"],
  },
];

export default function Welcome({ onAsk, disabled }) {
  return (
    <div className="welcome">
      <h1 className="welcome-title">Ask about NexaAI's projects</h1>
      <p className="welcome-lead">
        Answers come from the project database and 150 project documents, and each one shows the
        sources the agent checked.
      </p>
      <ul className="welcome-facts" aria-label="What the data covers">
        <li>
          <strong>40</strong> projects
        </li>
        <li>
          <strong>20</strong> clients
        </li>
        <li>
          <strong>100</strong> employees
        </li>
        <li>
          <strong>2022–2025</strong>
        </li>
      </ul>

      <div className="examples">
        {EXAMPLES.map((group) => (
          <section key={group.kind} className="example-group">
            <h3>{group.kind}</h3>
            <ul>
              {group.questions.map((q) => (
                <li key={q}>
                  <button type="button" className="example" onClick={() => onAsk(q)} disabled={disabled}>
                    {q}
                  </button>
                </li>
              ))}
            </ul>
          </section>
        ))}
      </div>

      <p className="welcome-note">
        NexaAI is a fictional company with synthetic data. Long analytical questions can take one to
        two minutes.
      </p>
    </div>
  );
}
