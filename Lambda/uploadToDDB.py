import json
import boto3
import os

def lambda_handler(event, context):
    # TODO implement
    
    client = boto3.client('elbv2')
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ["DynamoDBName"])
    
    #get listener arn associated with the signalling load balancer
    response = client.describe_load_balancers(
       Names=[os.environ["ALBName"]]
    )
    loadbalancerarn=response['LoadBalancers'][0]['LoadBalancerArn']
   
    response = client.describe_listeners(
       LoadBalancerArn=loadbalancerarn
    )
    listenerarn=response['Listeners'][0]['ListenerArn']
     
    response = client.describe_rules(
       ListenerArn=listenerarn
    )
    
    #iterate through the list of rules available in signalling load balancer listener and populate DDB
    
    for rule in response['Rules']:
        if rule['Priority']!='default':
            qs=rule['Conditions'][0]['QueryStringConfig']['Values'][0]['Key']+"="+rule['Conditions'][0]['QueryStringConfig']['Values'][0]['Value']
            table.put_item(
                
                Item={
                    'TargetGroup': 'TG'+rule['Conditions'][0]['QueryStringConfig']['Values'][0]['Value'],
                    'ARN': rule['Actions'][0]['TargetGroupArn'],
                    'InstanceID': '',
                    'QueryString': qs
                }
            )
        else :
            table.put_item(
                Item={
                        'TargetGroup': 'TG01',
                        'ARN': rule['Actions'][0]['TargetGroupArn'],
                        'InstanceID': '',
                        'QueryString': ''
                    }
            )        
    
    return {
        'statusCode': 200,
        'body': 'Populated dynamodb with required information !'
    }