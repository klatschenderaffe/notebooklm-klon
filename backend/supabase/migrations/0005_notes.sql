-- Migration 0005: Notizen pro Quelle
-- Einfache Freitext-Notizen, die Nutzer zu einer einzelnen Quelle hinzufügen können
-- (kein Text-Highlighting/Viewer, wie besprochen). Analog zu "chunks" gibt es keine
-- eigene user_id-Spalte — Eigentümerschaft wird über die Kette notes -> sources ->
-- notebooks -> auth.users geprüft (Backend filtert zusätzlich explizit in jeder Query,
-- RLS hier ist Tiefenverteidigung).

create table if not exists notes (
  id uuid primary key default gen_random_uuid(),
  source_id uuid not null references sources (id) on delete cascade,
  content text not null,
  created_at timestamptz not null default now()
);

create index if not exists notes_source_id_idx on notes (source_id, created_at);

alter table notes enable row level security;

create policy "Nutzer sehen nur Notizen eigener Quellen" on notes
  for all
  using (exists (
    select 1 from sources
    join notebooks on notebooks.id = sources.notebook_id
    where sources.id = notes.source_id and notebooks.user_id = auth.uid()
  ))
  with check (exists (
    select 1 from sources
    join notebooks on notebooks.id = sources.notebook_id
    where sources.id = notes.source_id and notebooks.user_id = auth.uid()
  ));

grant all on notes to service_role;
