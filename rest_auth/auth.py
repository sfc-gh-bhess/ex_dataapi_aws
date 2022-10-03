import os
import base64

def lambda_handler(event, context):
  print(event)
  action = "Allow"
  authorization = None
  # methodArn for REST API, routeArn for HTTP API
  methodArn = event["methodArn"] if "methodArn" in event else event["routeArn"]
  if "Authorization" in event["headers"]:
      authorization = event["headers"]["Authorization"]
  if "authorization" in event["headers"]:
      authorization = event["headers"]["authorization"]
  if None == authorization:
      action = "Deny"
  splits = base64.b64decode(authorization.split(" ")[-1]).decode("utf-8").split(":")
  username = splits[0]
  password = splits[1]
  if (username != os.environ["USERNAME"] or password != os.environ["PASSWORD"]):
      print("Invalid username or password")
      action = "Deny"

  return buildPolicy(methodArn, username, action)

def buildPolicy(methodArn, principalId, action):
  splits = methodArn.split(":")
  awsRegion = splits[3]
  awsAccountId = splits[4]
  apisplits = splits[5].split("/")
  restApiId = apisplits[0]
  apiStage = apisplits[1]
  apiArn = "arn:aws:execute-api:" + awsRegion + ":" + awsAccountId + ":" + restApiId + "/" + apiStage + "/*/*"

  policy = {
      "principalId": principalId,
      "policyDocument": {
          "Version": "2012-10-17",
          "Statement": [
              {
                  "Action": "execute-api:Invoke",
                  "Effect": action,
                  "Resource": [apiArn]
              }
          ]
      }
  }
  return policy
