import { notificationClient } from './client';
import type { Notification, NotificationPreference, Watcher } from '@/types/notification';

export interface NotificationListParams {
  email: string;
  status?: string;
  event_type?: string;
  limit?: number;
  offset?: number;
}

export interface NotificationListResponse {
  items: Notification[];
  total: number;
  limit: number;
  offset: number;
}

export interface WatcherListParams {
  email?: string;
  contract_id?: string;
  publisher_team?: string;
  limit?: number;
  offset?: number;
}

export interface WatcherListResponse {
  items: Watcher[];
  total: number;
  limit: number;
  offset: number;
}

export const notificationsApi = {
  list: async (params: NotificationListParams): Promise<NotificationListResponse> => {
    const { data } = await notificationClient.get('/api/v1/notifications', { params });
    return data;
  },

  get: async (id: string): Promise<Notification> => {
    const { data } = await notificationClient.get(`/api/v1/notifications/${id}`);
    return data;
  },

  markRead: async (id: string): Promise<Notification> => {
    const { data } = await notificationClient.post(`/api/v1/notifications/${id}/mark-read`);
    return data;
  },

  markAllRead: async (email: string): Promise<{ marked_read: number }> => {
    const { data } = await notificationClient.post('/api/v1/notifications/mark-all-read', null, {
      params: { email },
    });
    return data;
  },

  getStats: async (email: string, days?: number): Promise<{
    email: string;
    period_days: number;
    total: number;
    unread: number;
    by_status: Record<string, number>;
    by_type: Record<string, number>;
  }> => {
    const { data } = await notificationClient.get(`/api/v1/notifications/stats/${email}`, {
      params: { days },
    });
    return data;
  },

  // Preferences
  getPreferences: async (email: string): Promise<NotificationPreference> => {
    const { data } = await notificationClient.get(`/api/v1/notifications/preferences/${email}`);
    return data;
  },

  updatePreferences: async (
    email: string,
    preferences: Partial<NotificationPreference>
  ): Promise<NotificationPreference> => {
    const { data } = await notificationClient.put(
      `/api/v1/notifications/preferences/${email}`,
      preferences
    );
    return data;
  },

  // Watchers
  listWatchers: async (params?: WatcherListParams): Promise<WatcherListResponse> => {
    const { data } = await notificationClient.get('/api/v1/watchers', { params });
    return data;
  },

  createWatcher: async (watcher: Partial<Watcher>): Promise<Watcher> => {
    const { data } = await notificationClient.post('/api/v1/watchers', watcher);
    return data;
  },

  updateWatcher: async (id: string, watcher: Partial<Watcher>): Promise<Watcher> => {
    const { data } = await notificationClient.put(`/api/v1/watchers/${id}`, watcher);
    return data;
  },

  deleteWatcher: async (id: string): Promise<void> => {
    await notificationClient.delete(`/api/v1/watchers/${id}`);
  },
};
