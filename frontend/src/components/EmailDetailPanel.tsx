"use client";

import { Fragment, type ReactNode, useEffect, useMemo, useState } from "react";
import type { Email } from "@/types";
import { PriorityBadge } from "./PriorityBadge";
import { DeadlineAlert } from "./DeadlineAlert";
import { X, Clock, Tag, FileText, CheckCircle, Star, ArrowLeft, Copy, Check, Sparkles } from "lucide-react";
import { useMarkAsRead, useToggleStar } from "@/hooks/useEmails";

interface EmailDetailPanelProps {
    email: Email | null;
    onClose: () => void;
}

type BodyBlock =
    | { kind: "paragraph"; text: string }
    | { kind: "url"; text: string }
    | { kind: "meta"; text: string }
    | { kind: "ul"; items: string[] }
    | { kind: "ol"; items: string[] };

function isUrlLine(line: string): boolean {
    const trimmed = line.trim();
    return /^<?https?:\/\//i.test(trimmed);
}

function isMetaLine(line: string): boolean {
    return /^\[[^\]]+\]$/.test(line.trim());
}

function isBulletLine(line: string): boolean {
    return /^[-*•]\s+/.test(line.trim());
}

function isOrderedLine(line: string): boolean {
    return /^\d+[.)]\s+/.test(line.trim());
}

function stripListMarker(line: string): string {
    return line.trim().replace(/^([-*•]|\d+[.)])\s+/, "");
}

function preprocessWrappedAngleBracketUrls(rawBody: string): string {
    const lines = rawBody.replace(/\r\n/g, "\n").split("\n");
    const output: string[] = [];
    let combining = false;
    let current = "";

    for (const line of lines) {
        const trimmed = line.trim();

        if (!combining && /<https?:\/\//i.test(trimmed) && !trimmed.includes(">")) {
            combining = true;
            current = trimmed;
            continue;
        }

        if (combining) {
            current += trimmed;
            if (trimmed.includes(">")) {
                output.push(current);
                current = "";
                combining = false;
            }
            continue;
        }

        output.push(line);
    }

    if (current) {
        output.push(current);
    }

    return output.join("\n");
}

function normalizeEmailBody(rawBody: string): BodyBlock[] {
    const lines = preprocessWrappedAngleBracketUrls(rawBody).split("\n");
    const blocks: BodyBlock[] = [];
    let current = "";
    let currentList: { kind: "ul" | "ol"; items: string[] } | null = null;

    const flushParagraph = () => {
        if (current.trim()) {
            blocks.push({ kind: "paragraph", text: current.trim() });
            current = "";
        }
    };

    const flushList = () => {
        if (currentList && currentList.items.length) {
            blocks.push(currentList);
        }
        currentList = null;
    };

    for (const line of lines) {
        const trimmed = line.trim();

        if (!trimmed) {
            flushParagraph();
            flushList();
            continue;
        }

        if (isBulletLine(trimmed) || isOrderedLine(trimmed)) {
            flushParagraph();
            const nextKind: "ul" | "ol" = isOrderedLine(trimmed) ? "ol" : "ul";
            if (!currentList || currentList.kind !== nextKind) {
                flushList();
                currentList = { kind: nextKind, items: [] };
            }
            currentList.items.push(stripListMarker(trimmed));
            continue;
        }

        if (isUrlLine(trimmed)) {
            flushParagraph();
            flushList();
            blocks.push({ kind: "url", text: trimmed });
            continue;
        }

        if (isMetaLine(trimmed)) {
            flushParagraph();
            flushList();
            blocks.push({ kind: "meta", text: trimmed.slice(1, -1) });
            continue;
        }

        flushList();

        if (!current) {
            current = trimmed;
            continue;
        }

        // Undo hard-wrapped plain-text lines from email clients.
        if (current.endsWith("-") && !trimmed.startsWith("-")) {
            current = `${current.slice(0, -1)}${trimmed}`;
        } else {
            current = `${current} ${trimmed}`;
        }
    }

    flushParagraph();
    flushList();

    return blocks;
}

