"use client";

import { useEffect } from "react";
import type { Email } from "@/types";
import { PriorityBadge } from "./PriorityBadge";
import { DeadlineAlert } from "./DeadlineAlert";
import { X, Clock, Tag, FileText, CheckCircle, Star, ArrowLeft } from "lucide-react";
import { useMarkAsRead, useToggleStar } from "@/hooks/useEmails";

interface EmailDetailPanelProps {
    email: Email | null;
    onClose: () => void;
}

function getInitials(name: string): string {
    return name
        .split(/[\s@]+/)
        .slice(0, 2)
        .map((w) => w[0]?.toUpperCase() ?? "")
        .join("");
}

export function EmailDetailPanel({ email, onClose }: EmailDetailPanelProps) {
    const markAsRead = useMarkAsRead();
    const toggleStar = useToggleStar();

    useEffect(() => {
        if (email && !email.is_read) {
            markAsRead.mutate(email.id);
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [email?.id]);

    if (!email) {
        return (
            <div className="flex flex-col items-center justify-center h-full text-slate-400 gap-3">
                <FileText className="w-12 h-12 text-slate-200" />
                <p className="text-sm">Select an email to view details</p>
            </div>
        );
    }

    return (
        <div className="h-full overflow-y-auto animate-fade-in">
            {/* Header */}
            <div className="sticky top-0 bg-white/80 backdrop-blur-md border-b border-slate-100 px-6 py-4 z-10">
                <div className="flex items-center justify-between gap-3">
                    <button
                        onClick={onClose}
                        className="p-1.5 hover:bg-slate-100 rounded-lg transition-colors text-slate-400 hover:text-slate-600"
                    >
                        <ArrowLeft className="w-4 h-4" />
                    </button>
                    <div className="flex items-center gap-2">
                        <button
                            onClick={() => toggleStar.mutate(email.id)}
                            className={`p-1.5 rounded-lg transition-colors ${email.is_starred
                                ? "text-amber-400 hover:bg-amber-50"
                                : "text-slate-300 hover:bg-slate-100 hover:text-amber-400"
                                }`}
                        >
                            <Star
                                className={`w-4 h-4 ${email.is_starred ? "fill-amber-400" : ""}`}
                            />
                        </button>
                        <button
                            onClick={onClose}
                            className="p-1.5 hover:bg-slate-100 rounded-lg transition-colors text-slate-400 hover:text-slate-600"
                        >
                            <X className="w-4 h-4" />
                        </button>
                    </div>
                </div>

                <h2 className="text-lg font-semibold text-slate-900 mt-3 leading-snug">
                    {email.subject}
                </h2>

                <div className="flex flex-wrap items-center gap-2 mt-2">
                    <PriorityBadge priority={email.priority} />
                    {email.category && (
                        <span className="inline-flex items-center gap-1 text-xs font-medium text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
                            <Tag className="w-3 h-3" />
                            {email.category}
                            {email.subcategory && ` / ${email.subcategory}`}
                        </span>
                    )}
                    {email.is_read && (
                        <span className="inline-flex items-center gap-1 text-xs text-emerald-600">
                            <CheckCircle className="w-3 h-3" />
                            Read
                        </span>
                    )}
                </div>
            </div>

            <div className="px-6 py-5 space-y-5">
                {/* Sender card */}
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-linear-to-br from-indigo-400 to-violet-400 flex items-center justify-center text-white text-sm font-semibold shrink-0">
                        {getInitials(email.sender)}
                    </div>
                    <div className="min-w-0">
                        <p className="text-sm font-semibold text-slate-800 truncate">
                            {email.sender.split("<")[0].trim()}
                        </p>
                        <p className="text-xs text-slate-400 flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {new Date(email.timestamp).toLocaleString()}
                        </p>
                    </div>
                </div>

                {/* Deadline */}
                {email.deadline && <DeadlineAlert deadline={email.deadline} />}

                {/* AI Summary */}
                {email.summary && (
                    <div className="rounded-xl bg-linear-to-br from-indigo-50 to-violet-50 border border-indigo-100/50 p-4">
                        <div className="flex items-center gap-2 text-sm font-semibold text-indigo-700 mb-2">
                            <FileText className="w-4 h-4" />
                            AI Summary
                        </div>
                        <p className="text-sm text-indigo-800/80 leading-relaxed">
                            {email.summary}
                        </p>
                    </div>
                )}

                {/* Email Body */}
                <div>
                    <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                        Email Body
                    </h3>
                    <div className="bg-slate-50 rounded-xl p-4 text-sm text-slate-700 whitespace-pre-wrap leading-relaxed border border-slate-100">
                        {email.body}
                    </div>
                </div>
            </div>
        </div>
    );
}
