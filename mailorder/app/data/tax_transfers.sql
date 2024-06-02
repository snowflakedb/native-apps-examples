create table if not exists
    data.tax_transfers (
        region_id text not null references data.regions(id),
        amount_cents integer not null,
        created_at timestamp not null default current_timestamp()
    );
