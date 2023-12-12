# this function is used to poll the SQS queue for new session request and then check if
# a Signalling instance is already available to service the nequest or needs to be created
# this function should be run on a schedule
import boto3
import json
import os
import json
import logging
import urllib.request
import urllib.error

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    
    lambdaFunc=boto3.client('lambda')
    
    lambdaArnSendSesionDetails=''
    lambdaArnCreateInstances=''
    
    response= lambdaFunc.get_function(
        FunctionName='sendSessionDetails'
        )
    lambdaArnSendSesionDetails=response['Configuration']['FunctionArn']
    response= lambdaFunc.get_function(
        FunctionName='createInstances'
        )
    lambdaArnCreateInstances=response['Configuration']['FunctionArn']
    response= lambdaFunc.get_function(
        FunctionName='keepConnectionAlive'
        )
    lambdaArnKeepAlive=response['Configuration']['FunctionArn']
    
    ssm = boto3.client('ssm')
    parameter = ssm.get_parameter(Name='matchmakerclientsecret')
    matchmakersecret = parameter['Parameter']['Value']
  
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName=os.environ["SQSName"])
    for message in queue.receive_messages():
        logger.info(message.body)
        
        payload=json.loads(message.body)
        
        # send a keep alive message to frontend
        lambdaFunc.invoke(
            FunctionName = lambdaArnKeepAlive,
            InvocationType = 'RequestResponse',
            Payload = json.dumps(payload)
        )
        
        
        logger.info("Connection id is "+payload["connectionId"])
        logger.info("Endpoints id is "+os.environ["MatchMakerURL"] +". "+matchmakersecret)
        # we make a call to matchmaker endpoint to check if a Signalling instance is available to service the request
        try:
            response = urllib.request.urlopen(urllib.request.Request(
                url=os.environ["MatchMakerURL"],
                headers={"clientsecret":matchmakersecret},
                method='GET'),
                timeout=5)
          
            if(response.status==200):
                responsePayload=response.read()
                JSON_object = json.loads(responsePayload.decode("utf-8"))
                payload.update(JSON_object)
            
                # a 200 response from Matchmaker indicates a Signalling server is available to to service request.
                # the matchmaker returns the Signalling server instanceID which is forwarded to sendSessionDetails
                response = lambdaFunc.invoke(
                    FunctionName = lambdaArnSendSesionDetails,
                    InvocationType = 'RequestResponse',
                    Payload = json.dumps(payload)
                )
            
            message.delete()
            logger.info("Found server to service request "+responsePayload.decode("utf-8"))
            #break
        except urllib.error.HTTPError as err:
            if(err.code==400):
                logger.info("No server to service request ")
                inputParams = {
                    "Key"   : "value"
                }
                # since no servers were found to service the request, we make a call to createInstance to create a new
                # Signalling server in case we are not running on capacity
                lambdaFunc.invoke(
                    FunctionName = lambdaArnCreateInstances,
                    InvocationType = 'Event',
                    Payload = json.dumps(inputParams)
                )
                # noticed the message is not deleted here since we could not service it with a Signalling server instanceID
            else:
                raise err

    return {
        'statusCode': 200,
        'body': json.dumps('Completed scanning for incoming requests')
    }
