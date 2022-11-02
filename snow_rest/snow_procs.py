from snowflake.snowpark.functions import col
import snowflake.snowpark.functions as f
import os
import logging
import datetime

# Set Logging Level
logger = logging.getLogger()
logger.setLevel(logging.INFO)

table = os.getenv('SNOW_TABLE')

def busy_airports(session, begin, end, deparr, nrows):
    df = session.table(table)
    if begin and end:
        try:
            d_begin = datetime.date.fromisoformat(begin)
            d_end = datetime.date.fromisoformat(end)
            df = df.filter((col('FLIGHT_DATE') >= d_begin) & (col('FLIGHT_DATE') <= d_end))
        except Exception as ex:
            logger.warning('Bad dates provided. Querying without date range: ' + str(ex))
    deparr = deparr if deparr == 'ARRAPT' else 'DEPAPT'
    try:
        nrows = int(nrows)
    except:
        nrows = 20
    df = df.group_by(col(deparr)) \
                    .agg(f.count(deparr).alias('ct')) \
                    .sort(col('ct').desc()) \
                    .limit(nrows) 
    try:
        retval = [x.as_dict() for x in df.to_local_iterator()]
    except Exception as ex:
        logger.error('Failed to retrieve data frame: ' + str(ex))
        raise
    return retval

def airport_daily(session, apt, begin, end):
    df = session.table(table)
    if begin and end:
        df = df.filter((col('FLIGHT_DATE') >= begin) & (col('FLIGHT_DATE') <= end))
    df = df.group_by(col('FLIGHT_DATE')) \
        .agg([ \
                f.sum(f.when(col('DEPAPT') == apt, f.lit(1)).otherwise(f.lit(0))).alias('depct'), \
                f.sum(f.when(col('ARRAPT') == apt, f.lit(1)).otherwise(f.lit(0))).alias('arrct') \
            ]) \
        .sort(col('FLIGHT_DATE').asc())
    try:
        retval = [x.as_dict() for x in df.to_local_iterator()]
    except Exception as ex:
        logger.error('Failed to retrieve data frame: ' + str(ex))
        raise
    return retval

airline_list = {
        'AA':'American', 
        'DL':'Delta', 
        'UA':'United', 
        'B6':'JetBlue', 
        'WN':'Southwest', 
        'AS':'Alaska'
    }
def airport_daily_carriers(session, apt, begin, end, deparr):
    df = session.table(table)
    if begin and end:
        try:
            d_begin = datetime.date.fromisoformat(begin)
            d_end = datetime.date.fromisoformat(end)
            df = df.filter((col('FLIGHT_DATE') >= d_begin) & (col('FLIGHT_DATE') <= d_end))
        except Exception as ex:
            logger.warning('Bad dates provided. Querying without date range: ' + str(ex))
    deparr = deparr if deparr == 'ARRAPT' else 'DEPAPT'
    df = df.filter(col('CARRIER').isin(list(airline_list.keys()))) \
        .filter(col(deparr) == apt) \
        .group_by([col('FLIGHT_DATE'), col('CARRIER')]) \
        .agg(f.count('FLIGHT_DATE').alias('ct')) \
        .sort(col('FLIGHT_DATE').asc())
    try:
        retval = [x.as_dict() for x in df.to_local_iterator()]
    except Exception as ex:
        logger.error('Failed to retrieve data frame: ' + str(ex))
        raise
    return retval

