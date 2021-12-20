import json
import boto3
import PIL

s3 = boto3.client("s3")
s3r = boto3.resource('s3')
client = boto3.client('lambda')

def lambda_handler(event, context):
    experiences = []
    
    all_objects = s3.list_objects(
        Bucket = 'ed1-eye-tracker',
        Prefix = "Experiences/",
        Delimiter = "/")
        
    for item in all_objects['CommonPrefixes']:
        folder = item['Prefix'].strip("/")
        folder = folder.replace("Experiences/","")
        if folder.endswith("css") or folder.endswith("Template"):
            pass
        else:
            experiences.append(folder)

        # source_bucket = s3r.Bucket('output-data-processing')
        source_bucket = s3r.Bucket('processed-output1')
        raw_data_bucket = s3r.Bucket('raw-data-bucket-egn-grp08')
        dest_bucket = s3r.Bucket('ed1-eye-tracker')
            
        if event['exp_name'] in experiences:
            # Experiences/Dining Room/2D_Processed_Eye_Data_Dining_Room.csv
            key = 'Experiences/' + event['exp_name'] + '/' + event['filename']
            s3r.Object(dest_bucket.name, key).copy_from(CopySource = {'Bucket': source_bucket.name, 'Key': event['filename']})
        
            # copy image
            et_list = event['filename'].split("_")
            exp_type = et_list[0]
            image_name = exp_type + '_' + event['exp_name'].replace(" ","_") + '1.png'
            key6 = 'Experiences/' + event['exp_name'] + '/' + image_name
            s3r.Object(dest_bucket.name, key6).copy_from(CopySource = {'Bucket': raw_data_bucket.name, 'Key': image_name})
            
            # invoke pygaze fixation map function
            input_params = {
                "exp_name": event['exp_name'],
                "exp_type": exp_type
                }
            response = client.invoke(
                FunctionName = 'arn:aws:lambda:us-east-1:886594678139:function:pygaze_fixation_map',
                InvocationType = 'RequestResponse',
                Payload = json.dumps(input_params)
                ) 
                
            return "File updated"
        else:
            # Create new Experience subfolder
            key1 = 'Experiences/' + event['exp_name'] + '/'
            s3.put_object(Bucket=dest_bucket.name, Key=key1)
            
            # Copy processed data csv from output bucket to new Experience subfolder
            key2 = 'Experiences/' + event['exp_name'] + '/' + event['filename']
            s3r.Object(dest_bucket.name, key2).copy_from(CopySource = {'Bucket': source_bucket.name, 'Key': event['filename']})
            
            # Create Fixation Maps subfolder
            key3 = 'Experiences/' + event['exp_name'] + '/Fixation Maps/'
            s3.put_object(Bucket=dest_bucket.name, Key=key3)
            
            # Copy css content from Template subfolder into new Experience subfolder
            key5 = 'Experiences/' + event['exp_name'] + '/css/style.css'
            s3r.Object(dest_bucket.name, key5).copy_from(CopySource = {'Bucket': dest_bucket.name, 'Key': 'Experiences/Template/css/style.css'})
            
            # Copy experience image from raw data bucket
            et_list = event['filename'].split("_")
            exp_type = et_list[0]
            image_name = exp_type + '_' + event['exp_name'].replace(" ","_") + '1.png'
            key6 = 'Experiences/' + event['exp_name'] + '/' + image_name
            s3r.Object(dest_bucket.name, key6).copy_from(CopySource = {'Bucket': raw_data_bucket.name, 'Key': image_name})
            
            # invoke pygaze fixation map function
            input_params = {
                "exp_name": event['exp_name'],
                "exp_type": exp_type
                }
            response = client.invoke(
                FunctionName = 'arn:aws:lambda:us-east-1:886594678139:function:pygaze_fixation_map',
                InvocationType = 'RequestResponse',
                Payload = json.dumps(input_params)
                ) 
            img_srcs = json.load(response['Payload'])
            # Copy index.html from Template subfolder into new Experience subfolder
            key4 = 'Experiences/' + event['exp_name'] + '/index.html'
            s3r.Object(dest_bucket.name, key4).copy_from(CopySource = {'Bucket': dest_bucket.name, 'Key': 'Experiences/Template/index.html'})
            
            input_params2 = {
                "exp_name": event['exp_name'],
                "src_2d": img_srcs[0],
                "src_ar": img_srcs[1],
                "src_rl": img_srcs[2]
                }
            response = client.invoke(
                FunctionName = 'arn:aws:lambda:us-east-1:886594678139:function:update_html',
                InvocationType = 'RequestResponse',
                Payload = json.dumps(input_params2)
                )   
            
            
            return "New Experience folder created"
