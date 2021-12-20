import json
import urllib.parse
import boto3
import string

s3 = boto3.client('s3')
client = boto3.client('lambda')


def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    filename = key
    if "Processed" in filename:
        return "No Fixations CSV available"
    else:
        try:
            # response = s3.get_object(Bucket=bucket, Key=key)
            # print("CONTENT TYPE: " + response['ContentType'])
            key_str = key.replace(".csv","")
            key_list = key_str.split("_")
            exp_name = ""
            for i in range(2,len(key_list)):
                exp_name += key_list[i]
                if i < len(key_list)-1:
                    exp_name += " "
                    
            input_params = {
                "exp_name": exp_name,
                "filename": filename
                }
                
            response = client.invoke(
                FunctionName = 'arn:aws:lambda:us-east-1:886594678139:function:update_experience_files',
                InvocationType = 'RequestResponse',
                Payload = json.dumps(input_params)
                )   
            # response_from_update = json.load(response['Payload'])
            
            return "Complete"
            
        except Exception as e:
            print(e)
            print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
            raise e
