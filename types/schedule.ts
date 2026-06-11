export type DayName =
  | "Sunday"
  | "Monday"
  | "Tuesday"
  | "Wednesday"
  | "Thursday"
  | "Friday"
  | "Saturday";

export type Schedule = {
  id: string;
  user_id: string;
  title: string;
  semester: string;
  created_at: string;
};

export type ScheduleBlock = {
  id: string;
  schedule_id: string;
  title: string;
  day: DayName;
  start_time: string;
  end_time: string;
  instructor: string;
  location: string;
  notes: string;
  color: string;
  created_at: string;
};

export type ScheduleBlockDraft = Omit<ScheduleBlock, "id" | "created_at">;

export const DAYS: DayName[] = [
  "Sunday",
  "Monday",
  "Tuesday",
  "Wednesday",
  "Thursday",
  "Friday",
  "Saturday"
];
