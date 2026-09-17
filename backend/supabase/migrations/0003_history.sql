-- Migration 0003: Verlauf für Chats und Präsentationen
-- Persistiert jede Chat-Nachricht und jede generierte Präsentation pro Notebook, damit
-- Nutzer beides später wiederfinden können (History-Ansicht im Frontend).

create table if not exists chat_messages (
  id uuid primary key default gen_random_uuid(),
  notebook_id uuid not null references notebooks (id) on delete cascade,
  role text not null check (role in ('user', 'assistant')),
  content text not null,
  citations jsonb not null default '[]'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists chat_messages_notebook_id_idx on chat_messages (notebook_id, created_at);

create table if not exists presentations (
  id uuid primary key default gen_random_uuid(),
  notebook_id uuid not null references notebooks (id) on delete cascade,
  title text not null,
  topic text not null,
  storage_path text not null,
  design jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists presentations_notebook_id_idx on presentations (notebook_id, created_at);

alter table chat_messages enable row level security;
alter table presentations enable row level security;

create policy "Nutzer sehen nur Chat-Nachrichten eigener Notebooks" on chat_messages
  for all
  using (exists (
    select 1 from notebooks
    where notebooks.id = chat_messages.notebook_id and notebooks.user_id = auth.uid()
  ))
  with check (exists (
    select 1 from notebooks
    where notebooks.id = chat_messages.notebook_id and notebooks.user_id = auth.uid()
  ));

create policy "Nutzer sehen nur Präsentationen eigener Notebooks" on presentations
  for all
  using (exists (
    select 1 from notebooks
    where notebooks.id = presentations.notebook_id and notebooks.user_id = auth.uid()
  ))
  with check (exists (
    select 1 from notebooks
    where notebooks.id = presentations.notebook_id and notebooks.user_id = auth.uid()
  ));

grant all on chat_messages to service_role;
grant all on presentations to service_role;

-- Eigener Storage-Bucket für generierte Präsentationen statt Wiederverwendung des
-- "sources"-Buckets: dieser hat eine MIME-Type-Restriktion auf PDF/Markdown, die PPTX-
-- Dateien ablehnen würde. Bucket-Erstellung per SQL statt manuell im Dashboard, damit
-- sie versioniert und reproduzierbar ist (funktioniert äquivalent zur Dashboard-UI, da
-- beide direkt in storage.buckets schreiben).
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values (
  'presentations',
  'presentations',
  false,
  52428800, -- 50 MB
  array['application/vnd.openxmlformats-officedocument.presentationml.presentation']
)
on conflict (id) do nothing;
