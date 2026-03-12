import type { Email, User, CategoryStat, PriorityStat, StatsOverview, Task, SearchResult, PipelineStatus } from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
const AUTH_BASE = process.env.NEXT_PUBLIC_AUTH_URL || "http://localhost:8000";

function getToken(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("token");
}

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
    const token = getToken();
    const headers: Record<string, string> = {
        "Content-Type": "application/json",
    };
    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }
    const res = await fetch(`${API_BASE}${path}`, {
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

export const api = {
    // Auth
    getGoogleLoginUrl: () => `${AUTH_BASE}/auth/google/login`,

    getMe: () => {
        const token = getToken();
        return fetch(`${AUTH_BASE}/auth/me`, {
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
    triggerPipeline: () =>
        apiFetch<PipelineStatus>("/pipeline/run", { method: "POST" }),
};
