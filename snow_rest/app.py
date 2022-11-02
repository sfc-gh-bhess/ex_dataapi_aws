import json
import datetime
import logging

import snow_procs
import snow_session

# Set Logging Level
logger = logging.getLogger()
logger.setLevel(logging.INFO)

## HELPERS
date_str = "%Y-%m-%d"
datetime_str = f"{date_str}T%H:%M:%S"
def stringify(doc):
    if (type(doc) == str):
        return doc
    if (type(doc) == dict):
        for k, v in doc.items():
            doc[k] = stringify(v)
    if (type(doc) == list):
        for i in range(len(doc)):
            doc[i] = stringify(doc[i])
    if (type(doc) == datetime.datetime):
        doc = doc.strftime(datetime_str)
    if (type(doc) == datetime.date):
        doc = doc.strftime(date_str)
    return doc

def get_parameter(event, pkey, key):
    return event.get(pkey).get(key) if event.get(pkey) else None

def wrap_return(body):
    return {
        'statusCode': 200,
        'body': json.dumps(stringify(body))
    }

session = snow_session.get_db_client()

def lambda_handler_busy_airports(event, context):
    logger.info(f"EVENT: {json.dumps(event)}")
    begin = get_parameter(event, 'queryStringParameters', 'begin')
    end = get_parameter(event, 'queryStringParameters', 'end')
    deparr = get_parameter(event, 'queryStringParameters', 'deparr')
    nrows = get_parameter(event, 'queryStringParameters', 'nrows')
    return wrap_return(snow_procs.busy_airports(session, begin, end, deparr, nrows))

def lambda_handler_airport_daily(event, context):
    logger.info(f"EVENT: {json.dumps(event)}")
    airport = get_parameter(event, 'pathParameters', 'airport')
    begin = get_parameter(event, 'queryStringParameters', 'begin')
    end = get_parameter(event, 'queryStringParameters', 'end')
    return wrap_return(snow_procs.airport_daily(session, airport, begin, end))

def lambda_handler_airport_daily_carriers(event, context):
    logger.info(f"EVENT: {json.dumps(event)}")
    airport = get_parameter(event, 'pathParameters', 'airport')
    begin = get_parameter(event, 'queryStringParameters', 'begin')
    end = get_parameter(event, 'queryStringParameters', 'end')
    deparr = get_parameter(event, 'queryStringParameters', 'deparr')
    return wrap_return(snow_procs.airport_daily_carriers(session, airport, begin, end, deparr))

