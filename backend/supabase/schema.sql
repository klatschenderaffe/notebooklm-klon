-- NotebookLM-Klon: Supabase-Schema
-- Anwenden im Supabase SQL Editor des Projekts (siehe README "Supabase Setup").
-- Single-User-Anwendung: keine Row-Level-Security / Nutzer-Trennung nötig.

create extension if not exists vector;

create table if not exists sources (
  id uuid primary key default gen_random_uuid(),
  filename text not null,
  file_type text not null check (file_type in ('pdf', 'md')),
  storage_path text not null,
  created_at timestamptz not null default now()
);

-- Embedding-Dimension muss zu GEMINI_EMBEDDING_DIMENSIONS in backend/app/config.py passen (Standard: 768).
create table if not exists chunks (
  id uuid primary key default gen_random_uuid(),
  source_id uuid not null references sources (id) on delete cascade,
  chunk_index int not null,
  content text not null,
  embedding vector(768) not null,
  created_at timestamptz not null default now()
);

create index if not exists chunks_embedding_idx
  on chunks using hnsw (embedding vector_cosine_ops);

create index if not exists chunks_source_id_idx on chunks (source_id);

-- RPC-Funktion für die Ähnlichkeitssuche (Cosine Similarity), aufgerufen über supabase-py `.rpc()`.
create or replace function match_chunks(
  query_embedding vector(768),
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
  order by chunks.embedding <=> query_embedding
  limit match_count;
$$;

-- Storage-Bucket für die Original-Dateien (im Supabase-Dashboard unter Storage anlegen,
-- falls nicht per SQL verfügbar): Name "sources", nicht-öffentlich.

-- Explizite Rechte für service_role: Da "Automatically expose new tables" beim Projekt-
-- Setup bewusst deaktiviert wurde (empfohlene Absicherung gegen anon/authenticated-
-- Zugriff), vergibt Supabase KEINE automatischen Grants mehr — auch nicht für
-- service_role, wenn Tabellen wie hier per SQL statt über den Table Editor angelegt
-- werden. service_role umgeht zwar immer Row-Level-Security (BYPASSRLS), braucht aber
-- trotzdem diese expliziten GRANTs, sonst schlägt jeder Zugriff mit
-- "permission denied for table ..." (Postgres-Fehlercode 42501) fehl.
grant usage on schema public to service_role;
grant all on all tables in schema public to service_role;
grant all on all sequences in schema public to service_role;
grant execute on all functions in schema public to service_role;
alter default privileges in schema public grant all on tables to service_role;
alter default privileges in schema public grant all on sequences to service_role;
alter default privileges in schema public grant execute on functions to service_role;
