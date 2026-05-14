-- ============================================================
-- GENOME SaaS — Initial Schema
-- Run this in your Supabase SQL Editor (once)
-- ============================================================

-- Profiles table (synced from Clerk via webhook)
create table if not exists profiles (
  id          text primary key,          -- Clerk user_id (e.g. "user_abc123")
  email       text,
  full_name   text,
  created_at  timestamptz default now()
);

-- Reports table
create table if not exists reports (
  id          uuid primary key default gen_random_uuid(),
  user_id     text not null references profiles(id) on delete cascade,
  title       text not null,
  report_type text default 'custom',     -- 'disease_risk' | 'genetic' | 'protocol' | 'custom'
  content     text not null,             -- Full Markdown string
  created_at  timestamptz default now()
);

-- Indexes
create index if not exists reports_user_id_idx on reports(user_id);
create index if not exists reports_created_at_idx on reports(created_at desc);

-- ============================================================
-- Row Level Security
-- NOTE: We use service role key in API routes for inserts,
--       so RLS mostly protects direct client access.
-- ============================================================
alter table profiles enable row level security;
alter table reports   enable row level security;

-- Drop policies if they exist (idempotent re-run)
drop policy if exists "profiles_self" on profiles;
drop policy if exists "reports_self"  on reports;

-- Users can only read/write their own profile
create policy "profiles_self" on profiles
  for all using (id = current_setting('request.jwt.claims', true)::json->>'sub');

-- Users can only read/write their own reports
create policy "reports_self" on reports
  for all using (user_id = current_setting('request.jwt.claims', true)::json->>'sub');
