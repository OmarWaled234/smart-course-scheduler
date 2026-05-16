import Constants from "expo-constants";
import { Platform } from "react-native";

const getHostFromExpo = () => {
  const hostUri =
    Constants.expoConfig?.hostUri ??
    Constants.manifest2?.extra?.expoClient?.hostUri ??
    "";
  return hostUri.split(":")[0];
};

const getDefaultBaseUrl = () => {
  const host = getHostFromExpo();
  if (host) {
    return `http://${host}:8000`;
  }
  if (Platform.OS === "android") {
    return "http://10.0.2.2:8000";
  }
  return "http://localhost:8000";
};

const env = (globalThis as { process?: { env?: Record<string, string | undefined> } }).process?.env;

export const API_BASE_URL = env?.EXPO_PUBLIC_API_BASE_URL ?? getDefaultBaseUrl();

export type Course = {
  id: number;
  name: string;
  instructor: string;
  color: string;
};

export type Task = {
  id: number;
  title: string;
  course_id: number;
  course_name: string;
  course_color: string;
  task_type: string;
  due_date: string;
  estimated_hours: number;
  completed_hours: number;
  remaining_hours: number;
  priority: "low" | "medium" | "high";
  completed: number;
  is_overdue: boolean;
};

export type StudyBlock = {
  id: number;
  day_of_week: string;
  start_time: string;
  end_time: string;
  completed: number;
  duration_hours: number;
};

export type ScheduleSession = {
  day: string;
  date: string;
  start_time: string;
  end_time: string;
  course: string;
  task: string;
  task_type: string;
  priority: string;
  session_hours: number;
  due_date: string;
  overdue: boolean;
  score: number;
};

export type Dashboard = {
  total_tasks: number;
  completed_tasks: number;
  overdue_tasks: number;
  upcoming_tasks: number;
  remaining_hours: number;
  study_blocks: number;
  tasks_by_course: { course_name: string; count: number }[];
  hours_by_course: { course_name: string; hours: number }[];
};

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers ?? {})
    }
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed with ${response.status}`);
  }

  if (response.status === 204) {
    return undefined as T;
  }
  return response.json() as Promise<T>;
}

export const api = {
  dashboard: () => request<Dashboard>("/api/dashboard"),
  courses: () => request<Course[]>("/api/courses"),
  tasks: () => request<Task[]>("/api/tasks"),
  studyBlocks: () => request<StudyBlock[]>("/api/study-blocks"),
  schedule: () => request<ScheduleSession[]>("/api/schedule"),
  demoData: () => request<{ status: string }>("/api/demo-data", { method: "POST" }),
  createCourse: (body: Omit<Course, "id">) =>
    request("/api/courses", { method: "POST", body: JSON.stringify(body) }),
  deleteCourse: (id: number) => request(`/api/courses/${id}`, { method: "DELETE" }),
  createTask: (body: {
    title: string;
    course_id: number;
    task_type: string;
    due_date: string;
    estimated_hours: number;
    completed_hours: number;
    priority: string;
    completed: boolean;
  }) => request("/api/tasks", { method: "POST", body: JSON.stringify(body) }),
  completeTask: (id: number, completed = true) =>
    request(`/api/tasks/${id}/complete?completed=${completed}`, { method: "POST" }),
  deleteTask: (id: number) => request(`/api/tasks/${id}`, { method: "DELETE" }),
  createStudyBlock: (body: {
    day_of_week: string;
    start_time: string;
    end_time: string;
    completed: boolean;
  }) => request("/api/study-blocks", { method: "POST", body: JSON.stringify(body) }),
  completeStudyBlock: (id: number, completed = true) =>
    request(`/api/study-blocks/${id}/complete?completed=${completed}`, { method: "POST" }),
  deleteStudyBlock: (id: number) => request(`/api/study-blocks/${id}`, { method: "DELETE" })
};
