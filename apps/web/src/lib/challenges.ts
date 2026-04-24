import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

import { load } from "js-yaml";

import {
  challengeZh,
  difficultyLabels,
  formatTag,
  localizedPath,
  type Locale,
  stageNotesByLocale,
  statusLabels,
} from "./i18n";

export type Difficulty = "easy" | "medium" | "hard" | "expert";
export type ChallengeStatus = "runnable" | "planned";

export type Challenge = {
  id: string;
  slug: string;
  title: string;
  track: string;
  stage: string;
  difficulty: Difficulty;
  difficultyLabel: string;
  status: ChallengeStatus;
  statusLabel: string;
  version: string;
  summary: string;
  tags: string[];
  focus: string;
  est: string;
  href: string;
  directory: string;
  detail?: ChallengeDetail;
};

export type ChallengeDetail = {
  background: string;
  objective: string;
  input_contract: string;
  output_contract: string;
  scoring: string;
  example_input: Record<string, unknown>;
  example_output: Record<string, unknown>;
  common_pitfalls: string[];
  stretch_goal: string;
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
const detailsPath = fileURLToPath(
  new URL("../../../../challenges/details.yaml", import.meta.url),
);

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
const details = loadDetails();

export const challenges: Challenge[] = getChallenges("en");

export const runnableChallenges = challenges.filter(
  (challenge) => challenge.status === "runnable",
);

export const stages: Stage[] = getStages("en");

export function getChallengeBySlug(slug: string): Challenge | undefined {
  return challenges.find((challenge) => challenge.slug === slug);
}

export function getChallenges(locale: Locale = "en"): Challenge[] {
  return catalog.challenges.map((entry) => {
    const stageNotes = stageNotesByLocale[locale];
    const stage = stageNotes[entry.track] ?? {
      name: formatTag(entry.track, locale),
      note: locale === "zh" ? "练习路线。" : "Practice track.",
    };
    const translated = locale === "zh" ? challengeZh[entry.id] : undefined;

    return {
      ...entry,
      title: translated?.title ?? entry.title,
      summary: translated?.summary ?? entry.summary,
      stage: stage.name,
      difficultyLabel: difficultyLabels[locale][entry.difficulty] ?? entry.difficulty,
      statusLabel: statusLabels[locale][entry.status] ?? entry.status,
      tags: entry.tags.map((tag) => formatTag(tag, locale)),
      focus: entry.tags.map((tag) => formatTag(tag, locale)).join(" / "),
      est: estimatesByDifficulty[entry.difficulty],
      href: localizedPath(`/challenges/${entry.slug}`, locale),
      directory: `challenges/${entry.id}-${entry.slug}`,
      detail: details[entry.id]?.[locale],
    };
  });
}

export function getRunnableChallenges(locale: Locale = "en"): Challenge[] {
  return getChallenges(locale).filter((challenge) => challenge.status === "runnable");
}

export function getStages(locale: Locale = "en"): Stage[] {
  const localizedChallenges = getChallenges(locale);
  const stageNotes = stageNotesByLocale[locale];

  return stageOrder.map((track) => {
    const stage = stageNotes[track];
    const trackChallenges = localizedChallenges.filter(
      (challenge) => challenge.track === track,
    );

    return {
      track,
      name: stage.name,
      note: stage.note,
      total: trackChallenges.length,
      runnable: trackChallenges.filter((challenge) => challenge.status === "runnable")
        .length,
    };
  });
}

export function getLocalizedChallengeBySlug(
  slug: string,
  locale: Locale = "en",
): Challenge | undefined {
  return getChallenges(locale).find((challenge) => challenge.slug === slug);
}

function loadCatalog(): Catalog {
  const raw = load(readFileSync(catalogPath, "utf-8"));

  if (!isCatalog(raw)) {
    throw new Error(`Invalid challenge catalog: ${catalogPath}`);
  }

  return raw;
}

function loadDetails(): Record<string, Partial<Record<Locale, ChallengeDetail>>> {
  const raw = load(readFileSync(detailsPath, "utf-8"));

  if (!raw || typeof raw !== "object") {
    throw new Error(`Invalid challenge details: ${detailsPath}`);
  }

  const result: Record<string, Partial<Record<Locale, ChallengeDetail>>> = {};

  for (const [id, localized] of Object.entries(raw)) {
    if (!localized || typeof localized !== "object") {
      continue;
    }

    result[id] = {};
    for (const locale of ["en", "zh"] as const) {
      const detail = (localized as Record<string, unknown>)[locale];
      if (isChallengeDetail(detail)) {
        result[id][locale] = detail;
      }
    }
  }

  return result;
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

function isChallengeDetail(value: unknown): value is ChallengeDetail {
  if (!value || typeof value !== "object") {
    return false;
  }

  const detail = value as Partial<ChallengeDetail>;
  return (
    typeof detail.background === "string" &&
    typeof detail.objective === "string" &&
    typeof detail.input_contract === "string" &&
    typeof detail.output_contract === "string" &&
    typeof detail.scoring === "string" &&
    isPlainObject(detail.example_input) &&
    isPlainObject(detail.example_output) &&
    Array.isArray(detail.common_pitfalls) &&
    detail.common_pitfalls.every((item) => typeof item === "string") &&
    typeof detail.stretch_goal === "string"
  );
}

function isPlainObject(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}
