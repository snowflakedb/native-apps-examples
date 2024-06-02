create sequence if not exists data.receipt_id_seq;
create table if not exists
    data.receipts (
        id integer not null primary key default data.receipt_id_seq.NEXTVAL,
        customer_id text not null references data.customers(id),
        region_id text not null references data.regions(id),
        created_at timestamp not null default current_timestamp()
    );

grant select on data.receipts to application role app_csr;
grant select, insert, update, delete, truncate on data.receipts to application role app_admin;
