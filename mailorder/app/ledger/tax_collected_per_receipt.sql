create or replace view ledger.tax_collected_per_receipt as
    select
        r.id as receipt_id,
        reg.id as region_id,
        least(rp.amount_cents, rt.amount_cents) as collected_taxable_cents,
        cast(round(collected_taxable_cents * reg.tax_amount_pct) as int) as collected_tax_cents
    from data.receipts r
    inner join data.regions reg on reg.id = r.region_id
    inner join ledger.receipt_paid rp on rp.receipt_id = r.id
    inner join ledger.receipt_total rt on rt.receipt_id = r.id
    where collected_taxable_cents > 0;

grant select on view ledger.tax_collected_per_receipt to application role app_admin;
