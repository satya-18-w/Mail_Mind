import type {
    Email,
    User,
    CategoryStat,
    PriorityStat,
    StatsOverview,
    Task,
    SearchResult,
    PipelineStatus,
    PipelineRun,
} from "@/types";

type TriggerPipelinePayload = {
    limit: number;
};

type PipelineStreamHandlers = {
    onMessage: (run: PipelineRun) => void;
    onError?: (error: unknown) => void;
};

function stripTrailingSlash(url: string): string {
    return url.endsWith("/") ? url.slice(0, -1) : url;
}

type RuntimeConfig = {
    authUrl?: string;
    apiUrl?: string;
};

const DEFAULT_PROD_BACKEND_URL = "https://mailmind-production-38fb.up.railway.app";

function isLocalHost(hostname: string): boolean {
    return hostname === "localhost" || hostname === "127.0.0.1";
}

function inBrowserLocalDev(): boolean {
    if (typeof window === "undefined") return false;
    return isLocalHost(window.location.hostname);
}

function getRuntimeConfig(): RuntimeConfig | null {
    if (typeof window === "undefined") return null;
    const runtime = (window as Window & { __MAILMIND_CONFIG__?: RuntimeConfig }).__MAILMIND_CONFIG__;
    return runtime ?? null;
}

function authBaseFromApiBase(apiBase: string): string {
    return apiBase.replace(/\/api(?:\/v1)?$/, "");
}

function resolveAuthBase(): string {
    const runtime = getRuntimeConfig();
    const rawUrl = runtime?.authUrl || process.env.NEXT_PUBLIC_AUTH_URL || runtime?.apiUrl || process.env.NEXT_PUBLIC_API_URL;

    if (rawUrl && rawUrl.startsWith("http")) {
        const trimmed = stripTrailingSlash(rawUrl);
        return authBaseFromApiBase(trimmed);
    }

    if (inBrowserLocalDev()) {
        return "http://localhost:8000";
    }

    return DEFAULT_PROD_BACKEND_URL;
}

function resolveApiBase(authBase: string): string {
    const runtime = getRuntimeConfig();
    // If the runtime or env explicitly has a URL ending in /api or /api/v1, use it.
    const rawApiUrl = runtime?.apiUrl || process.env.NEXT_PUBLIC_API_URL;
    if (rawApiUrl && rawApiUrl.startsWith("http") && /\/api(?:\/v1)?$/.test(rawApiUrl)) {
        return stripTrailingSlash(rawApiUrl);
    }

    // Otherwise, build it from the resolved auth base (the root).
    if (authBase) {
        return `${stripTrailingSlash(authBase)}/api/v1`;
    }

    if (inBrowserLocalDev()) {
        return "http://localhost:8000/api/v1";
    }

    return `${DEFAULT_PROD_BACKEND_URL}/api/v1`;
}

function getAuthBase(): string {
    return resolveAuthBase();
}

function getApiBase(): string {
    const authBase = getAuthBase();
    return resolveApiBase(authBase);
}

function getToken(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("token");
}

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
    const token = getToken();
    const apiBase = getApiBase();
    const headers: Record<string, string> = {
        "Content-Type": "application/json",
    };
    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }
    const res = await fetch(`${apiBase}${path}`, {
        headers,
        ...options,
    });
    if (res.status === 401) {
        if (typeof window !== "undefined") {
            localStorage.removeItem("token");
            window.location.href = "/login";
        }
        throw new Error("Unauthorized");
    }
    if (!res.ok) {
        throw new Error(`API error: ${res.status} ${res.statusText}`);
    }
    return res.json();
}

function parseSseEventChunk(chunk: string): PipelineRun | null {
    const lines = chunk.split("\n");
    let data = "";

    for (const line of lines) {
        if (line.startsWith("data:")) {
            data += `${line.slice(5).trim()}\n`;
        }
    }

    const trimmed = data.trim();
    if (!trimmed) return null;
    return JSON.parse(trimmed) as PipelineRun;
}

