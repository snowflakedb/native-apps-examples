create table if not exists
    data.items (
        receipt_id integer not null references data.receipts(id),
        name text not null,
        amount_cents integer not null,
        quantity integer not null default 1,
        created_at timestamp not null default current_timestamp()
    );

grant select, insert on data.items to application role app_csr;
grant select, insert, update, delete, truncate on data.items to application role app_admin;
