# this function is used to send session details back to browser when a signalling server is available to process it
# the response includes the query string for the signalling server and it uses the websocket connection id to interface
# back with the client
import boto3
import json
import os
import logging


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
  
  
  print(event)
  inputParams = {
                "signallingServer"   : event["signallingServer"]
            }
  apigateway=boto3.client('apigatewaymanagementapi' ,endpoint_url=os.environ["ApiGatewayUrl"])
  apigateway.post_to_connection(ConnectionId=event["connectionId"], Data=json.dumps(inputParams))
           
  logger.info("Sent server details to frontend ! ")
  return {
    'statusCode': 200,
    'body': json.dumps('Completed sending server details to backend')    
  }
