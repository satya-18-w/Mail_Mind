"use client";

import type { User } from "@/types";
import { Mail, ShieldCheck } from "lucide-react";

interface ProfileSectionProps {
    user: User | null;
}

export function ProfileSection({ user }: ProfileSectionProps) {
    if (!user) return null;

    const initials = (user.name || "User")
        .split(" ")
        .filter(Boolean)
        .map((part) => part[0]?.toUpperCase() ?? "")
        .join("")
        .slice(0, 2);

    return (
        <section className="px-6 pt-4 pb-3 border-b border-slate-200/60 bg-white/60">
            <div className="rounded-2xl border border-slate-200 bg-linear-to-r from-slate-50 to-white p-4 shadow-xs">
                <div className="flex items-center gap-4">
                    {user.picture ? (
                        <img
                            src={user.picture}
                            alt={user.name}
                            className="h-12 w-12 rounded-full ring-2 ring-white shadow"
                            referrerPolicy="no-referrer"
                        />
                    ) : (
                        <div className="h-12 w-12 rounded-full bg-linear-to-br from-indigo-600 to-violet-600 text-white text-sm font-bold flex items-center justify-center">
                            {initials}
                        </div>
                    )}

                    <div className="min-w-0 flex-1">
                        <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                            Logged in account
                        </p>
                        <p className="text-base font-semibold text-slate-900 truncate">{user.name}</p>
                        <p className="text-sm text-slate-600 truncate flex items-center gap-1.5">
                            <Mail className="h-3.5 w-3.5 shrink-0" />
                            {user.email}
                        </p>
                    </div>

                    <div className="hidden sm:flex items-center gap-1.5 text-xs font-medium text-emerald-700 bg-emerald-50 border border-emerald-100 rounded-full px-2.5 py-1">
                        <ShieldCheck className="h-3.5 w-3.5" />
                        Connected
                    </div>
                </div>
            </div>
        </section>
    );
}
