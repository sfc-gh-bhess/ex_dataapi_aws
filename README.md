# ex_dataapi_aws
Blog Example for Snowflake Data API on AWS

This repository is an example of building a data API on data hosted
in Snowflake. It accompanies this Medium post describing how to build
APIs in AWS to data in Snowflake.

## REST API for OAG Flight Schedule data
This example puts a simple data API to answer some basic questions of
the OAG Flight Schedule data in the Snowflake Marketplace.

The data is available in the Snowflake Marketplace [here](https://app.snowflake.com/marketplace/listing/GZ1M7Z2MQ39).

There are 3 API endpoints for this data:
* `busy_airports` - this will list the top airpots in terms of flight departures (or arrivals). It can be
  customized with the following optional parameters:
  * `deparr` - whether to consider departures (`DEPAPT`) or arrivals (`ARRAPT`). Default is `DEPAPT`.
  * `nrows` - how many airports to show. Default is `20`.
  * `begin` - start date to include. Default is all the data.
  * `end` - end date to include. Default is all the data.
* `airport_daily` - this will show the daily departures and arrivals for the specified airport. 
  The airport code is included as a path variable (i.e., `/airport_daily/{airport_code}`).
  * `airport_code` - the 3-letter airport code to consider. Required.
  * `begin` - start date to include. Default is all the data.
  * `end` - end date to include. Default is all the data.
* `airport_daily_carriers` - this will show the daily departures (or arrivals) for various 
  airline carriers for the specified airport. The airport code is included as a path variable
  (i.e., `/airport_daily_carriers/{airport_code})
  * `airport_code` - the 3-letter airport code to consider. Required.
  * `deparr` - whether to consider departures (`DEPAPT`) or arrivals (`ARRAPT`). Default is `DEPAPT`.
  * `begin` - start date to include. Default is all the data.
  * `end` - end date to include. Default is all the data.

The `busy_airports` and `airport_daily` endpoints are accessed via the `GET` verb. 
The `airport_daily_carriers` endpiont is accessed via the `POST` verb.
All parameters (other than the `airport_code`, which is supplied as a path variable) are 
supplied as query parameters.

## Snowflake Setup for Example
To deploy this example you will need to get the OAG Flight Schedule data imported into your
Snowflake account. It is advised to create a role to access this data, and create a user (and password)
that the example will use to access this data, and grant that user the role. This user/password
will be used by the AWS Lambda functions to access Snowflake.

To deploy the API via AWS SAM you will need to provide the following information about 
your Snowflake setup:
* Snowflake account identifier
* Snowflake username - who has access to the OAG data share in your account
* Snowflake password
* Snowflake warehouse to use
* Name of the database in your Snowflake account that houses the imported OAG data share.

## AWS Stack for Example
This repo is a SAM application and can be deployed using the AWS Serverless Application
Model (see [here](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) 
for more information).

The stack will deploy the following resources:
* AWS Lambda layer for the Snowflake Snowpark Python package
* AWS Lambda function to find the busy airports
* AWS Lambda function to calculate the number of daily flights from/to a given airport
* AWS Lambda function to calculate the number of daily flights for a number of carriers from/to a given airport.
* AWS Lambda function to provide simple username/password authentication to protect the API
* Permissions to allow API Gateway to call the Lambda functions.
* API Gateway API to expose the 3 API endpoints

To build and deploy the stack, you will need to have installed and configured AWS SAM. 
See the AWS SAM documentation for more informaiton.

To build the stack, run:
```
make build
```

To deploy the stack, run:
```
make deploy
```

and answer the interactive questions. In addition to the Snowflake information, you
will need to provide a "prefix", which is a string that will be prepended to all
resources created by the SAM stack, and a username/password to protect the REST API.

The URL for the root of the API will be an output from the `make deploy` command.

## Testing the API

### Example Queries
In the following examples, `APIROOT` is the output from the stack, `WEBUSER` is the
username to protect the API, and `WEBPASSWORD` is the password to protect the API.

1. Show the 20 busiest airports based on departures using the full data set:
```
curl -u {WEBUSER}:{WEBPASSWORD} https://{APIROOT}/busy_airports
```

2. Show the 10 busiest airports based on arrivals in the date range of July 1-5, 2022:
```
curl -u {WEBUSER}:{WEBPASSWORD} https://{APIROOT}/busy_airports?deparr=ARRAPT&nrows=10&begin=2022-07-01&end=2022-07-05
```

3. Show the daily departures and arrivals for `BOS` in the date range of July 1-5, 2022:
```
curl -u {WEBUSER}:{WEBPASSWORD} https://{APIROOT}/airport_daily/BOS?begin=2022-07-01&end=2022-07-05
```

4. Show the daily arrivals for select carriers for `BOS` in the date range of July 1-5, 2022:
```
curl -X POST -u {WEBUSER}:{WEBPASSWORD} https://{APIROOT}/airport_daily_carriers/BOS?begin=2022-07-01&end=2022-07-05&deparr=ARRAPT
```

### Test Webpage
This repository also includes a simple HTML/JavaScript page that will allow you to
test the API. To mimic a real webserver, you can launch a local webserver via Python:
```
python -m http.server
```

Then navigate to the `index.html` page in this repository. There you will see a form where
you can choose `GET` or `POST`, fill in the endpoint and query parameters, and enter the
API username and password. This will also test the CORS situation, as well.

## Beyond This Example
While this example is fully functional, it does have some simplifications that might not
be sufficient for production. This repository is provided as an example and it is intended 
that you will modify and enhance as suits your needs. Here is a list of some areas you 
may consider to make more production-ready:
* The API is protected with simple username/password authentication. That authentication
  is integrated into Amazon API Gateway, but API Gateway provides other options for securing
  the API, such as Amazon Cognito. Username/password is the simplest form of protection, and
  production-ready solutions should look at more rigorous options, such as Cognito. 
* This example has AWS Lambda connect to Snowflake using username/password authentication.
  This is a simple way to connect, and was concise for this example. However, in production
  you would likely want to use [keypair](https://docs.snowflake.com/en/user-guide/key-pair-auth.html)
  authentication. Keypair authentication supports rotating credentials with zero downtime,
  which is important for production applications.
* You will want to make sure that your API connects to Snowflake as an application user
  and is granted narrow permissions via Snowflake RBAC. Connecting as a user with `ACCOUNTADMIN`, 
  for example, while being convenient is a high security risk.
