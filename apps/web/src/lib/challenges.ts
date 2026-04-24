import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

import { load } from "js-yaml";

import { sitePath } from "./urls";

export type Difficulty = "easy" | "medium" | "hard" | "expert";
export type ChallengeStatus = "runnable" | "planned";

export type Challenge = {
  id: string;
  slug: string;
  title: string;
  track: string;
  stage: string;
  difficulty: Difficulty;
  status: ChallengeStatus;
  version: string;
  summary: string;
  tags: string[];
  focus: string;
  est: string;
  href: string;
  directory: string;
};

export type Stage = {
  track: string;
  name: string;
  note: string;
  total: number;
  runnable: number;
};

type Catalog = {
  schema_version: string;
  challenges: CatalogEntry[];
};

type CatalogEntry = {
  id: string;
  slug: string;
  title: string;
  track: string;
  difficulty: Difficulty;
  status: ChallengeStatus;
  version: string;
  summary: string;
  tags: string[];
};

const catalogPath = fileURLToPath(
  new URL("../../../../challenges/catalog.yaml", import.meta.url),
);

const stageNotes: Record<string, { name: string; note: string }> = {
  foundations: {
    name: "Foundations",
    note: "Instruction following, structured output, deterministic behavior.",
  },
  tools: {
    name: "Tools",
    note: "Tool choice, parameters, retries, bounded execution.",
  },
  rag: {
    name: "RAG",
    note: "Citations, source faithfulness, conflicting evidence.",
  },
  memory: {
    name: "Memory",
    note: "State compression, preferences, conflict handling.",
  },
  workflow: {
    name: "Workflow",
    note: "Routing, staged execution, recoverability.",
  },
  safety: {
    name: "Safety",
    note: "Prompt injection resistance and trust boundaries.",
  },
  evaluation: {
    name: "Evaluation",
    note: "Graders, regression suites, trace inspection.",
  },
  capstone: {
    name: "Capstone",
    note: "Integrated agent systems with realistic constraints.",
  },
};

const stageOrder = [
  "foundations",
  "tools",
  "rag",
  "memory",
  "workflow",
  "safety",
  "evaluation",
  "capstone",
];

const estimatesByDifficulty: Record<Difficulty, string> = {
  easy: "15-20m",
  medium: "30-40m",
  hard: "45-60m",
  expert: "60-90m",
};

const catalog = loadCatalog();

export const challenges: Challenge[] = catalog.challenges.map((entry) => {
  const stage = stageNotes[entry.track] ?? {
    name: toTitleCase(entry.track),
    note: "Practice track.",
  };

  return {
    ...entry,
    stage: stage.name,
    focus: entry.tags.map(formatTag).join(" / "),
    est: estimatesByDifficulty[entry.difficulty],
    href: sitePath(`/challenges/${entry.slug}`),
    directory: `challenges/${entry.id}-${entry.slug}`,
  };
});

export const runnableChallenges = challenges.filter(
  (challenge) => challenge.status === "runnable",
);

export const stages: Stage[] = stageOrder.map((track) => {
  const stage = stageNotes[track];
  const trackChallenges = challenges.filter((challenge) => challenge.track === track);

  return {
    track,
    name: stage.name,
    note: stage.note,
    total: trackChallenges.length,
    runnable: trackChallenges.filter((challenge) => challenge.status === "runnable")
      .length,
  };
});

export function getChallengeBySlug(slug: string): Challenge | undefined {
  return challenges.find((challenge) => challenge.slug === slug);
}

function loadCatalog(): Catalog {
  const raw = load(readFileSync(catalogPath, "utf-8"));

  if (!isCatalog(raw)) {
    throw new Error(`Invalid challenge catalog: ${catalogPath}`);
  }

  return raw;
}

function isCatalog(value: unknown): value is Catalog {
  if (!value || typeof value !== "object") {
    return false;
  }

  const candidate = value as Partial<Catalog>;
  return (
    typeof candidate.schema_version === "string" &&
    Array.isArray(candidate.challenges) &&
    candidate.challenges.every(isCatalogEntry)
  );
}

function isCatalogEntry(value: unknown): value is CatalogEntry {
  if (!value || typeof value !== "object") {
    return false;
  }

  const entry = value as Partial<CatalogEntry>;
  return (
    typeof entry.id === "string" &&
    typeof entry.slug === "string" &&
    typeof entry.title === "string" &&
    typeof entry.track === "string" &&
    isDifficulty(entry.difficulty) &&
    isStatus(entry.status) &&
    typeof entry.version === "string" &&
    typeof entry.summary === "string" &&
    Array.isArray(entry.tags) &&
    entry.tags.every((tag) => typeof tag === "string")
  );
}

function isDifficulty(value: unknown): value is Difficulty {
  return value === "easy" || value === "medium" || value === "hard" || value === "expert";
}

function isStatus(value: unknown): value is ChallengeStatus {
  return value === "runnable" || value === "planned";
}

function formatTag(value: string): string {
  return value
    .split("-")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

function toTitleCase(value: string): string {
  return formatTag(value);
}
