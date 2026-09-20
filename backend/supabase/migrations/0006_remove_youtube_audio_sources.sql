-- Migration 0006: YouTube- und Audio-Quellen entfernen
-- YouTube-Transkription war seit einiger Zeit unzuverlässig (YouTube ändert regelmäßig
-- die Mechanismen, über die inoffizielle Bibliotheken Transkripte abrufen), Audio-
-- Transkription wurde nie über einen einfachen Prototypen hinaus benötigt. Beide
-- Quellentypen werden ersatzlos gestrichen, analog zum bereits früher entfernten
-- Podcast/Audio-Overview-Feature. Übrig bleiben: PDF, Markdown, URL.

-- Bestehende YouTube-/Audio-Quellen zuerst löschen (per "on delete cascade" auf
-- chunks.source_id werden zugehörige Chunks automatisch mitgelöscht) — das muss VOR dem
-- Anlegen der strengeren CHECK-Constraint passieren, sonst würde diese Migration an
-- bestehenden Testdaten scheitern, die 'youtube' oder 'audio' als file_type haben.
delete from sources where file_type in ('youtube', 'audio');

-- Denselben Ansatz wie in 0004_more_source_types.sql: Der aktuell aktive Name des
-- file_type-CHECK-Constraints wird zur Laufzeit über den Systemkatalog ermittelt statt
-- geraten (0004 hat ihn explizit "sources_file_type_check" genannt, aber das nicht zu
-- wiederholen und stattdessen robust nachzuschlagen bleibt das sicherere Muster).
do $$
declare
  constraint_name text;
begin
  select conname into constraint_name
  from pg_constraint
  where conrelid = 'sources'::regclass
    and contype = 'c'
    and pg_get_constraintdef(oid) ilike '%file_type%';

  if constraint_name is not null then
    execute format('alter table sources drop constraint %I', constraint_name);
  end if;
end $$;

alter table sources add constraint sources_file_type_check
  check (file_type in ('pdf', 'md', 'url'));

-- Audio-MIME-Types wieder aus dem "sources"-Bucket entfernen, die in
-- 0004_more_source_types.sql hinzugefügt wurden — übrig bleiben PDF/Markdown/Plain-Text.
update storage.buckets
set allowed_mime_types = array[
  'application/pdf',
  'text/markdown',
  'text/x-markdown',
  'text/plain'
]
where id = 'sources';
