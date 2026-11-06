import * as SecureStore from 'expo-secure-store';

const API_BASE_URL = (process.env.EXPO_PUBLIC_API_BASE_URL ?? 'http://127.0.0.1:8000/api').replace(/\/$/, '');
const ACCESS_TOKEN_KEY = 'longtua.accessToken';
const REFRESH_TOKEN_KEY = 'longtua.refreshToken';

export type Activity = {
  id: string;
  title: string;
  activityType: string | null;
  status: string;
  dateStart: string;
  startAt: string | null;
  endAt: string | null;
  durationMinutes: number | null;
};

export type Schedule = {
  scheduleVersion: { id: string; versionNumber: number; isCurrent: boolean } | null;
  items: Array<{ id: string; planningObjectId: string; startAt: string; endAt: string }>;
  unscheduled: Array<{ planningObjectId: string; date: string; title: string }>;
};

async function request<T>(path: string, init: RequestInit = {}, token?: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...init.headers,
    },
  });
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(typeof body?.detail === 'string' ? body.detail : `Request failed (${response.status})`);
  }
  return response.status === 204 ? (undefined as T) : response.json();
}

export async function login(email: string, password: string): Promise<void> {
  const result = await request<{ accessToken: string; refreshToken: string }>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password, rememberMe: true }),
  });
  await SecureStore.setItemAsync(ACCESS_TOKEN_KEY, result.accessToken);
  await SecureStore.setItemAsync(REFRESH_TOKEN_KEY, result.refreshToken);
}

export async function logout(): Promise<void> {
  const refreshToken = await SecureStore.getItemAsync(REFRESH_TOKEN_KEY);
  const accessToken = await SecureStore.getItemAsync(ACCESS_TOKEN_KEY);
  if (refreshToken && accessToken) {
    await request('/auth/logout', { method: 'POST', body: JSON.stringify({ refreshToken }) }, accessToken).catch(
      () => undefined,
    );
  }
  await SecureStore.deleteItemAsync(ACCESS_TOKEN_KEY);
  await SecureStore.deleteItemAsync(REFRESH_TOKEN_KEY);
}

export async function getAccessToken(): Promise<string | null> {
  return SecureStore.getItemAsync(ACCESS_TOKEN_KEY);
}

export async function getActivities(token: string): Promise<Activity[]> {
  return request<Activity[]>('/activities', {}, token);
}

export async function getSchedule(token: string): Promise<Schedule> {
  return request<Schedule>('/schedule', {}, token);
}

export async function createActivity(token: string, title: string): Promise<Activity> {
  return request<Activity>('/activities', {
    method: 'POST',
    body: JSON.stringify({
      activityType: 'TASK',
      title,
      dateStart: new Date().toISOString().slice(0, 10),
      durationMinutes: 60,
    }),
  }, token);
}

export async function cancelActivity(token: string, activityId: string): Promise<Activity> {
  return request<Activity>(`/activities/${activityId}/cancel`, { method: 'POST' }, token);
}

export type Preview = {
  proposalId: string;
  candidateItems: Array<{ planningObjectId: string; title: string; startAt: string; endAt: string }>;
};

export async function createPreview(token: string, inputText: string): Promise<Preview> {
  return request<Preview>('/planning/requests', {
    method: 'POST',
    body: JSON.stringify({ inputText }),
  }, token);
}

export async function reviewProposal(token: string, proposalId: string, action: 'confirm' | 'reject'): Promise<void> {
  await request(`/proposals/${proposalId}/${action}`, { method: 'POST', body: JSON.stringify({}) }, token);
}
