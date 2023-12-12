# this function is used to request for a new streaming session. The function is triggered by the API gateway websocket
# endpoint. The function validates the websocket message to check if the source is valid(by checking bearer) and then
# pushes the session request to a FIFO queue. the request body also includes the socket connection id for further
# connection with the browser

import boto3
import json
import os
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
  print(event)
  
  sqs = boto3.resource("sqs")
  logger.info(os.environ["SQSName"])
  queue = sqs.get_queue_by_name(QueueName=os.environ["SQSName"])
  
  messageReqId=event["requestContext"]["requestId"]
  messageConnId=event["requestContext"]["connectionId"]
  messageReqBody=event["body"]
  secretParam=(json.loads(messageReqBody))['bearer']
  print("secretParam "+secretParam)
  uniqueId=str(event["requestContext"]["requestTimeEpoch"])
  
  # validate the websocket message to check if it originated from a valid source
  if(secretParam==os.environ["clientSecret"]):
    payload = json.dumps({'requestId': messageReqId, 'connectionId': messageConnId,'body':json.loads(messageReqBody) })
    logger.info(payload)
    logger.info("Sending message to SQS")
    queue.send_message(MessageBody=payload,MessageGroupId=messageReqId,MessageDeduplicationId=uniqueId)
  else :
    logger.info('Invalid client !')
  
  return {
    'statusCode': 200,
    'body': json.dumps('Message posted to Q !')    
  }