function linkifyText(text: string): ReactNode[] {
    const parts = text.split(/(<?https?:\/\/[^\s>]+>?)/gi);

    return parts.map((part, idx) => {
        const clean = part.replace(/^<|>$/g, "");
        if (/^https?:\/\//i.test(clean)) {
            return (
                <a
                    key={`${clean}-${idx}`}
                    href={clean}
                    target="_blank"
                    rel="noreferrer"
                    className="text-indigo-600 underline underline-offset-2 break-all hover:text-indigo-700"
                >
                    {clean}
                </a>
            );
        }

        return <Fragment key={`text-${idx}`}>{part}</Fragment>;
    });
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
    const [showOriginalBody, setShowOriginalBody] = useState(false);
    const [copied, setCopied] = useState(false);

    const bodyBlocks = useMemo(
        () => normalizeEmailBody(email?.body ?? ""),
        [email?.body],
    );

    const copyBody = async () => {
        if (!email?.body) return;
        await navigator.clipboard.writeText(email.body);
        setCopied(true);
        window.setTimeout(() => setCopied(false), 1500);
    };

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
            <div className="sticky top-0 bg-white/80 backdrop-blur-md border-b border-slate-100 px-4 sm:px-6 py-4 z-10">
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

            <div className="px-4 sm:px-6 py-5 space-y-5">
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
                    <div className="mb-2 flex items-center justify-between gap-3">
                        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                            Email Body
                        </h3>
                        <div className="flex items-center gap-2">
                            <button
                                type="button"
                                onClick={() => setShowOriginalBody((prev) => !prev)}
                                className="inline-flex items-center gap-1 rounded-md border border-slate-200 bg-white px-2 py-1 text-xs font-medium text-slate-600 hover:bg-slate-50"
                                title="Toggle between cleaned and original body"
                            >
                                <Sparkles className="h-3 w-3" />
                                {showOriginalBody ? "Show Cleaned" : "Show Original"}
                            </button>
                            <button
                                type="button"
                                onClick={copyBody}
                                className="inline-flex items-center gap-1 rounded-md border border-slate-200 bg-white px-2 py-1 text-xs font-medium text-slate-600 hover:bg-slate-50"
                                title="Copy email body"
                            >
                                {copied ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
                                {copied ? "Copied" : "Copy"}
                            </button>
                        </div>
                    </div>

                    <div className="bg-slate-50 rounded-xl p-4 text-sm text-slate-700 leading-relaxed border border-slate-100 space-y-3">
                        {!email.body?.trim() ? (
                            <p className="text-slate-400 italic">No readable body content found in this email.</p>
                        ) : showOriginalBody ? (
                            <pre className="whitespace-pre-wrap break-words overflow-x-auto font-sans text-sm text-slate-700">
                                {email.body}
                            </pre>
                        ) : bodyBlocks.map((block, idx) => {
                            if (block.kind === "ul") {
                                return (
                                    <ul key={`ul-${idx}`} className="list-disc pl-5 space-y-1">
                                        {block.items.map((item, itemIdx) => (
                                            <li key={`ul-${idx}-${itemIdx}`} className="break-words">
                                                {linkifyText(item)}
                                            </li>
                                        ))}
                                    </ul>
                                );
                            }

                            if (block.kind === "ol") {
                                return (
                                    <ol key={`ol-${idx}`} className="list-decimal pl-5 space-y-1">
                                        {block.items.map((item, itemIdx) => (
                                            <li key={`ol-${idx}-${itemIdx}`} className="break-words">
                                                {linkifyText(item)}
                                            </li>
                                        ))}
                                    </ol>
                                );
                            }

                            if (block.kind === "meta") {
                                return (
                                    <div
                                        key={`meta-${idx}`}
                                        className="inline-flex items-center rounded-full bg-slate-200/80 px-2.5 py-1 text-xs font-medium text-slate-600"
                                    >
                                        {block.text}
                                    </div>
                                );
                            }

                            const paragraphClass =
                                block.kind === "url"
                                    ? "wrap-break-word text-slate-800"
                                    : "wrap-break-word";

                            return (
                                <p key={`para-${idx}`} className={paragraphClass}>
                                    {linkifyText(block.text)}
                                </p>
                            );
                        })}
                    </div>
                </div>
            </div>
        </div>
    );
}
