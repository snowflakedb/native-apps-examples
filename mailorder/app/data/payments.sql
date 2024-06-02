create table if not exists
    data.payments (
        receipt_id integer not null references data.receipts(id),
        method text not null,
        amount_cents integer not null,
        created_at timestamp not null default current_timestamp()
    );

grant select, insert on data.payments to application role app_csr;
grant select, insert, update, delete, truncate on data.payments to application role app_admin;