export const api = {
    // Auth
    getGoogleLoginUrl: () => {
        const authBase = getAuthBase();
        if (typeof window === "undefined") return `${authBase}/auth/google/login`;
        const frontend = encodeURIComponent(window.location.origin);
        return `${authBase}/auth/google/login?frontend=${frontend}`;
    },

    getMe: () => {
        const token = getToken();
        const authBase = getAuthBase();
        return fetch(`${authBase}/auth/me`, {
            headers: token ? { Authorization: `Bearer ${token}` } : {},
        }).then((res) => {
            if (!res.ok) throw new Error("Not authenticated");
            return res.json() as Promise<User>;
        });
    },

    // Emails
    getEmails: (limit = 50, offset = 0) =>
        apiFetch<Email[]>(`/emails?limit=${limit}&offset=${offset}`),

    getEmail: (id: number) =>
        apiFetch<Email>(`/emails/${id}`),

    markAsRead: (id: number) =>
        apiFetch<Email>(`/emails/${id}/read`, { method: "PATCH" }),

    toggleStar: (id: number) =>
        apiFetch<Email>(`/emails/${id}/star`, { method: "PATCH" }),

    getStarredEmails: (limit = 50) =>
        apiFetch<Email[]>(`/emails/starred?limit=${limit}`),

    getEmailsByCategory: (category: string, limit = 50) =>
        apiFetch<Email[]>(`/emails/category/${encodeURIComponent(category)}?limit=${limit}`),

    getEmailsByPriority: (priority: string, limit = 50) =>
        apiFetch<Email[]>(`/emails/priority/${encodeURIComponent(priority)}?limit=${limit}`),

    getDeadlines: (limit = 50) =>
        apiFetch<Email[]>(`/emails/deadlines/upcoming?limit=${limit}`),

    searchEmails: (query: string, limit = 10) =>
        apiFetch<SearchResult>("/emails/search", {
            method: "POST",
            body: JSON.stringify({ query, limit }),
        }),

    // Stats
    getStatsOverview: () =>
        apiFetch<StatsOverview>("/stats/overview"),

    getCategoryStats: () =>
        apiFetch<CategoryStat[]>("/stats/categories"),

    getPriorityStats: () =>
        apiFetch<PriorityStat[]>("/stats/priorities"),

    // Tasks
    getTasks: () =>
        apiFetch<Task[]>("/tasks"),

    // Pipeline
    triggerPipeline: ({ limit }: TriggerPipelinePayload) =>
        apiFetch<PipelineStatus>("/pipeline/run", {
            method: "POST",
            body: JSON.stringify({ limit }),
        }),

    getLatestPipelineRun: () =>
        apiFetch<PipelineRun>("/pipeline/runs/latest"),

    getPipelineRun: (runId: number) =>
        apiFetch<PipelineRun>(`/pipeline/runs/${runId}`),

    streamLatestPipelineRun: ({ onMessage, onError }: PipelineStreamHandlers) => {
        const controller = new AbortController();

        const run = async () => {
            const token = getToken();
            if (!token) {
                throw new Error("Unauthorized");
            }

            const response = await fetch(`${getApiBase()}/pipeline/runs/stream`, {
                method: "GET",
                headers: {
                    Authorization: `Bearer ${token}`,
                    Accept: "text/event-stream",
                },
                signal: controller.signal,
                cache: "no-store",
            });

            if (!response.ok || !response.body) {
                throw new Error(`Pipeline stream failed: ${response.status}`);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = "";

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const events = buffer.split("\n\n");
                buffer = events.pop() ?? "";

                for (const eventChunk of events) {
                    if (!eventChunk.trim() || eventChunk.startsWith(":")) {
                        continue;
                    }
                    const payload = parseSseEventChunk(eventChunk);
                    if (payload) {
                        onMessage(payload);
                    }
                }
            }
        };

        run().catch((error) => {
            if (!controller.signal.aborted) {
                onError?.(error);
            }
        });

        return () => controller.abort();
    },
};
