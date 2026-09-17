-- Migration 0002: Multi-User + Notebooks
-- Führt echte Nutzerverwaltung (Supabase Auth) und mehrere Notebooks pro Nutzer ein.
-- Das Backend nutzt weiterhin den service_role-Key (umgeht RLS) und filtert zusätzlich
-- explizit nach user_id/notebook_id in jeder Query. Die RLS-Policies hier sind
-- Tiefenverteidigung, kein alleiniger Schutzmechanismus.

create table if not exists notebooks (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  name text not null,
  created_at timestamptz not null default now()
);

create index if not exists notebooks_user_id_idx on notebooks (user_id);

-- sources.notebook_id ist Pflichtfeld ab hier (Tabelle war zum Zeitpunkt dieser Migration
-- leer, siehe PROGRESS.md — keine Datenmigration nötig).
alter table sources add column notebook_id uuid not null references notebooks (id) on delete cascade;
create index if not exists sources_notebook_id_idx on sources (notebook_id);

alter table notebooks enable row level security;
alter table sources enable row level security;
alter table chunks enable row level security;

create policy "Nutzer verwalten nur eigene Notebooks" on notebooks
  for all
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

create policy "Nutzer sehen nur Quellen eigener Notebooks" on sources
  for all
  using (exists (
    select 1 from notebooks
    where notebooks.id = sources.notebook_id and notebooks.user_id = auth.uid()
  ))
  with check (exists (
    select 1 from notebooks
    where notebooks.id = sources.notebook_id and notebooks.user_id = auth.uid()
  ));

create policy "Nutzer sehen nur Chunks eigener Quellen" on chunks
  for all
  using (exists (
    select 1 from sources
    join notebooks on notebooks.id = sources.notebook_id
    where sources.id = chunks.source_id and notebooks.user_id = auth.uid()
  ))
  with check (exists (
    select 1 from sources
    join notebooks on notebooks.id = sources.notebook_id
    where sources.id = chunks.source_id and notebooks.user_id = auth.uid()
  ));

-- match_chunks muss jetzt zusätzlich nach notebook_id filtern, sonst würde die
-- Ähnlichkeitssuche versehentlich Quellen aus fremden Notebooks mit durchsuchen.
create or replace function match_chunks(
  query_embedding vector(768),
  target_notebook_id uuid,
  match_count int default 6
)
returns table (
  id uuid,
  source_id uuid,
  content text,
  similarity float,
  filename text
)
language sql stable
as $$
  select
    chunks.id,
    chunks.source_id,
    chunks.content,
    1 - (chunks.embedding <=> query_embedding) as similarity,
    sources.filename
  from chunks
  join sources on sources.id = chunks.source_id
  where sources.notebook_id = target_notebook_id
  order by chunks.embedding <=> query_embedding
  limit match_count;
$$;

-- Explizite Grants für die neue Tabelle (siehe Begründung in 0001_initial_schema.sql:
-- "Automatically expose new tables" ist deaktiviert, also keine automatischen Grants).
grant all on notebooks to service_role;
