# this function is used to create new signalling instances. The function can either be triggered on schedule
# in which case, multiple signalling servers are created. This is identified when the event contains startAllServers
# as true. Refer eventbridge rule ScheduledStartSignallingServer in infra scripts
# this function can also be triggered as a response to a session request in which case only one server is created
# note that in both cases an userdata is passed which starts the signalling server and takes the matchmaker ip for 
# integration

import json
import boto3
import os
import random
from boto3.dynamodb.conditions import Attr


def lambda_handler(event, context):
    ssm = boto3.client('ssm')
    parameter = ssm.get_parameter(Name='concurrencyLimit')
    # this is used to determine the maximum number of Signalling instances that can be created
    concurrencyLimit = parameter['Parameter']['Value']
    
    # this is used to chose a subnet randomly while generating the instance
    allSubnets=['SubnetIdPublicA','SubnetIdPublicB']
    
    matchMakerPrivateIP=''
    ec2MatchMaker = boto3.client('ec2')
    response = ec2MatchMaker.describe_instances(Filters=[{'Name': 'tag:aws:cloudformation:logical-id', 'Values': ['MatchMakingInstance']}])
    if(len(response['Reservations'])==1):
        print(response['Reservations'][0]['Instances'][0]['PrivateIpAddress'])
        # this is used to retrieve the private ip of Matchmaker which allows Signalling instance to interface with it
        matchMakerPrivateIP=response['Reservations'][0]['Instances'][0]['PrivateIpAddress']
    
    # this is the startup script for Signalling instance. The execut.sh is defined in the infra scripts
    # the shutdown halt allows the instance to shutdown automatically after 20 minutes. This can be modified
    # depending on the length of the streaming session
    userData='''#!/bin/bash
    sudo su
    sudo shutdown --halt +20
    cd /usr/customapps/
    ./startSS.sh {}'''.format(matchMakerPrivateIP)
    
    print(event)
    
    if("startAllServers" in event):
        if(event["startAllServers"]):
            print("We will start all instances !")
            ec2 = boto3.client('ec2')
            response = ec2.run_instances(
                ImageId=os.environ["ImageId"],
                SubnetId=os.environ[random.choice(allSubnets)],
                LaunchTemplate={'LaunchTemplateName': os.environ["LaunchTemplateName"]},
                UserData=userData,
                MinCount=int(concurrencyLimit),
                MaxCount=int(concurrencyLimit)
            )
            return {
                'statusCode': 200,
                'body': json.dumps('All instances created ')
            }
    else:
        dynamodb = boto3.resource('dynamodb')
        # query all items based on a filter
        table = dynamodb.Table('instanceMapping')
        response = table.scan(
            FilterExpression=Attr('InstanceID').eq('')
            )
        # the dynamoDB table keeps a track of all Signalling instances and their mapping to target groups
        # this is used later to retrieve the query string for starting a streaming session
        # the absence of any row in the dynamoDB with a blank instanceID would indicate that all target groups are being used
        # and the create instance request would need to skipped
        if(len(response['Items'])==0):
            return {
                'statusCode': 400,
                'body': json.dumps('Instance pool at capacity ! Could not create new instance')
            }
        else:
            ec2 = boto3.client('ec2')
            response = ec2.run_instances(
                ImageId=os.environ["ImageId"],
                SubnetId=os.environ[random.choice(allSubnets)],
                LaunchTemplate={'LaunchTemplateName': os.environ["LaunchTemplateName"]},
                UserData=userData,
                MinCount=1,
                MaxCount=1
            )
            print(response['Instances'][0]['InstanceId'])
            # get instance id
            instanceId = response['Instances'][0]['InstanceId']
            
            return {
                'statusCode': 200,
                'body': json.dumps('New instance created '+instanceId)
            }
    
    
       