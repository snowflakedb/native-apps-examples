create or replace view ledger.outstanding_customers as
    select
        c.id as customer_id,
        sum(outr.owing_cents) as owing_cents,
        listagg(outr.receipt_id, ',') as receipts_owing
    from data.customers c
    inner join ledger.outstanding_receipts outr on outr.customer_id = c.id
    group by c.id;

grant select on view ledger.outstanding_customers to application role app_admin;
