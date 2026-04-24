import { sitePath } from "./urls";

export const locales = ["en", "zh"] as const;
export type Locale = (typeof locales)[number];

export const defaultLocale: Locale = "en";

export const localeMeta: Record<Locale, { htmlLang: string; label: string }> = {
  en: {
    htmlLang: "en",
    label: "EN",
  },
  zh: {
    htmlLang: "zh-CN",
    label: "中文",
  },
};

export const layoutCopy: Record<
  Locale,
  {
    defaultDescription: string;
    tagline: string;
    nav: {
      path: string;
      challenges: string;
      scoring: string;
      contribute: string;
      github: string;
    };
    switchLanguage: string;
  }
> = {
  en: {
    defaultDescription: "Learn agent engineering by solving graded local challenges.",
    tagline: "Open-source agent training lab",
    nav: {
      path: "Path",
      challenges: "Challenges",
      scoring: "Scoring",
      contribute: "Contribute",
      github: "GitHub",
    },
    switchLanguage: "中文",
  },
  zh: {
    defaultDescription: "通过可评分的本地挑战学习智能体工程。",
    tagline: "开源智能体训练实验室",
    nav: {
      path: "路线",
      challenges: "题库",
      scoring: "评分",
      contribute: "贡献",
      github: "GitHub",
    },
    switchLanguage: "EN",
  },
};

export const stageNotesByLocale: Record<
  Locale,
  Record<string, { name: string; note: string }>
> = {
  en: {
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
  },
  zh: {
    foundations: {
      name: "基础能力",
      note: "指令遵循、结构化输出、稳定可复现行为。",
    },
    tools: {
      name: "工具调用",
      note: "工具选择、参数填写、重试与受控执行。",
    },
    rag: {
      name: "检索增强",
      note: "引用、来源忠实度、冲突证据处理。",
    },
    memory: {
      name: "记忆",
      note: "状态压缩、偏好记录、冲突处理。",
    },
    workflow: {
      name: "工作流",
      note: "路由、分阶段执行、失败恢复。",
    },
    safety: {
      name: "安全",
      note: "提示注入防御与信任边界。",
    },
    evaluation: {
      name: "评测",
      note: "评分器、回归套件、轨迹检查。",
    },
    capstone: {
      name: "综合项目",
      note: "带真实约束的完整智能体系统。",
    },
  },
};

export const difficultyLabels: Record<Locale, Record<string, string>> = {
  en: {
    easy: "easy",
    medium: "medium",
    hard: "hard",
    expert: "expert",
  },
  zh: {
    easy: "入门",
    medium: "进阶",
    hard: "困难",
    expert: "专家",
  },
};

export const statusLabels: Record<Locale, Record<string, string>> = {
  en: {
    runnable: "runnable",
    planned: "planned",
  },
  zh: {
    runnable: "可运行",
    planned: "规划中",
  },
};

export const tagLabelsZh: Record<string, string> = {
  "adversarial": "对抗样本",
  "approval": "人工审批",
  "budgeting": "预算约束",
  "capstone": "综合项目",
  "citations": "引用",
  "classification": "分类",
  "conflicts": "冲突处理",
  "context": "上下文",
  "deterministic": "确定性",
  "escalation": "人工升级",
  "evaluation": "评测",
  "explanation": "解释",
  "extraction": "抽取",
  "forms": "表单",
  "grading": "评分",
  "handoff": "交接",
  "instruction-following": "指令遵循",
  "memory": "记忆",
  "multi-agent": "多智能体",
  "planning": "规划",
  "preferences": "偏好",
  "prompt-injection": "提示注入",
  "prompts": "提示词",
  "rag": "检索增强",
  "react": "ReAct",
  "regression": "回归测试",
  "research": "研究",
  "retries": "重试",
  "routing": "路由",
  "rubrics": "评分标准",
  "safety": "安全",
  "state": "状态",
  "structured-output": "结构化输出",
  "summarization": "摘要",
  "support": "客服",
  "testing": "测试",
  "tools": "工具",
  "traces": "轨迹",
  "workflow": "工作流",
};

