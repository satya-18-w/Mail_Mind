"use client";

import { useState, useEffect, useCallback, useRef } from "react";
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
} from "@/hooks/useEmails";
import { useAuth } from "@/contexts/AuthContext";
import type { Email } from "@/types";
import { RefreshCw, LayoutDashboard, Keyboard } from "lucide-react";

export default function Dashboard() {
  const { user, logout } = useAuth();
  const [selectedView, setSelectedView] = useState("all");
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [selectedPriority, setSelectedPriority] = useState<string | null>(null);
  const [selectedEmail, setSelectedEmail] = useState<Email | null>(null);
  const [showShortcuts, setShowShortcuts] = useState(false);
  const [searchResults, setSearchResults] = useState<Email[] | null>(null);
  const [showAnalytics, setShowAnalytics] = useState(true);

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

  return (
    <div className="flex h-screen bg-slate-50">
      {/* Keyboard shortcuts modal */}
      {showShortcuts && (
        <KeyboardShortcuts onClose={() => setShowShortcuts(false)} />
      )}

      {/* Sidebar */}
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
        }}
        onSelectPriority={(pri) => {
          setSelectedPriority(pri);
          setSelectedEmail(null);
          clearSearch();
        }}
        onSelectView={(view) => {
          setSelectedView(view);
          setSelectedEmail(null);
          clearSearch();
        }}
        unreadCount={statsOverview?.unread ?? 0}
        starredCount={statsOverview?.starred ?? 0}
      />

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="bg-white/80 backdrop-blur-md border-b border-slate-200/60 px-6 py-3 flex items-center gap-4 sticky top-0 z-20">
          <div className="flex-1 max-w-xl">
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
            disabled={pipelineMutation.isPending}
            className="flex items-center gap-2 px-4 py-2 bg-linear-to-r from-indigo-600 to-violet-600 text-white text-sm font-medium rounded-lg hover:from-indigo-700 hover:to-violet-700 disabled:opacity-50 transition-all shadow-sm hover:shadow-md active:scale-[0.98]"
          >
            <RefreshCw
              className={`w-4 h-4 ${pipelineMutation.isPending ? "animate-spin" : ""
                }`}
            />
            {pipelineMutation.isPending ? "Scanning..." : "Scan Emails"}
          </button>

          <UserMenu />
        </header>

        <ProfileSection user={user} />

        {/* Search results indicator */}
        {searchResults && (
          <div className="bg-indigo-50 px-6 py-2 flex items-center justify-between text-sm border-b border-indigo-100">
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
            className={`${selectedEmail ? "w-2/5" : "w-full"
              } border-r border-slate-200/60 overflow-hidden transition-all duration-300`}
          >
            <EmailList
              emails={displayEmails}
              selectedEmail={selectedEmail}
              onSelectEmail={setSelectedEmail}
              isLoading={isLoading}
            />
          </div>
          {selectedEmail && (
            <div className="w-3/5 overflow-hidden animate-slide-right">
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
