const rawBase = import.meta.env.BASE_URL || "/";
const basePath = rawBase.endsWith("/") ? rawBase.slice(0, -1) : rawBase;

export function sitePath(path: string): string {
  const normalized = path.startsWith("/") ? path : `/${path}`;

  if (normalized === "/") {
    return basePath ? `${basePath}/` : "/";
  }

  return `${basePath}${normalized}`;
}
