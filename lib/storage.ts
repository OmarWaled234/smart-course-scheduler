import AsyncStorage from "@react-native-async-storage/async-storage";
import { Schedule, ScheduleBlock } from "@/types/schedule";

const SCHEDULES_KEY = "smart-course-scheduler:schedules";
const BLOCKS_KEY = "smart-course-scheduler:schedule-blocks";

async function readJson<T>(key: string, fallback: T): Promise<T> {
  const value = await AsyncStorage.getItem(key);
  return value ? (JSON.parse(value) as T) : fallback;
}

async function writeJson<T>(key: string, value: T) {
  await AsyncStorage.setItem(key, JSON.stringify(value));
}

// This thin repository-style wrapper keeps offline storage isolated.
// Later, the internals can move from AsyncStorage to SQLite without changing screens.
export const localStorage = {
  getSchedules: () => readJson<Schedule[]>(SCHEDULES_KEY, []),
  saveSchedules: (schedules: Schedule[]) => writeJson(SCHEDULES_KEY, schedules),
  getBlocks: () => readJson<ScheduleBlock[]>(BLOCKS_KEY, []),
  saveBlocks: (blocks: ScheduleBlock[]) => writeJson(BLOCKS_KEY, blocks)
};
