create or replace view ledger.outstanding_receipts as
    select
        r.id as receipt_id,
        c.id as customer_id,
        rp.amount_cents as paid_cents,
        rt.amount_cents as total_cents,
        greatest(0, total_cents - paid_cents) as owing_cents,
    from data.receipts r
    inner join data.customers c on c.id = r.customer_id
    inner join ledger.receipt_paid rp on rp.receipt_id = r.id
    inner join ledger.receipt_total rt on rt.receipt_id = r.id
    where owing_cents > 0
    order by owing_cents desc;

grant select on view ledger.outstanding_receipts to application role app_admin;
