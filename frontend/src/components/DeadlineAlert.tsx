"use client";

import { AlertTriangle, Clock } from "lucide-react";
import { clsx } from "clsx";

interface DeadlineAlertProps {
    deadline: string | null;
    compact?: boolean;
}

export function DeadlineAlert({ deadline, compact = false }: DeadlineAlertProps) {
    if (!deadline) return null;

    const deadlineDate = new Date(deadline);
    const now = new Date();
    const daysLeft = Math.ceil(
        (deadlineDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24)
    );

    const isUrgent = daysLeft <= 3;
    const isPast = daysLeft < 0;

    if (compact) {
        return (
            <span
                className={clsx(
                    "inline-flex items-center gap-1 text-[10px] font-medium px-1.5 py-0.5 rounded",
                    isPast
                        ? "bg-red-100 text-red-700"
                        : isUrgent
                            ? "bg-orange-100 text-orange-700"
                            : "bg-blue-100 text-blue-700"
                )}
            >
                <Clock className="w-2.5 h-2.5" />
                {isPast ? "Overdue" : daysLeft === 0 ? "Today" : `${daysLeft}d`}
            </span>
        );
    }

    return (
        <div
            className={clsx(
                "flex items-center gap-2 px-3 py-2 rounded-lg text-sm",
                isPast
                    ? "bg-red-50 text-red-700 border border-red-100"
                    : isUrgent
                        ? "bg-orange-50 text-orange-700 border border-orange-100"
                        : "bg-blue-50 text-blue-700 border border-blue-100"
            )}
        >
            <AlertTriangle className="w-4 h-4 shrink-0" />
            <span className="font-medium">
                {isPast
                    ? `Overdue (${deadline})`
                    : daysLeft === 0
                        ? `Due today`
                        : `Due in ${daysLeft} day${daysLeft > 1 ? "s" : ""} (${deadline})`}
            </span>
        </div>
    );
}
