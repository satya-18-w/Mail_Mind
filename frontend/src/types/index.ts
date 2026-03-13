export interface Email {
    id: number;
    gmail_id: string;
    sender: string;
    subject: string;
    body: string;
    category: string | null;
    subcategory: string | null;
    priority: string | null;
    deadline: string | null;
    summary: string | null;
    timestamp: string;
    is_read: boolean;
    is_starred: boolean;
}

export interface User {
    id: number;
    email: string;
    name: string;
    picture: string | null;
}

export interface CategoryStat {
    name: string;
    count: number;
}

export interface PriorityStat {
    name: string;
    count: number;
}

export interface StatsOverview {
    total: number;
    unread: number;
    high_priority: number;
    deadlines: number;
    starred: number;
}

export interface Task {
    id: number;
    email_id: number;
    deadline: string | null;
    status: string;
    priority: string | null;
}

export interface SearchResult {
    emails: Email[];
}

export interface PipelineStatus {
    status: string;
    run_id?: number | null;
    processed: number;
    message: string;
}

export interface PipelineRun {
    id: number;
    status: "QUEUED" | "RUNNING" | "COMPLETED" | "FAILED";
    fetched_count: number;
    processed_count: number;
    skipped_count: number;
    failed_count: number;
    started_at: string | null;
    finished_at: string | null;
    error_message: string | null;
    created_at: string;
}

export interface TokenResponse {
    access_token: string;
    user: User;
}
