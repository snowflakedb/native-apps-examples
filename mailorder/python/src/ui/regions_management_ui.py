def run_streamlit():
    import streamlit as st
    from snowflake.snowpark.functions import col
    from snowflake.snowpark import Session

    session = Session.builder.getOrCreate()
    
    st.title("Manage Regions")

    st.header("Regions")
    regions_df = session.table("data.regions").select(col('ID'), col('NAME'), (col('TAX_AMOUNT_PCT') * 100).alias('TAX_PERCENTAGE'), col('CREATED_AT'))
    st.dataframe(regions_df.to_pandas(), use_container_width=True)

    st.header("Add Region")
    region_id = st.text_input("Region Id, will not be visible", key='regionId')
    region_name = st.text_input("Region Name, will be visible in dropdown", key='regionName')
    tax_percent = st.number_input("Tax Percentage in that region, e.g. 5 %", value=0, key='taxPercent')

    def add_region_button():
        session.sql(
            "insert into data.regions(id, name, tax_amount_pct, created_at) values (?, ?, ?, current_timestamp())",
            params=[region_id, region_name, tax_percent/100]
        ).collect()

    st.button("Add Region", on_click=add_region_button, key='addRegion')

if __name__ == '__main__':
    run_streamlit()
