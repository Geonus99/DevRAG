create extension if not exists vector;

create table if not exists knowledge_sources (
    id uuid primary key default gen_random_uuid(),
    source_name text not null,
    source_url text not null,
    source_type text not null check (source_type in ('URL', 'PDF')),
    status text not null default 'PENDING' check (status in ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED')),
    crawled_pages integer not null default 0,
    chunk_count integer not null default 0,
    error_message text,
    created_at timestamptz not null default now()
);

create table if not exists ingestion_jobs (
    id uuid primary key default gen_random_uuid(),
    source_id uuid not null references knowledge_sources(id) on delete cascade,
    status text not null default 'PROCESSING' check (status in ('PROCESSING', 'COMPLETED', 'FAILED')),
    started_at timestamptz not null default now(),
    completed_at timestamptz,
    error_message text
);

create table if not exists document_chunks (
    id uuid primary key default gen_random_uuid(),
    source_id uuid not null references knowledge_sources(id) on delete cascade,
    title text,
    content text not null,
    chunk_index integer not null,
    token_count integer not null default 0,
    page_url text,
    embedding vector(1536) not null,
    created_at timestamptz not null default now()
);

create table if not exists chat_sessions (
    id uuid primary key default gen_random_uuid(),
    title text not null,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists chat_messages (
    id uuid primary key default gen_random_uuid(),
    session_id uuid not null references chat_sessions(id) on delete cascade,
    role text not null check (role in ('user', 'assistant')),
    message text not null,
    token_usage integer,
    created_at timestamptz not null default now()
);

create table if not exists source_references (
    id uuid primary key default gen_random_uuid(),
    message_id uuid not null references chat_messages(id) on delete cascade,
    chunk_id uuid not null references document_chunks(id) on delete cascade,
    relevance_score double precision
);

create index if not exists document_chunks_embedding_idx
    on document_chunks using ivfflat (embedding vector_cosine_ops)
    with (lists = 100);

create or replace function match_document_chunks(
    query_embedding vector(1536),
    match_count int default 5
)
returns table (
    id uuid,
    source_id uuid,
    title text,
    content text,
    chunk_index integer,
    token_count integer,
    page_url text,
    relevance_score double precision,
    created_at timestamptz
)
language sql
stable
as $$
    select
        document_chunks.id,
        document_chunks.source_id,
        document_chunks.title,
        document_chunks.content,
        document_chunks.chunk_index,
        document_chunks.token_count,
        document_chunks.page_url,
        1 - (document_chunks.embedding <=> query_embedding) as relevance_score,
        document_chunks.created_at
    from document_chunks
    order by document_chunks.embedding <=> query_embedding
    limit match_count;
$$;
