# this function is used to keep the web socket connection between browser and API gateway alive, till a session is available
import boto3
import json
import os
import logging


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
  
  
  print(event)
  inputParams = {
                "status"   : 'waiting for session!'
            }
  apigateway=boto3.client('apigatewaymanagementapi' ,endpoint_url=os.environ["ApiGatewayUrl"])
  apigateway.post_to_connection(ConnectionId=event["connectionId"], Data=json.dumps(inputParams))
           
  logger.info("Sent server details to frontend ! ")
  return {
    'statusCode': 200,
    'body': json.dumps('Completed sending server details to backend')    
  }
