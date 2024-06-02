from typing import Optional
from snowflake.snowpark.session import Session
from snowflake.snowpark.functions import col, sum

def total_cost(unit_cost: int, quantity: int) -> int:
    return unit_cost * quantity

def create_new(session: Session, customer_id: str, region_id: str) -> int:
    """
    Creates a new receipt.
    """
    if not session.table("data.customers").filter(col("ID") == customer_id).count():
        raise ValueError(f"Customer with id={customer_id} does not exist")

    if not session.table("data.regions").filter(col("ID") == region_id).count():
        raise ValueError(f"Region with id={customer_id} does not exist")

    return session.sql(
        "insert into data.receipts (customer_id, region_id) values (?, ?) returning id",
        params=[customer_id, region_id]
    ).collect()[0]["ID"]


def add_item(session: Session, receipt_id: int, name: str, amount_cents: int, quantity: int) -> None:
    """
    Adds an item to an existing receipt.
    """
    if amount_cents <= 0:
        raise ValueError(f"Invalid amount of cents: {amount_cents}")
    
    if quantity <= 0:
        raise ValueError(f"Invalid quantity: {quantity}")

    if not session.table("data.receipts").filter(col("ID") == receipt_id).count():
        raise ValueError(f"Receipt with id={receipt_id} does not exist")

    session.sql(
        "insert into data.items (receipt_id, name, amount_cents, quantity) values (?, ?, ?, ?)",
        params=[receipt_id, name, amount_cents, quantity]
    ).collect()

    return None


def record_payment(session: Session, receipt_id: int, method: str, amount_cents: int) -> None:
    """
    Records a payment against this receipt on behalf of the customer.
    Overpayment is interpreted as a tip. Returns the remaining owing amount on
    the receipt (in cents), or 0 if the receipt has been paid in full / overpaid
    (tip).
    """
    if amount_cents <= 0:
        raise ValueError(f"Invalid amount of cents: {amount_cents}")
    
    if method is None or method.strip() == '':
        raise ValueError(f"Invalid method: {method}")

    if not session.table("data.receipts").filter(col("ID") == receipt_id).count():
        raise ValueError(f"Receipt with id={receipt_id} does not exist")

    session.sql(
        "insert into data.payments (receipt_id, method, amount_cents) values (?, ?, ?)",
        params=[receipt_id, method, amount_cents]
    ).collect()

    # return the amount the customer has left to pay
    outstanding = session.table("ledger.outstanding_receipts").filter(
        col("RECEIPT_ID") == receipt_id
    ).select(col("OWING_CENTS")).collect()

    return 0 if len(outstanding) == 0 else outstanding[0]["OWING_CENTS"]


def subtotal(session: Session, receipt_id: int) -> int:
    """
    Bill subtotal (all items x quantities totalled up), in cents.
    """
    if not session.table("data.receipts").filter(col("ID") == receipt_id).count():
        raise ValueError(f"Receipt with id={receipt_id} does not exist")
    
    return session.table('data.items').filter(
        col('RECEIPT_ID') == receipt_id
    ).agg(
        sum(col('AMOUNT_CENTS') * col('QUANTITY')).as_('SUM_LINE_TOTAL')
    ).collect()[0]['SUM_LINE_TOTAL']


def total(session: Session, receipt_id: int) -> int:
    """
    Total amount, after regional tax, in cents.
    """
    before_tax = subtotal(session, receipt_id)
    regions_df = session.table("data.regions")
    receipts_df = session.table("data.receipts")

    df = regions_df.join(receipts_df, regions_df.id == receipts_df.region_id)
    df = df.filter(receipts_df.id == receipt_id)
    region_tax_pct = df.select(regions_df.tax_amount_pct.alias("TAX_PCT")).collect()[0]["TAX_PCT"]

    return round(before_tax + before_tax * region_tax_pct)


def tip_percentage(session: Session, receipt_id: int) -> Optional[float]:
    """
    How much did the customer tip on this receipt (calculated
    by subtracting the owing amount from total payment)? Value
    returned in cents.
    """
    total_owed = total(session, receipt_id)
    if total_owed == 0:
        return None  # cannot divide by 0

    paid = session.table("data.payments").filter(
        col("RECEIPT_ID") == receipt_id
    ).agg(sum(col("AMOUNT_CENTS"))).collect()[0]["SUM(AMOUNT_CENTS)"]

    return (paid - total_owed) / total_owed
