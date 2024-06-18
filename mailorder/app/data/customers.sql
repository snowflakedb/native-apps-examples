create table if not exists
    data.customers (
        id text not null primary key,
        name text not null,
        created_at timestamp not null default current_timestamp()
    );

grant select on data.customers to application role app_csr;
grant select, insert, update, delete, truncate on data.customers to application role app_admin;
