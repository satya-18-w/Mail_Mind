"use client";

import { clsx } from "clsx";
import { ArrowUp, ArrowRight, ArrowDown } from "lucide-react";

const priorityConfig: Record<string, { style: string; icon: React.ElementType }> = {
    HIGH: {
        style: "bg-red-50 text-red-700 border-red-200",
        icon: ArrowUp,
    },
    MEDIUM: {
        style: "bg-amber-50 text-amber-700 border-amber-200",
        icon: ArrowRight,
    },
    LOW: {
        style: "bg-emerald-50 text-emerald-700 border-emerald-200",
        icon: ArrowDown,
    },
};

export function PriorityBadge({ priority }: { priority: string | null }) {
    if (!priority) return null;

    const config = priorityConfig[priority] || {
        style: "bg-slate-50 text-slate-700 border-slate-200",
        icon: ArrowRight,
    };
    const Icon = config.icon;

    return (
        <span
            className={clsx(
                "inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] font-semibold border",
                config.style
            )}
        >
            <Icon className="w-3 h-3" />
            {priority}
        </span>
    );
}
