"use client";

import type { StatsOverview } from "@/types";
import { Mail, MailOpen, AlertTriangle, Calendar, Star } from "lucide-react";

const stats = [
    {
        key: "total" as const,
        label: "Total Emails",
        icon: Mail,
        gradient: "from-blue-500 to-blue-600",
        bg: "bg-blue-50",
        text: "text-blue-700",
    },
    {
        key: "unread" as const,
        label: "Unread",
        icon: MailOpen,
        gradient: "from-amber-500 to-orange-500",
        bg: "bg-amber-50",
        text: "text-amber-700",
    },
    {
        key: "high_priority" as const,
        label: "High Priority",
        icon: AlertTriangle,
        gradient: "from-rose-500 to-red-600",
        bg: "bg-rose-50",
        text: "text-rose-700",
    },
    {
        key: "deadlines" as const,
        label: "Deadlines",
        icon: Calendar,
        gradient: "from-violet-500 to-purple-600",
        bg: "bg-violet-50",
        text: "text-violet-700",
    },
    {
        key: "starred" as const,
        label: "Starred",
        icon: Star,
        gradient: "from-emerald-500 to-teal-600",
        bg: "bg-emerald-50",
        text: "text-emerald-700",
    },
];

interface StatsCardsProps {
    data: StatsOverview | undefined;
    isLoading: boolean;
}

export function StatsCards({ data, isLoading }: StatsCardsProps) {
    return (
        <div className="grid grid-cols-5 gap-3 px-6 py-4">
            {stats.map((stat, i) => (
                <div
                    key={stat.key}
                    className="bg-white rounded-xl border border-slate-100 p-4 card-hover animate-fade-in"
                    style={{ animationDelay: `${i * 60}ms` }}
                >
                    <div className="flex items-center justify-between mb-3">
                        <div
                            className={`w-9 h-9 rounded-lg bg-linear-to-br ${stat.gradient} flex items-center justify-center shadow-sm`}
                        >
                            <stat.icon className="w-4.5 h-4.5 text-white" />
                        </div>
                    </div>
                    <div className="animate-count-up" style={{ animationDelay: `${i * 100 + 200}ms` }}>
                        {isLoading ? (
                            <div className="skeleton h-7 w-12 mb-1" />
                        ) : (
                            <p className="text-2xl font-bold text-slate-900">
                                {data?.[stat.key] ?? 0}
                            </p>
                        )}
                    </div>
                    <p className="text-xs text-slate-500 mt-0.5">{stat.label}</p>
                </div>
            ))}
        </div>
    );
}
