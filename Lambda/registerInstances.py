# this function is triggered when a new Signalling instance is created and is used to register the instance
# in the signalling target group and keep a mapping of its query string in dynamoDB table
import boto3
import json
from boto3.dynamodb.conditions import Attr

def lambda_handler(event, context):
    ssm = boto3.client('ssm')
    parameter = ssm.get_parameter(Name='concurrencyLimit')
    concurrencyLimit = parameter['Parameter']['Value']
    instanceId=event["detail"]["instance-id"]
    ec2 = boto3.client('ec2')
    
    response = ec2.describe_instances(InstanceIds=[instanceId],Filters=[{'Name': 'tag:type', 'Values': ['signalling']}])
    if(len(response['Reservations'])==1):
        dynamodb = boto3.resource('dynamodb')
       
        table = dynamodb.Table('instanceMapping')
        response = table.scan(
            FilterExpression=Attr('InstanceID').eq('')
            )
        # it is unlikely that an instanceID was created and the pool is at capacity. However in case it happens we do not
        # register it in the DynamoDB table. A further enhancement can be created in the form of a CW Alarm which can check
        # for such unused instances and delete them automatically based on certain metrics
        if(len(response['Items'])==0):
            return {
                'statusCode': 400,
                'body': json.dumps('Instance pool at capacity ! Could not create new instance')
            }
        else:
            # the dynamoDB item is updated with the instanceID  
            table.update_item(
            Key={
                'TargetGroup': response['Items'][0]['TargetGroup'],
                },
                UpdateExpression="set InstanceID = :i",
                ExpressionAttributeValues={
                    ':i': instanceId
                    }
                    )
            # the Signalling server ALB target group is updated with the instance id. The arn for the same is retrieved from the
            # dynamoDB table which has a mapping for the same
            elbClient = boto3.client('elbv2')
            elbClient.register_targets(
                TargetGroupArn=response['Items'][0]['ARN'],
                Targets=[
                  {
                      'Id':instanceId ,
                  },
                ]
            )       
            return {
                'statusCode': 200,
                'body': json.dumps(response['Items'][0]['QueryString'])
                }
    else :
        return {
                'statusCode': 400,
                'body': json.dumps('Instance not of type signalling ! skipped registration !')
            }

    
    
