# this function is used to authenticate websocket connection from client to API Gateway
# the web socket connection is used for requesting streaming sessions
import json

def lambda_handler(event, context):
    
    print(event)
    
    if("abcd" == event["queryStringParameters"]["tokenId"]):
        return {
            'statusCode': 200,
            'body': json.dumps('Web socket connection  valid !')
        }
    else:
        return {
            'statusCode': 401,
            'body': json.dumps('Web socket connection  invalid !')
        } 
    
