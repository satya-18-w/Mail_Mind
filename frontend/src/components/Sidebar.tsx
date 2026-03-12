"use client";

import { clsx } from "clsx";
import type { CategoryStat } from "@/types";
import {
    Building2,
    GraduationCap,
    Linkedin,
    Users,
    ShoppingBag,
    UserCircle,
    AlertTriangle,
    Calendar,
    Inbox,
    Star,
    Brain,
    LogOut,
} from "lucide-react";

const categoryIcons: Record<string, React.ElementType> = {
    Institute: Building2,
    Professor: GraduationCap,
    LinkedIn: Linkedin,
    Society: Users,
    Promotion: ShoppingBag,
    Personal: UserCircle,
};

const categoryColors: Record<string, string> = {
    Institute: "bg-blue-500",
    Professor: "bg-emerald-500",
    LinkedIn: "bg-sky-500",
    Society: "bg-violet-500",
    Promotion: "bg-amber-500",
    Personal: "bg-pink-500",
};

interface SidebarProps {
    categories: CategoryStat[];
    selectedCategory: string | null;
    selectedPriority: string | null;
    selectedView: string;
    onSelectCategory: (category: string | null) => void;
    onSelectPriority: (priority: string | null) => void;
    onSelectView: (view: string) => void;
    unreadCount?: number;
    starredCount?: number;
    onLogout?: () => void;
}

export function Sidebar({
    categories,
    selectedCategory,
    selectedPriority,
    selectedView,
    onSelectCategory,
    onSelectPriority,
    onSelectView,
    unreadCount = 0,
    starredCount = 0,
    onLogout,
}: SidebarProps) {
    return (
        <aside className="w-64 bg-linear-to-b from-slate-900 to-slate-800 h-full overflow-y-auto flex flex-col">
            {/* Logo */}
            <div className="p-5 pb-4">
                <div className="flex items-center gap-2.5">
                    <div className="w-9 h-9 rounded-xl bg-linear-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
                        <Brain className="w-5 h-5 text-white" />
                    </div>
                    <div>
                        <h1 className="text-base font-bold text-white leading-tight">MailMind</h1>
                        <p className="text-xs text-slate-400">AI Email Intelligence</p>
                    </div>
                </div>
            </div>

            {/* Views */}
            <div className="px-3 py-2">
                <h2 className="px-3 text-[10px] font-semibold text-slate-500 uppercase tracking-widest mb-2">
                    Views
                </h2>
                <nav className="space-y-0.5">
                    <SidebarItem
                        icon={Inbox}
                        label="All Emails"
                        isActive={selectedView === "all"}
                        badge={unreadCount > 0 ? unreadCount : undefined}
                        badgeColor="bg-indigo-500"
                        onClick={() => {
                            onSelectView("all");
                            onSelectCategory(null);
                            onSelectPriority(null);
                        }}
                    />
                    <SidebarItem
                        icon={AlertTriangle}
                        label="High Priority"
                        isActive={selectedView === "high-priority"}
                        accentColor="text-rose-400"
                        onClick={() => {
                            onSelectView("high-priority");
                            onSelectCategory(null);
                            onSelectPriority("HIGH");
                        }}
                    />
                    <SidebarItem
                        icon={Calendar}
                        label="Deadlines"
                        isActive={selectedView === "deadlines"}
                        accentColor="text-amber-400"
                        onClick={() => {
                            onSelectView("deadlines");
                            onSelectCategory(null);
                            onSelectPriority(null);
                        }}
                    />
                    <SidebarItem
                        icon={Star}
                        label="Starred"
                        isActive={selectedView === "starred"}
                        badge={starredCount > 0 ? starredCount : undefined}
                        badgeColor="bg-amber-500"
                        accentColor="text-amber-400"
                        onClick={() => {
                            onSelectView("starred");
                            onSelectCategory(null);
                            onSelectPriority(null);
                        }}
                    />
                </nav>
            </div>

            {/* Categories */}
            <div className="px-3 py-2 mt-1 flex-1">
                <h2 className="px-3 text-[10px] font-semibold text-slate-500 uppercase tracking-widest mb-2">
                    Categories
                </h2>
                <nav className="space-y-0.5">
                    {categories.map((cat) => {
                        const Icon = categoryIcons[cat.name] || UserCircle;
                        const dotColor = categoryColors[cat.name] || "bg-slate-500";
                        return (
                            <button
                                key={cat.name}
                                onClick={() => {
                                    onSelectView("category");
                                    onSelectCategory(cat.name);
                                    onSelectPriority(null);
                                }}
                                className={clsx(
                                    "w-full flex items-center justify-between px-3 py-2 text-sm rounded-lg transition-all duration-150",
                                    selectedCategory === cat.name
                                        ? "bg-white/10 text-white sidebar-active"
                                        : "text-slate-400 hover:bg-white/5 hover:text-slate-200"
                                )}
                            >
                                <span className="flex items-center gap-2.5">
                                    <div className={clsx("w-2 h-2 rounded-full", dotColor)} />
                                    <span>{cat.name}</span>
                                </span>
                                <span className="text-xs text-slate-500 bg-white/5 px-1.5 py-0.5 rounded">
                                    {cat.count}
                                </span>
                            </button>
                        );
                    })}
                </nav>
            </div>

            {/* Footer */}
            <div className="p-4 border-t border-white/5 space-y-2">
                {onLogout && (
                    <button
                        onClick={onLogout}
                        className="w-full flex items-center gap-2.5 px-3 py-2 text-sm text-slate-400 hover:text-red-400 hover:bg-white/5 rounded-lg transition-all"
                    >
                        <LogOut className="w-4 h-4" />
                        Sign out
                    </button>
                )}
                <p className="text-[10px] text-slate-600 text-center">Powered by Groq + LangGraph</p>
            </div>
        </aside>
    );
}

function SidebarItem({
    icon: Icon,
    label,
    isActive,
    badge,
    badgeColor = "bg-indigo-500",
    accentColor,
    onClick,
}: {
    icon: React.ElementType;
    label: string;
    isActive: boolean;
    badge?: number;
    badgeColor?: string;
    accentColor?: string;
    onClick: () => void;
}) {
    return (
        <button
            onClick={onClick}
            className={clsx(
                "w-full flex items-center justify-between px-3 py-2 text-sm rounded-lg transition-all duration-150",
                isActive
                    ? "bg-white/10 text-white sidebar-active"
                    : "text-slate-400 hover:bg-white/5 hover:text-slate-200"
            )}
        >
            <span className="flex items-center gap-2.5">
                <Icon className={clsx("w-4 h-4", isActive && accentColor)} />
                <span>{label}</span>
            </span>
            {badge !== undefined && (
                <span className={clsx("text-[10px] font-bold text-white px-1.5 py-0.5 rounded-full min-w-5 text-center", badgeColor)}>
                    {badge}
                </span>
            )}
        </button>
    );
}
