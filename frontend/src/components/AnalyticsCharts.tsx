"use client";

import type { CategoryStat, PriorityStat } from "@/types";
import {
    PieChart,
    Pie,
    Cell,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
} from "recharts";

const CATEGORY_COLORS: Record<string, string> = {
    Institute: "#3b82f6",
    Professor: "#10b981",
    LinkedIn: "#0ea5e9",
    Society: "#8b5cf6",
    Promotion: "#f59e0b",
    Personal: "#ec4899",
};

const PRIORITY_COLORS: Record<string, string> = {
    HIGH: "#ef4444",
    MEDIUM: "#f59e0b",
    LOW: "#22c55e",
};

interface AnalyticsChartsProps {
    categories: CategoryStat[];
    priorities: PriorityStat[];
    isLoading: boolean;
}

export function AnalyticsCharts({
    categories,
    priorities,
    isLoading,
}: AnalyticsChartsProps) {
    if (isLoading) {
        return (
            <div className="grid grid-cols-1 xl:grid-cols-2 gap-4 px-3 sm:px-6 pb-4">
                <div className="skeleton h-48 rounded-xl" />
                <div className="skeleton h-48 rounded-xl" />
            </div>
        );
    }

    const categoryData = categories.map((c) => ({
        name: c.name,
        value: c.count,
        fill: CATEGORY_COLORS[c.name] || "#94a3b8",
    }));

    const priorityData = priorities.map((p) => ({
        name: p.name,
        count: p.count,
        fill: PRIORITY_COLORS[p.name] || "#94a3b8",
    }));

    return (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-4 px-3 sm:px-6 pb-4 animate-fade-in" style={{ animationDelay: "300ms" }}>
            {/* Category Distribution */}
            <div className="bg-white rounded-xl border border-slate-100 p-4">
                <h3 className="text-sm font-semibold text-slate-700 mb-3">
                    Category Distribution
                </h3>
                {categoryData.length > 0 ? (
                    <div className="flex flex-col sm:flex-row items-stretch gap-4">
                        <ResponsiveContainer width="100%" height={160}>
                            <PieChart>
                                <Pie
                                    data={categoryData}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={35}
                                    outerRadius={60}
                                    paddingAngle={3}
                                    dataKey="value"
                                    stroke="none"
                                >
                                    {categoryData.map((entry, i) => (
                                        <Cell key={`cell-${i}`} fill={entry.fill} />
                                    ))}
                                </Pie>
                                <Tooltip
                                    contentStyle={{
                                        borderRadius: "8px",
                                        border: "1px solid #e2e8f0",
                                        fontSize: "12px",
                                    }}
                                />
                            </PieChart>
                        </ResponsiveContainer>
                        <div className="flex-1 space-y-1.5">
                            {categoryData.map((cat) => (
                                <div key={cat.name} className="flex items-center justify-between text-xs">
                                    <div className="flex items-center gap-2">
                                        <div
                                            className="w-2.5 h-2.5 rounded-full"
                                            style={{ backgroundColor: cat.fill }}
                                        />
                                        <span className="text-slate-600">{cat.name}</span>
                                    </div>
                                    <span className="font-semibold text-slate-800">{cat.value}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                ) : (
                    <p className="text-sm text-slate-400 text-center py-8">No data yet</p>
                )}
            </div>

            {/* Priority Breakdown */}
            <div className="bg-white rounded-xl border border-slate-100 p-4">
                <h3 className="text-sm font-semibold text-slate-700 mb-3">
                    Priority Breakdown
                </h3>
                {priorityData.length > 0 ? (
                    <ResponsiveContainer width="100%" height={180}>
                        <BarChart data={priorityData} barGap={8}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                            <XAxis
                                dataKey="name"
                                tick={{ fontSize: 11, fill: "#64748b" }}
                                axisLine={false}
                                tickLine={false}
                            />
                            <YAxis
                                tick={{ fontSize: 11, fill: "#64748b" }}
                                axisLine={false}
                                tickLine={false}
                            />
                            <Tooltip
                                contentStyle={{
                                    borderRadius: "8px",
                                    border: "1px solid #e2e8f0",
                                    fontSize: "12px",
                                }}
                            />
                            <Bar dataKey="count" radius={[6, 6, 0, 0]} barSize={36}>
                                {priorityData.map((entry, i) => (
                                    <Cell key={`cell-${i}`} fill={entry.fill} />
                                ))}
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                ) : (
                    <p className="text-sm text-slate-400 text-center py-8">No data yet</p>
                )}
            </div>
        </div>
    );
}
