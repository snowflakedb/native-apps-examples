create or replace view ledger.receipt_paid as
    select
        r.id as receipt_id,
        SUM(p.amount_cents) as amount_cents,
        MAX(p.created_at) as last_payment_at
    from data.receipts r
    left join data.payments p ON p.receipt_id = r.id
    group by r.id;

grant select on view ledger.receipt_paid to application role app_admin;
