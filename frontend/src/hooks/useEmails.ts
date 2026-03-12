"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/services/api";

export function useEmails(limit = 50, offset = 0) {
    return useQuery({
        queryKey: ["emails", limit, offset],
        queryFn: () => api.getEmails(limit, offset),
    });
}

export function useEmail(id: number) {
    return useQuery({
        queryKey: ["email", id],
        queryFn: () => api.getEmail(id),
        enabled: id > 0,
    });
}

export function useMarkAsRead() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (id: number) => api.markAsRead(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["emails"] });
            queryClient.invalidateQueries({ queryKey: ["stats"] });
        },
    });
}

export function useToggleStar() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (id: number) => api.toggleStar(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["emails"] });
            queryClient.invalidateQueries({ queryKey: ["stats"] });
        },
    });
}

export function useStarredEmails() {
    return useQuery({
        queryKey: ["emails", "starred"],
        queryFn: () => api.getStarredEmails(),
    });
}

export function useEmailsByCategory(category: string | null) {
    return useQuery({
        queryKey: ["emails", "category", category],
        queryFn: () => api.getEmailsByCategory(category!),
        enabled: !!category,
    });
}

export function useEmailsByPriority(priority: string | null) {
    return useQuery({
        queryKey: ["emails", "priority", priority],
        queryFn: () => api.getEmailsByPriority(priority!),
        enabled: !!priority,
    });
}

export function useDeadlines() {
    return useQuery({
        queryKey: ["emails", "deadlines"],
        queryFn: () => api.getDeadlines(),
    });
}

export function useSearchEmails() {
    return useMutation({
        mutationFn: ({ query, limit }: { query: string; limit?: number }) =>
            api.searchEmails(query, limit),
    });
}

export function useStatsOverview() {
    return useQuery({
        queryKey: ["stats", "overview"],
        queryFn: api.getStatsOverview,
    });
}

export function useCategoryStats() {
    return useQuery({
        queryKey: ["stats", "categories"],
        queryFn: api.getCategoryStats,
    });
}

export function usePriorityStats() {
    return useQuery({
        queryKey: ["stats", "priorities"],
        queryFn: api.getPriorityStats,
    });
}

export function useTasks() {
    return useQuery({
        queryKey: ["tasks"],
        queryFn: api.getTasks,
    });
}

export function useTriggerPipeline() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: api.triggerPipeline,
        onSuccess: () => {
            setTimeout(() => {
                queryClient.invalidateQueries({ queryKey: ["emails"] });
                queryClient.invalidateQueries({ queryKey: ["stats"] });
            }, 3000);
        },
    });
}