export const challengeZh: Record<string, { title: string; summary: string }> = {
  "001": {
    title: "复读智能体",
    summary: "原样返回给定事实，不添加新事实。",
  },
  "002": {
    title: "只输出 JSON",
    summary: "把任务抽取为严格的 JSON 对象。",
  },
  "003": {
    title: "工具选择器",
    summary: "根据用户请求选择正确的模拟工具。",
  },
  "004": {
    title: "计算器智能体",
    summary: "使用确定性计算器工具，而不是猜答案。",
  },
  "005": {
    title: "工单分诊",
    summary: "用稳定标签对客服工单进行分类。",
  },
  "006": {
    title: "迷你 RAG",
    summary: "基于小型文档集回答问题，并提供引用。",
  },
  "007": {
    title: "上下文瘦身",
    summary: "压缩噪声上下文，同时保留任务关键事实。",
  },
  "008": {
    title: "工具错误恢复",
    summary: "从工具错误和空结果中恢复。",
  },
  "009": {
    title: "轻量个人记忆",
    summary: "使用小型偏好记忆，同时避免泄露无关状态。",
  },
  "010": {
    title: "两步研究员",
    summary: "先检索证据，再只基于证据回答。",
  },
  "011": {
    title: "提示路由器",
    summary: "把请求路由到专门的提示路径。",
  },
  "012": {
    title: "表单填写智能体",
    summary: "填写结构化字段，并在必填信息缺失时追问。",
  },
  "013": {
    title: "注入防御 I",
    summary: "把恶意检索文本当作数据，而不是指令。",
  },
  "014": {
    title: "单元测试解释器",
    summary: "解释测试失败，同时不编造代码行为。",
  },
  "015": {
    title: "带审批的邮件助手",
    summary: "起草需要人工确认的邮件操作。",
  },
  "016": {
    title: "会议记忆",
    summary: "根据会议笔记更新记忆，避免复制过期事实。",
  },
  "017": {
    title: "评测框架基础",
    summary: "检查一个简单的确定性评分器和评测框架。",
  },
  "018": {
    title: "ReAct 轨迹审计",
    summary: "审计推理/行动轨迹中的工具使用错误。",
  },
  "019": {
    title: "多工具规划器",
    summary: "规划并执行有边界的多工具工作流。",
  },
  "020": {
    title: "冲突来源 RAG",
    summary: "带引用地处理相互冲突的检索证据。",
  },
  "021": {
    title: "长流程工作流",
    summary: "在分阶段工作流中持久化进度。",
  },
  "022": {
    title: "记忆冲突解析器",
    summary: "用新的偏好证据解析旧记忆中的冲突。",
  },
  "023": {
    title: "人工升级智能体",
    summary: "把模糊或高风险请求升级给人类处理。",
  },
  "024": {
    title: "回归评测套件",
    summary: "为智能体行为构建小型回归测试套件。",
  },
  "025": {
    title: "智能体裁判校准",
    summary: "用确定性检查校准基于评分标准的判断。",
  },
  "026": {
    title: "注入防御 II",
    summary: "防御跨多步骤工具结果注入。",
  },
  "027": {
    title: "多智能体交接",
    summary: "协调专业智能体之间的任务交接。",
  },
  "028": {
    title: "预算感知智能体",
    summary: "在时间、工具和成本预算下选择行动。",
  },
  "029": {
    title: "对抗式 RAG 挑战",
    summary: "基于带对抗性的检索上下文忠实回答。",
  },
  "030": {
    title: "综合客服智能体",
    summary: "把路由、工具、RAG、记忆和升级整合进一个客服任务。",
  },
};

export function localizedPath(path: string, locale: Locale): string {
  const normalized = path.startsWith("/") ? path : `/${path}`;

  if (locale === defaultLocale) {
    return sitePath(normalized);
  }

  if (normalized === "/") {
    return sitePath("/zh");
  }

  return sitePath(`/zh${normalized}`);
}

export function oppositeLocale(locale: Locale): Locale {
  return locale === "zh" ? "en" : "zh";
}

export function formatTag(value: string, locale: Locale): string {
  if (locale === "zh") {
    return tagLabelsZh[value] ?? value;
  }

  return value
    .split("-")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}
