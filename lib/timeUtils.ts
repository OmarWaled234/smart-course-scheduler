import { DayName, DAYS } from "@/types/schedule";

export const START_HOUR = 7;
export const END_HOUR = 24;
export const HOUR_HEIGHT = 64;

export function buildHourLabels() {
  return Array.from({ length: END_HOUR - START_HOUR + 1 }, (_, index) => {
    const hour = START_HOUR + index;
    return formatHour(hour);
  });
}

export function formatHour(hour24: number) {
  if (hour24 === 24) {
    return "12 AM";
  }

  const suffix = hour24 >= 12 ? "PM" : "AM";
  const hour = hour24 % 12 === 0 ? 12 : hour24 % 12;
  return `${hour} ${suffix}`;
}

export function timeToMinutes(time: string) {
  const [hours, minutes] = time.split(":").map(Number);
  return hours * 60 + minutes;
}

export function minutesToTime(totalMinutes: number) {
  const hours = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;
  return `${String(hours).padStart(2, "0")}:${String(minutes).padStart(2, "0")}`;
}

export function getBlockLayout(startTime: string, endTime: string) {
  const dayStart = START_HOUR * 60;
  const top = ((timeToMinutes(startTime) - dayStart) / 60) * HOUR_HEIGHT;
  const height = Math.max(
    36,
    ((timeToMinutes(endTime) - timeToMinutes(startTime)) / 60) * HOUR_HEIGHT
  );

  return { top, height };
}

export function isDayName(value: string): value is DayName {
  return DAYS.includes(value as DayName);
}

export const timeOptions = Array.from({ length: (END_HOUR - START_HOUR) * 2 + 1 }, (_, index) =>
  minutesToTime(START_HOUR * 60 + index * 30)
);
