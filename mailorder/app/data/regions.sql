create table if not exists
    data.regions (
        id text not null primary key,
        name text not null,
        tax_amount_pct numeric(8, 7) not null,
        created_at timestamp not null default current_timestamp()
    );

grant select on data.regions to application role app_csr;
grant select, insert, update, delete, truncate on data.regions to application role app_admin;
