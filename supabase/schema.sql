create extension if not exists "pgcrypto";

create table if not exists public.schedules (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  title text not null,
  semester text default '',
  created_at timestamp with time zone default now()
);

create table if not exists public.schedule_blocks (
  id uuid primary key default gen_random_uuid(),
  schedule_id uuid not null references public.schedules(id) on delete cascade,
  title text not null,
  day text not null check (day in ('Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday')),
  start_time text not null,
  end_time text not null,
  instructor text default '',
  location text default '',
  notes text default '',
  color text not null default '#2563eb',
  created_at timestamp with time zone default now()
);

alter table public.schedules enable row level security;
alter table public.schedule_blocks enable row level security;

create policy "Users can view their schedules"
on public.schedules for select
using (auth.uid() = user_id);

create policy "Users can create their schedules"
on public.schedules for insert
with check (auth.uid() = user_id);

create policy "Users can update their schedules"
on public.schedules for update
using (auth.uid() = user_id)
with check (auth.uid() = user_id);

create policy "Users can delete their schedules"
on public.schedules for delete
using (auth.uid() = user_id);

create policy "Users can view their schedule blocks"
on public.schedule_blocks for select
using (
  exists (
    select 1 from public.schedules
    where schedules.id = schedule_blocks.schedule_id
    and schedules.user_id = auth.uid()
  )
);

create policy "Users can create their schedule blocks"
on public.schedule_blocks for insert
with check (
  exists (
    select 1 from public.schedules
    where schedules.id = schedule_blocks.schedule_id
    and schedules.user_id = auth.uid()
  )
);

create policy "Users can update their schedule blocks"
on public.schedule_blocks for update
using (
  exists (
    select 1 from public.schedules
    where schedules.id = schedule_blocks.schedule_id
    and schedules.user_id = auth.uid()
  )
)
with check (
  exists (
    select 1 from public.schedules
    where schedules.id = schedule_blocks.schedule_id
    and schedules.user_id = auth.uid()
  )
);

create policy "Users can delete their schedule blocks"
on public.schedule_blocks for delete
using (
  exists (
    select 1 from public.schedules
    where schedules.id = schedule_blocks.schedule_id
    and schedules.user_id = auth.uid()
  )
);
