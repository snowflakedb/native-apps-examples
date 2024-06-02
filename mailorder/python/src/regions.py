from snowflake.snowpark.session import Session
from snowflake.snowpark.functions import col, sum
from snowflake.snowpark import DataFrame

def record_tax_transfer(session: Session, region_id: str, amount_cents: int) -> None:
    """
    Records a transfer of collected tax (e.g. HST in Ontario, Canada)
    from our business to the government collection agency.
    """
    session.sql(
        "insert into data.tax_transfers (region_id, amount_cents) values (?, ?)",
        params=[region_id, amount_cents]
    ).collect()

    return None


def tax_balances(session: Session) -> DataFrame:
    """
    Returns a table with our balances per-region. Positive values are
    where we owe collected tax, negative values means we have pre-/over-paid.
    
    :returns rows of (region_id, owing_cents).
    """

    tax_transfers_per_region_df = session.table('data.tax_transfers').group_by('region_id').agg(sum('AMOUNT_CENTS').alias('transferred'))
    tax_collected_per_region_df = session.table('ledger.tax_collected_per_receipt').group_by('region_id').agg(sum('COLLECTED_TAX_CENTS').alias('owed'))
    regions_df = session.table('data.regions')

    regions_and_transfers = regions_df.join(tax_transfers_per_region_df, col('id') == col('region_id'), how='left').select(col('id').alias('region_id'), col('transferred'))
    summary = regions_and_transfers.join(tax_collected_per_region_df, on='region_id', how='left').select(regions_and_transfers.region_id, col('owed'), col('transferred'))
    summary_with_defaults = summary.na.fill({'owed': 0, 'transferred': 0})  # sets defaults for missing values
    return summary_with_defaults.select(col('region_id'), col('owed') - col('transferred'))
