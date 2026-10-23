-- Run once in Supabase SQL Editor. Keep the bucket private.
create table if not exists public.btcusdt_history_objects (
  object_path text primary key,
  file_name text not null,
  dataset text not null,
  month text,
  size_bytes bigint not null check (size_bytes >= 0),
  sha256 text not null check (length(sha256) = 64),
  validation_status text not null default 'COLLECTED',
  source_url text,
  uploaded_at timestamptz not null default now()
);
create index if not exists btcusdt_history_objects_dataset_month_idx
  on public.btcusdt_history_objects (dataset, month);
alter table public.btcusdt_history_objects enable row level security;
-- No anon/authenticated policies: only service-role automation can write/read this catalog.
