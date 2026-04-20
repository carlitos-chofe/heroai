/**
 * API client — fetch wrapper toward FastAPI backend.
 * Automatically attaches the Clerk session token.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export type LanguageTarget = "es" | "en" | "mixed_es_en";

export type AvatarConfig = {
  hair: string;
  hair_color: string;
  eye_color: string;
  skin: string;
  clothing: string;
};

export type PreferenceSummary = {
  likes: string[];
  avoid: string[];
  last_reactions: { panel_order: number; reaction_type: string }[];
};

export type Profile = {
  id: string;
  name: string;
  age: number;
  initial_interests: string;
  avatar_config: AvatarConfig;
  preference_summary: PreferenceSummary;
  created_at: string;
  updated_at: string;
};

export type StoryListItem = {
  id: string;
  child_profile_id: string;
  title: string | null;
  status: string;
  language_target: LanguageTarget;
  created_at: string;
  completed_at: string | null;
};

export type Panel = {
  panel_order: number;
  scene_description: string;
  narrative_text: string;
  dialogue: string;
  image_url: string | null;
};

export type StoryDetail = {
  id: string;
  child_profile_id: string;
  title: string | null;
  status: string;
  language_target: LanguageTarget;
  error_message: string | null;
  created_at: string;
  completed_at: string | null;
  panels: Panel[];
};

export type StoryStatus = {
  story_id: string;
  status: string;
  generated_panels: number;
  total_panels: number;
  error_message: string | null;
};

export type StoryScript = {
  story_id: string;
  title: string | null;
  language_target: LanguageTarget;
  panels: Omit<Panel, "image_url">[];
};

async function apiFetch<T>(
  path: string,
  options: RequestInit & { token?: string } = {}
): Promise<T> {
  const { token, ...fetchOptions } = options;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(fetchOptions.headers as Record<string, string>),
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, {
    ...fetchOptions,
    headers,
  });

  if (!res.ok) {
    let detail: unknown;
    try {
      detail = await res.json();
    } catch {
      detail = { message: res.statusText };
    }
    throw { status: res.status, detail };
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

// --- Profiles ---

export async function getProfiles(token: string): Promise<Profile[]> {
  return apiFetch("/api/v1/profiles", { token });
}

export async function createProfile(
  token: string,
  data: { name: string; age: number; initial_interests: string; avatar_config: AvatarConfig }
): Promise<Profile> {
  return apiFetch("/api/v1/profiles", {
    method: "POST",
    body: JSON.stringify(data),
    token,
  });
}

export async function updateProfile(
  token: string,
  profileId: string,
  data: Partial<{ name: string; age: number; initial_interests: string; avatar_config: AvatarConfig }>
): Promise<Profile> {
  return apiFetch(`/api/v1/profiles/${profileId}`, {
    method: "PATCH",
    body: JSON.stringify(data),
    token,
  });
}

// --- Stories ---

export async function createStory(
  token: string,
  data: { profile_id: string; content: string; language_target: LanguageTarget }
): Promise<{ story_id: string; status: string }> {
  return apiFetch("/api/v1/stories", {
    method: "POST",
    body: JSON.stringify(data),
    token,
  });
}

export async function getStories(
  token: string,
  params?: { profile_id?: string; status?: string }
): Promise<StoryListItem[]> {
  const qs = new URLSearchParams();
  if (params?.profile_id) qs.set("profile_id", params.profile_id);
  if (params?.status) qs.set("status", params.status);
  const query = qs.toString() ? `?${qs.toString()}` : "";
  return apiFetch(`/api/v1/stories${query}`, { token });
}

export async function getStory(token: string, storyId: string): Promise<StoryDetail> {
  return apiFetch(`/api/v1/stories/${storyId}`, { token });
}

export async function getStoryStatus(token: string, storyId: string): Promise<StoryStatus> {
  return apiFetch(`/api/v1/stories/${storyId}/status`, { token });
}

export async function getStoryScript(token: string, storyId: string): Promise<StoryScript> {
  return apiFetch(`/api/v1/stories/${storyId}/script`, { token });
}

export async function approveStory(
  token: string,
  storyId: string
): Promise<{ story_id: string; status: string }> {
  return apiFetch(`/api/v1/stories/${storyId}/approve`, {
    method: "POST",
    token,
  });
}

export async function postFeedback(
  token: string,
  storyId: string,
  data: { panel_order: number; reaction_type: string }
): Promise<unknown> {
  return apiFetch(`/api/v1/stories/${storyId}/feedback`, {
    method: "POST",
    body: JSON.stringify(data),
    token,
  });
}

export function assetUrl(relativePath: string): string {
  return `${API_BASE}${relativePath}`;
}
