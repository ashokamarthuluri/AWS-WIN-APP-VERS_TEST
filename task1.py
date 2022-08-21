import boto3
import time

ec2 = boto3.resource('ec2', region_name='us-east-1')

win_ec2_list = []

#Checking for all windows instances and saving the server ids into a list. 
for i in ec2.instances.all():
    if i.platform == 'windows' and i.state["Name"] == 'running':
        win_ec2_list.append(i.id)
# print(win_ec2_list)        

#Sending powershell command to get name and version of the software.
#Using AWS SSM for connecting to the server for above. And Saving the output in S3 Bucket. 
ssm_client = boto3.client('ssm',region_name='us-east-1')
response = ssm_client.send_command(
    InstanceIds = win_ec2_list,
    DocumentName = "AWS-RunPowerShellScript",
    Parameters = {
        'commands': [
            'Get-WmiObject -Class Win32_Product | select Name, version'
        ]
    },
    OutputS3BucketName='ssmbucketfortst'
)

command_id = response['Command']['CommandId']
output = ssm_client.get_command_invocation(
    CommandId = command_id,
    InstanceId = 'i-0533ec91ec7a77f25',
)
time.sleep(5)
# print(output)

#Retreving the Output and printing the Output form S3 bucket.
s3_res = boto3.resource('s3',region_name='us-east-1')
my_bucket = s3_res.Bucket('ssmbucketfortst')

for i in my_bucket.objects.all():
    print(i.get()['Body'].read())