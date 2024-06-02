create or replace view ledger.receipt_total as
    select
        r.id as receipt_id,
        SUM(i.amount_cents * i.quantity) as amount_cents
    from data.receipts r
    left join data.items i ON i.receipt_id = r.id
    group by r.id;

grant select on view ledger.receipt_total to application role app_admin;
