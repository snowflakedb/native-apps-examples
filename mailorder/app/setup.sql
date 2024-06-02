create application role if not exists app_csr;
create application role if not exists app_admin;

create schema if not exists data;
    grant usage on schema data to application role app_csr;
    grant usage on schema data to application role app_admin;
    execute immediate from './data/regions.sql';
    execute immediate from './data/customers.sql';
    execute immediate from './data/receipts.sql';
    execute immediate from './data/items.sql';
    execute immediate from './data/payments.sql';
    execute immediate from './data/tax_transfers.sql';

create or alter versioned schema ledger;
    grant usage on schema ledger to application role app_admin;
    execute immediate from './ledger/receipt_paid.sql';
    execute immediate from './ledger/receipt_total.sql';
    execute immediate from './ledger/tax_collected_per_receipt.sql';
    execute immediate from './ledger/outstanding_receipts.sql';
    execute immediate from './ledger/outstanding_customers.sql';

create or alter versioned schema receipts;
    grant usage on schema receipts to application role app_csr;
    grant usage on schema receipts to application role app_admin;
    execute immediate from './receipts/add_item.sql';
    execute immediate from './receipts/create_new.sql';
    execute immediate from './receipts/record_payment.sql';
    execute immediate from './receipts/subtotal.sql';
    execute immediate from './receipts/tip_percentage.sql';
    execute immediate from './receipts/total_cost.sql';
    execute immediate from './receipts/total.sql';


create or alter versioned schema regions;
    grant usage on schema regions to application role app_csr;
    grant usage on schema regions to application role app_admin;
    execute immediate from './regions/record_tax_transfer.sql';
    execute immediate from './regions/tax_balances.sql';

create or alter versioned schema ui;
    grant usage on schema ui to application role app_csr;
    grant usage on schema ui to application role app_admin;
    execute immediate from './ui/receipts_ui.sql';
    execute immediate from './ui/ledger_ui.sql';
    execute immediate from './ui/tax_management_ui.sql';
    execute immediate from './ui/regions_management_ui.sql';
    execute immediate from './ui/customers_management_ui.sql';
