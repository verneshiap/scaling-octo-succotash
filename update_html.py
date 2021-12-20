import json
import boto3
import string

s3 = boto3.client('s3')
client = boto3.client('lambda')
s3r = boto3.resource('s3')

def lambda_handler(event, context):
    
    key = 'Experiences/' + event['exp_name'] + '/index.html'
    bucket = 'ed1-eye-tracker'
    local = '/tmp/index.html'
    s3.download_file(bucket,key,local)
    path = 'Experiences/'+ event['exp_name'] + '/' 
    inp = open(local, 'r')
    out = open('/tmp/index_update.html', 'w')
    lines = inp.readlines()
    inp.close()
    for line in lines:
        if "update_experience_name_here" in line:
            line = line.replace("update_experience_name_here",event['exp_name'])
        if "<div id='2D_space'></div>" in line:
            line = line.replace("<div id='2D_space'></div>",event['src_2d'])
        if "<div id='AR_space'></div>" in line:
            line = line.replace("<div id='AR_space'></div>",event['src_ar'])
        if "<div id='RL_space'></div>" in line:
            line = line.replace("<div id='RL_space'></div>",event['src_rl'])
        
        out.write(line)
        if line == 0:
            break
    out.close
    local = '/tmp/index_update.html'
    out = open(local, 'r')
    lines = out.readlines()
    contents = []
    for line in lines:
        contents.append(line)
    body = "".join(contents)
    
    s3.put_object(Bucket=bucket, Body=body, Key=key, ContentType='text/html; charset=UTF-8', ACL='public-read')
    # s3r.meta.client.upload_file(local, bucket, key, ExtraArgs={'Metadata': {'ContentType': 'text/html'}})
    out.close()
    
    
    return 0
