"use client";

import { useState, useEffect, useRef } from "react";
import { Sidebar } from "@/components/Sidebar";
import { EmailList } from "@/components/EmailList";
import { EmailDetailPanel } from "@/components/EmailDetailPanel";
import { SearchBar } from "@/components/SearchBar";
import { StatsCards } from "@/components/StatsCards";
import { AnalyticsCharts } from "@/components/AnalyticsCharts";
import { UserMenu } from "@/components/UserMenu";
import { KeyboardShortcuts } from "@/components/KeyboardShortcuts";
import { ProfileSection } from "@/components/ProfileSection";
import {
  useEmails,
  useEmailsByCategory,
  useEmailsByPriority,
  useDeadlines,
  useStarredEmails,
  useCategoryStats,
  usePriorityStats,
  useStatsOverview,
  useSearchEmails,
  useTriggerPipeline,
  useLatestPipelineRun,
} from "@/hooks/useEmails";
import { useAuth } from "@/contexts/AuthContext";
import type { Email } from "@/types";
import { RefreshCw, LayoutDashboard, Keyboard, Menu, X } from "lucide-react";
import { useQueryClient } from "@tanstack/react-query";

export default function Dashboard() {
  const { user, logout } = useAuth();
  const queryClient = useQueryClient();
  const [selectedView, setSelectedView] = useState("all");
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [selectedPriority, setSelectedPriority] = useState<string | null>(null);
  const [selectedEmail, setSelectedEmail] = useState<Email | null>(null);
  const [showShortcuts, setShowShortcuts] = useState(false);
  const [searchResults, setSearchResults] = useState<Email[] | null>(null);
  const [showAnalytics, setShowAnalytics] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Data queries
  const { data: allEmails = [], isLoading: loadingAll } = useEmails();
  const { data: categoryEmails = [], isLoading: loadingCategory } =
    useEmailsByCategory(selectedCategory);
  const { data: priorityEmails = [], isLoading: loadingPriority } =
    useEmailsByPriority(selectedPriority);
  const { data: deadlineEmails = [], isLoading: loadingDeadlines } =
    useDeadlines();
  const { data: starredEmails = [], isLoading: loadingStarred } =
    useStarredEmails();
  const { data: categories = [] } = useCategoryStats();
  const { data: priorities = [] } = usePriorityStats();
  const { data: statsOverview, isLoading: loadingStats } = useStatsOverview();

  const searchMutation = useSearchEmails();
  const pipelineMutation = useTriggerPipeline();
  const { data: latestRun } = useLatestPipelineRun(!!user);

  const isPipelineActive =
    pipelineMutation.isPending ||
    latestRun?.status === "QUEUED" ||
    latestRun?.status === "RUNNING";

  const pipelineTotal = latestRun?.fetched_count ?? 0;
  const pipelineDone =
    (latestRun?.processed_count ?? 0) +
    (latestRun?.skipped_count ?? 0) +
    (latestRun?.failed_count ?? 0);
  const pipelinePercent = pipelineTotal > 0
    ? Math.min(100, Math.round((pipelineDone / pipelineTotal) * 100))
    : 0;

  const pipelineLabel = (() => {
    if (pipelineMutation.isPending) return "Starting...";
    if (!latestRun) return "Scan Emails";
    if (latestRun.status === "QUEUED") return "Queued...";
    if (latestRun.status === "RUNNING") {
      return `Processing ${latestRun.processed_count}/${latestRun.fetched_count || "?"}`;
    }
    return "Scan Emails";
  })();

  useEffect(() => {
    if (!latestRun) return;
    if (latestRun.status === "COMPLETED" || latestRun.status === "FAILED") {
      queryClient.invalidateQueries({ queryKey: ["emails"] });
      queryClient.invalidateQueries({ queryKey: ["stats"] });
    }
  }, [latestRun, queryClient]);

  // Determine which emails to show
  let displayEmails: Email[] = [];
  let isLoading = false;

  if (searchResults) {
    displayEmails = searchResults;
  } else if (selectedView === "all") {
    displayEmails = allEmails;
    isLoading = loadingAll;
  } else if (selectedView === "category" && selectedCategory) {
    displayEmails = categoryEmails;
    isLoading = loadingCategory;
  } else if (selectedView === "high-priority") {
    displayEmails = priorityEmails;
    isLoading = loadingPriority;
  } else if (selectedView === "deadlines") {
    displayEmails = deadlineEmails;
    isLoading = loadingDeadlines;
  } else if (selectedView === "starred") {
    displayEmails = starredEmails;
    isLoading = loadingStarred;
  }

  const handleSearch = (query: string) => {
    searchMutation.mutate(
      { query },
      {
        onSuccess: (data) => setSearchResults(data.emails),
      }
    );
  };

  const clearSearch = () => setSearchResults(null);

  // Refs for keyboard handler to avoid stale closures
  const showShortcutsRef = useRef(showShortcuts);
  const selectedEmailRef = useRef(selectedEmail);
  useEffect(() => { showShortcutsRef.current = showShortcuts; }, [showShortcuts]);
  useEffect(() => { selectedEmailRef.current = selectedEmail; }, [selectedEmail]);

  // Keyboard shortcuts
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      // Don't trigger in inputs
      if (
        e.target instanceof HTMLInputElement ||
        e.target instanceof HTMLTextAreaElement
      )
        return;

      if (e.key === "?" && e.shiftKey) {
        e.preventDefault();
        setShowShortcuts((v) => !v);
      }
      if (e.key === "Escape") {
        if (showShortcutsRef.current) setShowShortcuts(false);
        else if (selectedEmailRef.current) setSelectedEmail(null);
      }
      if (e.key === "r" && !e.ctrlKey && !e.metaKey) {
        e.preventDefault();
        pipelineMutation.mutate();
      }
      if (e.key === "a" && !e.ctrlKey && !e.metaKey) {
        e.preventDefault();
        setShowAnalytics((v) => !v);
      }
      if (e.key === "1") {
        setSelectedView("all");
        setSelectedCategory(null);
        setSelectedPriority(null);
      }
      if (e.key === "2") {
        setSelectedView("high-priority");
        setSelectedCategory(null);
        setSelectedPriority("HIGH");
      }
      if (e.key === "3") {
        setSelectedView("deadlines");
        setSelectedCategory(null);
        setSelectedPriority(null);
      }
      if (e.key === "4") {
        setSelectedView("starred");
        setSelectedCategory(null);
        setSelectedPriority(null);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [pipelineMutation]);

  useEffect(() => {
    if (!selectedEmail) return;
    setSidebarOpen(false);
  }, [selectedEmail]);

  return (
    <div className="flex h-dvh bg-slate-50 overflow-hidden">
      {/* Keyboard shortcuts modal */}
      {showShortcuts && (
        <KeyboardShortcuts onClose={() => setShowShortcuts(false)} />
      )}

      {sidebarOpen && (
        <button
          type="button"
          className="fixed inset-0 z-30 bg-slate-900/45 md:hidden"
          onClick={() => setSidebarOpen(false)}
          aria-label="Close menu"
        />
      )}

      {/* Sidebar */}
      <div
        className={`fixed inset-y-0 left-0 z-40 w-72 max-w-[82vw] transform transition-transform duration-300 md:relative md:inset-auto md:z-auto md:w-64 md:max-w-none ${sidebarOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"
          }`}
      >
        <div className="relative h-full">
          <button
            type="button"
            onClick={() => setSidebarOpen(false)}
            className="absolute right-3 top-3 rounded-lg p-1.5 text-slate-300 hover:bg-white/10 md:hidden"
            aria-label="Close sidebar"
          >
            <X className="h-4 w-4" />
          </button>
          <Sidebar
            categories={categories}
            selectedCategory={selectedCategory}
            selectedPriority={selectedPriority}
            selectedView={selectedView}
            onLogout={logout}
            onSelectCategory={(cat) => {
              setSelectedCategory(cat);
              setSelectedEmail(null);
              clearSearch();
              setSidebarOpen(false);
            }}
            onSelectPriority={(pri) => {
              setSelectedPriority(pri);
              setSelectedEmail(null);
              clearSearch();
              setSidebarOpen(false);
            }}
            onSelectView={(view) => {
              setSelectedView(view);
              setSelectedEmail(null);
              clearSearch();
              setSidebarOpen(false);
            }}
            unreadCount={statsOverview?.unread ?? 0}
            starredCount={statsOverview?.starred ?? 0}
          />
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="bg-white/80 backdrop-blur-md border-b border-slate-200/60 px-3 sm:px-6 py-3 flex items-center gap-2 sm:gap-4 sticky top-0 z-20">
          <button
            type="button"
            onClick={() => setSidebarOpen(true)}
            className="p-2 rounded-lg text-slate-500 hover:bg-slate-100 md:hidden"
            aria-label="Open sidebar"
          >
            <Menu className="w-5 h-5" />
          </button>

          <div className="flex-1 min-w-0 sm:max-w-xl">
            <SearchBar
              onSearch={handleSearch}
              isSearching={searchMutation.isPending}
            />
          </div>

          <button
            onClick={() => setShowAnalytics(!showAnalytics)}
            className={`p-2 rounded-lg transition-colors ${showAnalytics
              ? "bg-indigo-50 text-indigo-600"
              : "text-slate-400 hover:bg-slate-100"
              }`}
            title="Toggle Analytics"
          >
            <LayoutDashboard className="w-4.5 h-4.5" />
          </button>

          <button
            onClick={() => setShowShortcuts(true)}
            className="p-2 rounded-lg text-slate-400 hover:bg-slate-100 transition-colors"
            title="Keyboard Shortcuts (?)"
          >
            <Keyboard className="w-4.5 h-4.5" />
          </button>

          <button
            onClick={() => pipelineMutation.mutate()}
            disabled={isPipelineActive}
            className="flex items-center gap-1.5 sm:gap-2 px-2.5 sm:px-4 py-2 bg-linear-to-r from-indigo-600 to-violet-600 text-white text-xs sm:text-sm font-medium rounded-lg hover:from-indigo-700 hover:to-violet-700 disabled:opacity-50 transition-all shadow-sm hover:shadow-md active:scale-[0.98]"
          >
            <RefreshCw
              className={`w-4 h-4 ${isPipelineActive ? "animate-spin" : ""
                }`}
            />
            <span className="hidden sm:inline">{pipelineLabel}</span>
            <span className="sm:hidden">Scan</span>
          </button>

          <UserMenu />
        </header>

        <ProfileSection user={user} />

        {latestRun && (
          <div className="px-3 sm:px-6 py-2 border-b border-slate-200/60 bg-white/60 text-xs sm:text-sm text-slate-600 flex flex-wrap items-center gap-x-4 gap-y-1">
            <span>
              Pipeline: <strong className="text-slate-800">{latestRun.status}</strong>
            </span>
            <span>Fetched: {latestRun.fetched_count}</span>
            <span>Processed: {latestRun.processed_count}</span>
            <span>Skipped: {latestRun.skipped_count}</span>
            <span>Failed: {latestRun.failed_count}</span>
            {latestRun.error_message && (
              <span className="text-rose-600 truncate max-w-full" title={latestRun.error_message}>
                Error: {latestRun.error_message}
              </span>
            )}
          </div>
        )}

        {isPipelineActive && (
          <div className="px-3 sm:px-6 py-2 border-b border-slate-200/50 bg-white/70">
            <div className="flex items-center justify-between text-xs text-slate-600 mb-1.5">
              <span>
                AI has read <strong className="text-slate-800">{latestRun?.processed_count ?? 0}</strong>
                {pipelineTotal > 0 ? ` / ${pipelineTotal}` : " emails"}
              </span>
              <span>
                {pipelineTotal > 0 ? `${pipelinePercent}%` : "Preparing inbox scan..."}
              </span>
            </div>
            <div className="h-2 w-full rounded-full bg-slate-200 overflow-hidden">
              {pipelineTotal > 0 ? (
                <div
                  className="h-full bg-linear-to-r from-indigo-500 to-violet-500 transition-all duration-500"
                  style={{ width: `${pipelinePercent}%` }}
                />
              ) : (
                <div className="h-full w-2/5 bg-linear-to-r from-indigo-500 to-violet-500 animate-pulse" />
              )}
            </div>
          </div>
        )}

        {/* Search results indicator */}
        {searchResults && (
          <div className="bg-indigo-50 px-3 sm:px-6 py-2 flex items-center justify-between text-sm border-b border-indigo-100">
            <span className="text-indigo-700 font-medium">
              {searchResults.length} search result{searchResults.length !== 1 ? "s" : ""}
            </span>
            <button
              onClick={clearSearch}
              className="text-indigo-600 hover:text-indigo-800 text-xs font-medium"
            >
              Clear search
            </button>
          </div>
        )}

        {/* Analytics Section */}
        {showAnalytics && !searchResults && selectedView === "all" && (
          <div className="border-b border-slate-200/60">
            <StatsCards data={statsOverview} isLoading={loadingStats} />
            <AnalyticsCharts
              categories={categories}
              priorities={priorities}
              isLoading={loadingStats}
            />
          </div>
        )}

        {/* Email list + Detail */}
        <div className="flex flex-1 min-h-0">
          <div
            className={`${selectedEmail ? "hidden md:block md:w-2/5" : "w-full"
              } md:border-r border-slate-200/60 overflow-hidden transition-all duration-300`}
          >
            <EmailList
              emails={displayEmails}
              selectedEmail={selectedEmail}
              onSelectEmail={setSelectedEmail}
              isLoading={isLoading}
            />
          </div>
          {selectedEmail && (
            <div className="w-full md:w-3/5 overflow-hidden animate-slide-right">
              <EmailDetailPanel
                email={selectedEmail}
                onClose={() => setSelectedEmail(null)}
              />
            </div>
          )}
          {!selectedEmail && (
            <div className="hidden" />
          )}
        </div>
      </div>
    </div>
  );
}
