"use client";

import { X } from "lucide-react";

interface KeyboardShortcutsProps {
    onClose: () => void;
}

const shortcuts = [
    { keys: ["Shift", "?"], description: "Show / hide this panel" },
    { keys: ["R"], description: "Scan emails (run pipeline)" },
    { keys: ["A"], description: "Toggle analytics dashboard" },
    { keys: ["Esc"], description: "Close detail panel / modal" },
    { keys: ["1"], description: "All emails" },
    { keys: ["2"], description: "High priority" },
    { keys: ["3"], description: "Deadlines" },
    { keys: ["4"], description: "Starred" },
];

export function KeyboardShortcuts({ onClose }: KeyboardShortcutsProps) {
    return (
        <div
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm animate-fade-in"
            onClick={onClose}
        >
            <div
                className="bg-white rounded-2xl shadow-2xl w-full max-w-sm mx-4 overflow-hidden"
                onClick={(e) => e.stopPropagation()}
            >
                <div className="flex items-center justify-between px-5 py-4 border-b border-slate-100">
                    <h2 className="text-sm font-semibold text-slate-800">
                        Keyboard Shortcuts
                    </h2>
                    <button
                        onClick={onClose}
                        className="p-1 rounded-md hover:bg-slate-100 text-slate-400 transition-colors"
                    >
                        <X className="w-4 h-4" />
                    </button>
                </div>

                <div className="p-4 space-y-2">
                    {shortcuts.map((s) => (
                        <div
                            key={s.description}
                            className="flex items-center justify-between py-1.5"
                        >
                            <span className="text-sm text-slate-600">{s.description}</span>
                            <div className="flex items-center gap-1">
                                {s.keys.map((key) => (
                                    <kbd
                                        key={key}
                                        className="inline-flex items-center justify-center min-w-6 h-6 px-1.5 text-[11px] font-medium text-slate-600 bg-slate-100 border border-slate-200 rounded-md shadow-sm"
                                    >
                                        {key}
                                    </kbd>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>

                <div className="px-5 py-3 bg-slate-50 border-t border-slate-100">
                    <p className="text-[11px] text-slate-400 text-center">
                        Press <kbd className="px-1 py-0.5 bg-white border rounded text-[10px]">Esc</kbd> to close
                    </p>
                </div>
            </div>
        </div>
    );
}
