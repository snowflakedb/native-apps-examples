from flask import Blueprint, request, abort, make_response, jsonify
import datetime
import logging
import snowflake.snowpark.functions as f

import spcs_helpers
session = spcs_helpers.session()

# Make the API endpoints
snowpark = Blueprint('snowpark', __name__)

dateformat = '%Y-%m-%d'

## Top clerks in date range
@snowpark.route('/top_clerks')
def top_clerks():
    # Validate arguments
    sdt_str = request.args.get('start_range') or '1995-01-01'
    edt_str = request.args.get('end_range') or '1995-03-31'
    topn_str = request.args.get('topn') or '10'
    try:
        sdt = datetime.datetime.strptime(sdt_str, dateformat)
        edt = datetime.datetime.strptime(edt_str, dateformat)
        topn = int(topn_str)
    except:
        abort(400, "Invalid arguments.")
    try:
        df = session.sql("SELECT * FROM Reference('ORDERS_TABLE')") \
                .filter(f.col('O_ORDERDATE') >= sdt) \
                .filter(f.col('O_ORDERDATE') <= edt) \
                .group_by(f.col('O_CLERK')) \
                .agg(f.sum(f.col('O_TOTALPRICE')).as_('CLERK_TOTAL')) \
                .order_by(f.col('CLERK_TOTAL').desc()) \
                .limit(topn)
        return make_response(jsonify([x.as_dict() for x in df.to_local_iterator()]))
    except Exception as e:
        logging.exception("message")
        abort(500, "Error reading from Snowflake. Check the logs for details.")

