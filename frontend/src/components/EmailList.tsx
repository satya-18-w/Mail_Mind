"use client";

import type { Email } from "@/types";
import { EmailCard } from "./EmailCard";
import { Mail } from "lucide-react";

interface EmailListProps {
    emails: Email[];
    selectedEmail: Email | null;
    onSelectEmail: (email: Email) => void;
    isLoading: boolean;
}

export function EmailList({
    emails,
    selectedEmail,
    onSelectEmail,
    isLoading,
}: EmailListProps) {
    if (isLoading) {
        return (
            <div className="mail-list-scroll h-full min-h-0 overflow-y-auto overscroll-contain">
                {Array.from({ length: 6 }).map((_, i) => (
                    <div key={i} className="px-4 py-4 border-b border-slate-100 animate-fade-in" style={{ animationDelay: `${i * 60}ms` }}>
                        <div className="flex items-start gap-3">
                            <div className="skeleton w-9 h-9 rounded-full shrink-0" />
                            <div className="flex-1 space-y-2">
                                <div className="skeleton h-4 w-3/4" />
                                <div className="skeleton h-3 w-full" />
                                <div className="skeleton h-3 w-1/2" />
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        );
    }

    if (emails.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center h-full text-slate-400 gap-3">
                <div className="w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center">
                    <Mail className="w-6 h-6 text-slate-300" />
                </div>
                <p className="text-sm">No emails found</p>
            </div>
        );
    }

    return (
        <div className="mail-list-scroll h-full min-h-0 overflow-y-auto overscroll-contain">
            {emails.map((email, i) => (
                <div key={email.id} className="animate-fade-in" style={{ animationDelay: `${i * 30}ms` }}>
                    <EmailCard
                        email={email}
                        onClick={onSelectEmail}
                        isSelected={selectedEmail?.id === email.id}
                    />
                </div>
            ))}
        </div>
    );
}
