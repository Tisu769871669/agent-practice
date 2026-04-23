export type Challenge = {
  id: string;
  slug: string;
  title: string;
  difficulty: "easy" | "medium" | "hard" | "expert";
  status: "runnable" | "planned";
  stage: string;
  focus: string;
  est: string;
};

const runnableIds = new Set([
  "001",
  "002",
  "003",
  "004",
  "005",
  "006",
  "008",
  "010",
  "013",
  "017",
]);

const rows: Array<Omit<Challenge, "status">> = [
  { id: "001", slug: "echo-agent", title: "Echo Agent", difficulty: "easy", stage: "Foundations", focus: "Instruction following", est: "10m" },
  { id: "002", slug: "json-only", title: "JSON Only", difficulty: "easy", stage: "Foundations", focus: "Structured output", est: "15m" },
  { id: "003", slug: "tool-picker", title: "Tool Picker", difficulty: "easy", stage: "Tools", focus: "Tool selection", est: "20m" },
  { id: "004", slug: "calculator-agent", title: "Calculator Agent", difficulty: "easy", stage: "Tools", focus: "Deterministic tools", est: "20m" },
  { id: "005", slug: "ticket-triage", title: "Ticket Triage", difficulty: "easy", stage: "Foundations", focus: "Classification", est: "20m" },
  { id: "006", slug: "mini-rag", title: "Mini RAG", difficulty: "medium", stage: "RAG", focus: "Retrieval + citations", est: "30m" },
  { id: "007", slug: "context-window-diet", title: "Context Window Diet", difficulty: "medium", stage: "Memory", focus: "Compression", est: "25m" },
  { id: "008", slug: "tool-error-recovery", title: "Tool Error Recovery", difficulty: "medium", stage: "Tools", focus: "Retry and degradation", est: "30m" },
  { id: "009", slug: "personal-memory-lite", title: "Personal Memory Lite", difficulty: "medium", stage: "Memory", focus: "Preference memory", est: "30m" },
  { id: "010", slug: "two-step-researcher", title: "Two-Step Researcher", difficulty: "medium", stage: "Workflow", focus: "Retrieve then answer", est: "35m" },
  { id: "011", slug: "prompt-router", title: "Prompt Router", difficulty: "medium", stage: "Workflow", focus: "Routing", est: "25m" },
  { id: "012", slug: "form-filler-agent", title: "Form Filler Agent", difficulty: "medium", stage: "Workflow", focus: "Clarifying questions", est: "25m" },
  { id: "013", slug: "injection-guard-i", title: "Injection Guard I", difficulty: "medium", stage: "Safety", focus: "Prompt injection defense", est: "35m" },
  { id: "014", slug: "unit-test-explainer", title: "Unit Test Explainer", difficulty: "medium", stage: "Workflow", focus: "Diagnostics", est: "30m" },
  { id: "015", slug: "email-assistant-with-approval", title: "Email Assistant with Approval", difficulty: "medium", stage: "Human Loop", focus: "Approval gates", est: "35m" },
  { id: "016", slug: "meeting-memory", title: "Meeting Memory", difficulty: "medium", stage: "Memory", focus: "Action extraction", est: "30m" },
  { id: "017", slug: "eval-harness-basics", title: "Eval Harness Basics", difficulty: "medium", stage: "Evaluation", focus: "Deterministic grading", est: "40m" },
  { id: "018", slug: "react-trace-auditor", title: "ReAct Trace Auditor", difficulty: "hard", stage: "Evaluation", focus: "Trace review", est: "45m" },
  { id: "019", slug: "multi-tool-planner", title: "Multi-Tool Planner", difficulty: "hard", stage: "Workflow", focus: "Planning", est: "45m" },
  { id: "020", slug: "rag-conflicting-sources", title: "RAG with Conflicting Sources", difficulty: "hard", stage: "RAG", focus: "Conflict handling", est: "45m" },
  { id: "021", slug: "long-running-workflow", title: "Long-Running Workflow", difficulty: "hard", stage: "Workflow", focus: "Recoverability", est: "50m" },
  { id: "022", slug: "memory-conflict-resolver", title: "Memory Conflict Resolver", difficulty: "hard", stage: "Memory", focus: "Conflict updates", est: "45m" },
  { id: "023", slug: "human-escalation-agent", title: "Human Escalation Agent", difficulty: "hard", stage: "Human Loop", focus: "Risk escalation", est: "40m" },
  { id: "024", slug: "regression-eval-suite", title: "Regression Eval Suite", difficulty: "hard", stage: "Evaluation", focus: "Regression sets", est: "45m" },
  { id: "025", slug: "agent-judge-calibration", title: "Agent Judge Calibration", difficulty: "hard", stage: "Evaluation", focus: "LLM judge alignment", est: "50m" },
  { id: "026", slug: "injection-guard-ii", title: "Injection Guard II", difficulty: "hard", stage: "Safety", focus: "Tool output isolation", est: "45m" },
  { id: "027", slug: "multi-agent-handoff", title: "Multi-Agent Handoff", difficulty: "expert", stage: "Multi-Agent", focus: "Role handoff", est: "60m" },
  { id: "028", slug: "budget-aware-agent", title: "Budget-Aware Agent", difficulty: "expert", stage: "Evaluation", focus: "Latency and cost routing", est: "60m" },
  { id: "029", slug: "adversarial-rag-challenge", title: "Adversarial RAG Challenge", difficulty: "expert", stage: "Safety", focus: "Adversarial retrieval", est: "60m" },
  { id: "030", slug: "capstone-support-agent", title: "Capstone Support Agent", difficulty: "expert", stage: "Capstone", focus: "End-to-end support agent", est: "90m" },
];

export const challenges: Challenge[] = rows.map((row) => ({
  ...row,
  status: runnableIds.has(row.id) ? "runnable" : "planned",
}));

export const stages = [
  { name: "Foundations", note: "Instruction following, structured output, deterministic behavior." },
  { name: "Tools", note: "Tool choice, parameters, retries, bounded execution." },
  { name: "RAG", note: "Citations, source faithfulness, conflicting evidence." },
  { name: "Memory", note: "State compression, preferences, conflict handling." },
  { name: "Workflow", note: "Routing, staged execution, recoverability." },
  { name: "Safety", note: "Prompt injection resistance and trust boundaries." },
  { name: "Evaluation", note: "Graders, regression suites, trace inspection." },
  { name: "Capstone", note: "Integrated agent systems with realistic constraints." },
];

export const runnableChallenges = challenges.filter((challenge) => challenge.status === "runnable");
