import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { notificationsApi, type NotificationListParams, type WatcherListParams } from '@/api/notifications';
import type { NotificationPreference, Watcher } from '@/types/notification';

export function useNotifications(params: NotificationListParams) {
  return useQuery({
    queryKey: ['notifications', params],
    queryFn: () => notificationsApi.list(params),
    enabled: !!params.email,
  });
}

export function useNotificationStats(email: string, days?: number) {
  return useQuery({
    queryKey: ['notifications', 'stats', email, days],
    queryFn: () => notificationsApi.getStats(email, days),
    enabled: !!email,
  });
}

export function useMarkNotificationRead() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => notificationsApi.markRead(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    },
  });
}

export function useMarkAllNotificationsRead() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (email: string) => notificationsApi.markAllRead(email),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    },
  });
}

// Preferences
export function useNotificationPreferences(email: string) {
  return useQuery({
    queryKey: ['notifications', 'preferences', email],
    queryFn: () => notificationsApi.getPreferences(email),
    enabled: !!email,
  });
}

export function useUpdateNotificationPreferences() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      email,
      preferences,
    }: {
      email: string;
      preferences: Partial<NotificationPreference>;
    }) => notificationsApi.updatePreferences(email, preferences),
    onSuccess: (_, { email }) => {
      queryClient.invalidateQueries({ queryKey: ['notifications', 'preferences', email] });
    },
  });
}

// Watchers
export function useWatchers(params?: WatcherListParams) {
  return useQuery({
    queryKey: ['watchers', params],
    queryFn: () => notificationsApi.listWatchers(params),
  });
}

export function useCreateWatcher() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (watcher: Partial<Watcher>) => notificationsApi.createWatcher(watcher),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['watchers'] });
    },
  });
}

export function useUpdateWatcher() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, watcher }: { id: string; watcher: Partial<Watcher> }) =>
      notificationsApi.updateWatcher(id, watcher),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['watchers'] });
    },
  });
}

export function useDeleteWatcher() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => notificationsApi.deleteWatcher(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['watchers'] });
    },
  });
}
