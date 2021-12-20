import json
import boto3 
s3 = boto3.client("s3")

def lambda_handler(event, context):
    get_exp = False
    if event['get_experiences'] == 'True':
        get_exp = True
    if get_exp:
        all_objects = s3.list_objects(
            Bucket = 'ed1-eye-tracker',
            Prefix = "Experiences/",
            Delimiter = "/"
            ) 
        data =''
        for item in all_objects['CommonPrefixes']:
                dir = item['Prefix'].strip("/")
                if dir.endswith("css") or dir.endswith("Template"):
                    pass
                else:
                    exp = dir.split("/")
                    path = dir.replace(" ","+")
                    # data += ("<a href='https://ed1-eye-tracker.s3.amazonaws.com/Experiences/"+path+"/index.html'>"
                    # +exp[len(exp)-1]+"</a><br>")
                    data += ("<a href='https://ed1-eye-tracker.s3.amazonaws.com/"+path+"/index.html'>"
                    +exp[len(exp)-1]+"</a><br>")                    
        return data
    else:
        return 'Error'
    
