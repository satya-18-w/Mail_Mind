"use client";

import { useAuth } from "@/contexts/AuthContext";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import {
    Mail,
    Sparkles,
    Shield,
    Zap,
    BarChart3,
    Brain,
    Clock,
    Star,
    ArrowRight,
    CheckCircle2,
    ChevronDown,
} from "lucide-react";

export default function LandingPage() {
    const { isAuthenticated, isLoading, login } = useAuth();
    const router = useRouter();
    const [scrolled, setScrolled] = useState(false);

    useEffect(() => {
        if (!isLoading && isAuthenticated) {
            router.push("/");
        }
    }, [isAuthenticated, isLoading, router]);

    useEffect(() => {
        const onScroll = () => setScrolled(window.scrollY > 40);
        window.addEventListener("scroll", onScroll);
        return () => window.removeEventListener("scroll", onScroll);
    }, []);

    if (isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-slate-950">
                <div className="animate-spin rounded-full h-8 w-8 border-2 border-indigo-500 border-t-transparent" />
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-slate-950 text-white overflow-x-hidden">
            {/* Floating nav */}
            <nav
                className={`fixed top-0 inset-x-0 z-50 transition-all duration-300 ${scrolled
                        ? "bg-slate-950/80 backdrop-blur-xl border-b border-white/5 shadow-lg"
                        : ""
                    }`}
            >
                <div className="max-w-6xl mx-auto flex items-center justify-between px-6 py-4">
                    <div className="flex items-center gap-2.5">
                        <div className="w-9 h-9 rounded-xl bg-linear-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
                            <Brain className="w-5 h-5 text-white" />
                        </div>
                        <span className="text-lg font-bold tracking-tight">MailMind</span>
                    </div>
                    <button
                        onClick={login}
                        className="px-5 py-2 text-sm font-semibold rounded-lg bg-white/10 hover:bg-white/20 border border-white/10 transition-all"
                    >
                        Sign in
                    </button>
                </div>
            </nav>

            {/* Hero */}
            <section className="relative min-h-screen flex items-center justify-center pt-20">
                {/* Gradient orbs */}
                <div className="absolute top-[-15%] left-[-8%] w-175 h-175 rounded-full bg-indigo-600/15 blur-[140px] animate-pulse" />
                <div
                    className="absolute bottom-[-15%] right-[-8%] w-150 h-150 rounded-full bg-violet-600/15 blur-[140px] animate-pulse"
                    style={{ animationDelay: "1s" }}
                />
                <div
                    className="absolute top-[35%] left-[55%] w-100 h-100 rounded-full bg-cyan-600/8 blur-[100px] animate-pulse"
                    style={{ animationDelay: "2s" }}
                />
                {/* Grid */}
                <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,.02)_1px,transparent_1px)] bg-size-[60px_60px]" />

                <div className="relative z-10 text-center max-w-3xl mx-auto px-6">
                    <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs font-medium mb-8">
                        <Sparkles className="w-3.5 h-3.5" />
                        Powered by Groq AI & LangGraph
                    </div>

                    <h1 className="text-5xl sm:text-6xl lg:text-7xl font-extrabold leading-[1.1] tracking-tight mb-6">
                        Your inbox,{" "}
                        <span className="bg-linear-to-r from-indigo-400 via-violet-400 to-cyan-400 bg-clip-text text-transparent">
                            supercharged
                        </span>{" "}
                        by AI.
                    </h1>

                    <p className="text-lg sm:text-xl text-slate-400 max-w-xl mx-auto mb-10 leading-relaxed">
                        MailMind classifies, prioritizes, and summarizes your emails
                        instantly — so you focus on what truly matters.
                    </p>

                    <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                        <button
                            onClick={login}
                            className="group flex items-center gap-3 px-8 py-4 bg-linear-to-r from-indigo-600 to-violet-600 text-white font-semibold rounded-xl hover:from-indigo-500 hover:to-violet-500 transition-all shadow-xl shadow-indigo-500/25 hover:shadow-indigo-500/40 hover:scale-[1.02] active:scale-[0.98]"
                        >
                            <svg className="w-5 h-5" viewBox="0 0 24 24">
                                <path
                                    fill="#fff"
                                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"
                                />
                                <path
                                    fill="#fff"
                                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                                />
                                <path
                                    fill="#fff"
                                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                                />
                                <path
                                    fill="#fff"
                                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                                />
                            </svg>
                            Get started with Google
                            <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
                        </button>
                        <a
                            href="#features"
                            className="flex items-center gap-2 px-6 py-4 text-sm text-slate-400 hover:text-white transition-colors"
                        >
                            See how it works
                            <ChevronDown className="w-4 h-4" />
                        </a>
                    </div>

                    {/* Trust badges */}
                    <div className="flex items-center justify-center gap-6 mt-14 text-xs text-slate-500">
                        <span className="flex items-center gap-1.5">
                            <Shield className="w-3.5 h-3.5 text-emerald-500" />
                            Read-only access
                        </span>
                        <span className="flex items-center gap-1.5">
                            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                            No data stored externally
                        </span>
                        <span className="flex items-center gap-1.5">
                            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                            Open source
                        </span>
                    </div>
                </div>
            </section>

            {/* Features grid */}
            <section id="features" className="relative py-28 px-6">
                <div className="max-w-5xl mx-auto">
                    <div className="text-center mb-16">
                        <h2 className="text-3xl sm:text-4xl font-bold mb-4">
                            Everything you need to{" "}
                            <span className="bg-linear-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent">
                                master your inbox
                            </span>
                        </h2>
                        <p className="text-slate-400 max-w-lg mx-auto">
                            Six intelligent agents work together to analyze every email the
                            moment it arrives.
                        </p>
                    </div>

                    <div className="grid md:grid-cols-3 gap-5">
                        <FeatureCard
                            icon={Brain}
                            gradient="from-indigo-500 to-indigo-600"
                            title="Smart Classification"
                            description="Automatically sorts emails into 6 categories — Work, Personal, Finance, Promotions, Social, Updates."
                        />
                        <FeatureCard
                            icon={Zap}
                            gradient="from-amber-500 to-orange-500"
                            title="Priority Scoring"
                            description="AI assigns HIGH, MEDIUM, or LOW priority so you never miss what's urgent."
                        />
                        <FeatureCard
                            icon={Clock}
                            gradient="from-rose-500 to-red-500"
                            title="Deadline Detection"
                            description="Extracts deadlines from email content and alerts you before they pass."
                        />
                        <FeatureCard
                            icon={Sparkles}
                            gradient="from-violet-500 to-purple-600"
                            title="AI Summaries"
                            description="One-line AI-generated summaries let you scan 100 emails in seconds."
                        />
                        <FeatureCard
                            icon={BarChart3}
                            gradient="from-cyan-500 to-blue-500"
                            title="Analytics Dashboard"
                            description="Beautiful charts showing category distribution, priority breakdown, and trends."
                        />
                        <FeatureCard
                            icon={Star}
                            gradient="from-emerald-500 to-teal-600"
                            title="Star & Bookmark"
                            description="Star important emails and find them instantly in your dedicated starred view."
                        />
                    </div>
                </div>
            </section>

            {/* How it works */}
            <section className="relative py-24 px-6 border-t border-white/5">
                <div className="max-w-4xl mx-auto">
                    <div className="text-center mb-16">
                        <h2 className="text-3xl sm:text-4xl font-bold mb-4">
                            How it works
                        </h2>
                        <p className="text-slate-400">
                            Three simple steps to a smarter inbox.
                        </p>
                    </div>

                    <div className="grid md:grid-cols-3 gap-10">
                        <Step
                            number="01"
                            title="Connect Gmail"
                            description="Sign in with Google. We request read-only access — your emails never leave your machine."
                        />
                        <Step
                            number="02"
                            title="AI scans your inbox"
                            description="Six LangGraph agents classify, prioritize, detect deadlines, summarize, and embed each email."
                        />
                        <Step
                            number="03"
                            title="Take action"
                            description="Browse by category, search semantically, star what matters, and track deadlines — all in one view."
                        />
                    </div>
                </div>
            </section>

            {/* CTA */}
            <section className="relative py-28 px-6">
                <div className="max-w-2xl mx-auto text-center">
                    <div className="p-10 rounded-3xl bg-linear-to-br from-indigo-600/20 to-violet-600/20 border border-indigo-500/20 backdrop-blur-sm">
                        <h2 className="text-3xl font-bold mb-3">
                            Ready to reclaim your inbox?
                        </h2>
                        <p className="text-slate-400 mb-8">
                            Join now and let AI handle the chaos.
                        </p>
                        <button
                            onClick={login}
                            className="inline-flex items-center gap-3 px-8 py-4 bg-white text-slate-900 font-semibold rounded-xl hover:bg-slate-100 shadow-xl transition-all hover:scale-[1.02] active:scale-[0.98]"
                        >
                            <svg className="w-5 h-5" viewBox="0 0 24 24">
                                <path
                                    fill="#4285F4"
                                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"
                                />
                                <path
                                    fill="#34A853"
                                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                                />
                                <path
                                    fill="#FBBC05"
                                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                                />
                                <path
                                    fill="#EA4335"
                                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                                />
                            </svg>
                            Continue with Google
                        </button>
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="border-t border-white/5 py-8 px-6">
                <div className="max-w-6xl mx-auto flex items-center justify-between text-xs text-slate-600">
                    <div className="flex items-center gap-2">
                        <Brain className="w-4 h-4 text-indigo-500" />
                        <span className="font-semibold text-slate-400">MailMind</span>
                    </div>
                    <span>Built with LangGraph, Groq AI & Next.js</span>
                </div>
            </footer>
        </div>
    );
}

/* ---- Sub-components ---- */

function FeatureCard({
    icon: Icon,
    gradient,
    title,
    description,
}: {
    icon: React.ElementType;
    gradient: string;
    title: string;
    description: string;
}) {
    return (
        <div className="group p-6 rounded-2xl bg-white/3 border border-white/5 hover:border-indigo-500/30 hover:bg-white/6 transition-all duration-300">
            <div
                className={`w-11 h-11 rounded-xl bg-linear-to-br ${gradient} flex items-center justify-center mb-4 shadow-lg group-hover:scale-110 transition-transform`}
            >
                <Icon className="w-5 h-5 text-white" />
            </div>
            <h3 className="text-base font-semibold mb-2">{title}</h3>
            <p className="text-sm text-slate-400 leading-relaxed">{description}</p>
        </div>
    );
}

function Step({
    number,
    title,
    description,
}: {
    number: string;
    title: string;
    description: string;
}) {
    return (
        <div className="text-center">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-indigo-500/10 text-indigo-400 text-sm font-bold mb-4 border border-indigo-500/20">
                {number}
            </div>
            <h3 className="text-lg font-semibold mb-2">{title}</h3>
            <p className="text-sm text-slate-400 leading-relaxed">{description}</p>
        </div>
    );
}
