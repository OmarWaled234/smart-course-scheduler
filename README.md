# Smart Course Scheduler

An Expo + React Native iOS-friendly schedule-making app for students and workers. Users can register, log in, create schedules, and add colored class/work blocks to a weekly Sunday-Saturday calendar grid.

## Tech Stack

- React Native with Expo
- TypeScript
- Expo Router
- Supabase Auth
- Supabase Postgres
- AsyncStorage for simple local/offline caching

## Project Structure

```text
app/
  index.tsx
  login.tsx
  register.tsx
  home.tsx
  schedule/[id].tsx
  create-schedule.tsx
  create-block.tsx
  edit-block/[id].tsx
components/
  CalendarGrid.tsx
  ScheduleBlock.tsx
  TimeColumn.tsx
  DayColumn.tsx
  ColorPicker.tsx
  FormInput.tsx
  PrimaryButton.tsx
lib/
  supabase.ts
  storage.ts
  timeUtils.ts
types/
  schedule.ts
supabase/
  schema.sql
```

## Supabase Setup

1. Create a Supabase project.
2. Open the SQL editor and run `supabase/schema.sql`.
3. In [lib/supabase.ts](./lib/supabase.ts), replace the placeholder URL and anon key with your project values.
4. In Supabase Auth settings, configure email confirmation based on how you want registration to behave during development.

## Run Locally

```bash
npm install
npm run start
```

Then open the app with Expo Go or the iOS simulator.

## Notes

- Calendar integration is intentionally not installed yet, but the screen boundaries make it straightforward to add `expo-calendar` later.
- Offline support starts with AsyncStorage through [lib/storage.ts](./lib/storage.ts), keeping the screens insulated so SQLite can replace it later.
