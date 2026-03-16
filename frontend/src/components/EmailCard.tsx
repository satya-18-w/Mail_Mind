"use client";

import type { Email } from "@/types";
import { PriorityBadge } from "./PriorityBadge";
import { DeadlineAlert } from "./DeadlineAlert";
import { Star } from "lucide-react";
import { useToggleStar } from "@/hooks/useEmails";

interface EmailCardProps {
    email: Email;
    onClick: (email: Email) => void;
    isSelected: boolean;
}

const CATEGORY_COLORS: Record<string, string> = {
    work: "bg-blue-100 text-blue-700",
    personal: "bg-emerald-100 text-emerald-700",
    finance: "bg-violet-100 text-violet-700",
    updates: "bg-sky-100 text-sky-700",
    promotions: "bg-amber-100 text-amber-700",
    social: "bg-pink-100 text-pink-700",
};

function timeAgo(date: Date): string {
    const seconds = Math.floor((Date.now() - date.getTime()) / 1000);
    if (seconds < 60) return "just now";
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h`;
    const days = Math.floor(hours / 24);
    if (days < 7) return `${days}d`;
    return date.toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

function getInitials(name: string): string {
    return name
        .split(/[\s@]+/)
        .slice(0, 2)
        .map((w) => w[0]?.toUpperCase() ?? "")
        .join("");
}

export function EmailCard({ email, onClick, isSelected }: EmailCardProps) {
    const toggleStar = useToggleStar();

    const handleStar = (e: React.MouseEvent) => {
        e.stopPropagation();
        toggleStar.mutate(email.id);
    };

    const catClass =
        CATEGORY_COLORS[email.category?.toLowerCase() ?? ""] ??
        "bg-slate-100 text-slate-600";

    return (
        <div
            onClick={() => onClick(email)}
            className={`group relative p-3 sm:p-4 cursor-pointer transition-all duration-200 border-b border-slate-100 hover:bg-slate-50 ${isSelected
                ? "bg-indigo-50/60 border-l-[3px] border-l-indigo-500"
                : "border-l-[3px] border-l-transparent"
                }`}
        >
            <div className="flex items-start gap-3">
                {/* Avatar */}
                <div className="relative shrink-0">
                    <div className="w-9 h-9 rounded-full bg-linear-to-br from-indigo-400 to-violet-400 flex items-center justify-center text-white text-xs font-semibold">
                        {getInitials(email.sender)}
                    </div>
                    {!email.is_read && (
                        <span className="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 bg-indigo-500 rounded-full ring-2 ring-white" />
                    )}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-2">
                        <span
                            className={`text-sm truncate ${!email.is_read
                                ? "font-semibold text-slate-900"
                                : "font-medium text-slate-500"
                                }`}
                        >
                            {email.sender.split("<")[0].trim()}
                        </span>
                        <span className="text-[11px] text-slate-400 shrink-0">
                            {timeAgo(new Date(email.timestamp))}
                        </span>
                    </div>

                    <h3
                        className={`text-sm truncate mt-0.5 ${!email.is_read ? "font-semibold text-slate-800" : "text-slate-600"
                            }`}
                    >
                        {email.subject}
                    </h3>

                    {email.summary && (
                        <p className="text-xs text-slate-400 truncate mt-0.5">
                            {email.summary}
                        </p>
                    )}

                    {/* Tags row */}
                    <div className="flex items-center gap-1.5 mt-2 flex-wrap">
                        <PriorityBadge priority={email.priority} />
                        {email.category && (
                            <span
                                className={`text-[10px] font-medium px-1.5 py-0.5 rounded ${catClass}`}
                            >
                                {email.category}
                            </span>
                        )}
                        {email.deadline && <DeadlineAlert deadline={email.deadline} compact />}
                    </div>
                </div>

                {/* Star */}
                <button
                    onClick={handleStar}
                    className={`shrink-0 p-1 rounded-md transition-all ${email.is_starred
                        ? "text-amber-400"
                        : "text-slate-300 opacity-100 md:opacity-0 md:group-hover:opacity-100"
                        } hover:text-amber-400`}
                >
                    <Star
                        className={`w-4 h-4 ${email.is_starred ? "fill-amber-400" : ""}`}
                    />
                </button>
            </div>
        </div>
    );
}
