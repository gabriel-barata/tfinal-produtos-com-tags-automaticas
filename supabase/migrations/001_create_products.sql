create table if not exists products (
  id          bigint generated always as identity primary key,
  name        text not null check (char_length(name) between 2 and 120),
  description text not null check (char_length(description) between 10 and 1000),
  tags        text[] not null,
  created_at  timestamptz not null default now()
);

-- RLS ligado e SEM policies: bloqueia acesso pela API REST pública do Supabase (anon).
-- O backend conecta como `postgres`, que ignora RLS.
alter table products enable row level security;
