# this function is used to terminate Signalling server instances. The user data script for Signalling server includes a logic
# to stop the instance after a predefined period like 20 minutes. Once instance moved to stopped state, an Event bridge rule
# triggers this function to terminate the stopped instance
# a varriation of the Event Bridge rule also triggers ths function on schedule, passing the paramater stopAllServers=true in event
# causing all Signalling servers to be terminated at the same time

import boto3
import json
import os
import json
from boto3.dynamodb.conditions import Attr

def lambda_handler(event, context):
  
  # get all TG to instance mapping from dynamoDB to remove mapping later during termination
  dynamodb = boto3.resource('dynamodb')
  table = dynamodb.Table('instanceMapping')
  response = table.scan(FilterExpression=Attr('InstanceID').ne(''))
  instanceMapping={}
  for item in response['Items']:
      instanceMapping[item['InstanceID']]=item['TargetGroup']
  print(json.dumps(instanceMapping))
  
  if("stopAllServers" in event):
        if(event["stopAllServers"]):
          ec2 = boto3.client('ec2')
          allInstances=[]
          response = ec2.describe_instances(Filters=[{'Name': 'tag:type', 'Values': ['signalling']}])
          for reservation in response['Reservations']:
            instanceID=reservation['Instances'][0]['InstanceId']
            print('Found instance id '+instanceID)
            allInstances.append(instanceID)
            # remove instance mapping from dynamoDb table
            table.update_item(
              Key={
                'TargetGroup': instanceMapping[instanceID],
                },
                UpdateExpression="set InstanceID = :i",
                ExpressionAttributeValues={
                    ':i': ''
                    }
            )
          print('will terminate all signalling instances ')
          ec2.terminate_instances(InstanceIds=allInstances)
  else:
          instanceId=event["detail"]["instance-id"]
          ec2 = boto3.client('ec2')
          # describe instance based on instance id
          response = ec2.describe_instances(InstanceIds=[instanceId],Filters=[{'Name': 'tag:type', 'Values': ['signalling']}])
          if(len(response['Reservations'])==1):
            print('will terminate instance '+instanceId)
            # remove instance mapping from dynamoDb table
            table.update_item(
            Key={
                'TargetGroup': instanceMapping[instanceId],
                },
                UpdateExpression="set InstanceID = :i",
                ExpressionAttributeValues={
                    ':i': ''
                    }
            )
            ec2.terminate_instances(InstanceIds=[instanceId])
  return {
    'statusCode': 200,
    'body': json.dumps('Instance was terminated successfully !')    
  }
