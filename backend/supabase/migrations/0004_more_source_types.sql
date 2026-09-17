-- Migration 0004: Weitere Quellentypen (URL, YouTube, Audio)
-- Erweitert sources.file_type um 'url', 'youtube', 'audio' und die Audio-MIME-Types im
-- bestehenden "sources"-Bucket (bislang nur PDF/Markdown erlaubt).

-- Der ursprüngliche CHECK-Constraint wurde in 0001_initial_schema.sql inline in der
-- Spaltendefinition angelegt; Postgres vergibt dafür automatisch einen Namen, der nicht
-- garantiert "sources_file_type_check" lautet. Name daher zur Laufzeit über den
-- Systemkatalog ermitteln statt zu raten, damit die Migration unabhängig vom tatsächlich
-- vergebenen Namen funktioniert.
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
  check (file_type in ('pdf', 'md', 'url', 'youtube', 'audio'));

-- URL- und YouTube-Quellen werden als extrahierter Text im selben Bucket wie PDF/MD
-- abgelegt (als text/markdown, konsistent mit den bestehenden Markdown-Quellen).
-- Audio-Quellen behalten ihr Original-Format bei, damit die hochgeladene Datei bei
-- Bedarf unverändert erhalten bleibt.
update storage.buckets
set allowed_mime_types = array[
  'application/pdf',
  'text/markdown',
  'text/x-markdown',
  'text/plain',
  'audio/mpeg',
  'audio/wav',
  'audio/x-wav',
  'audio/mp4',
  'audio/x-m4a',
  'audio/ogg'
]
where id = 'sources';
