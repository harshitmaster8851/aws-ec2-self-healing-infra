import boto3, os, json, time
from datetime import datetime

ec2 = boto3.client("ec2")
sns = boto3.client("sns")

# Env vars
SNS_TOPIC_ARN = os.getenv("SNS_TOPIC_ARN")
AMI_ID = os.getenv("AMI_ID")
INSTANCE_TYPE = os.getenv("INSTANCE_TYPE")
SUBNET_ID = os.getenv("SUBNET_ID")
SEC_GROUP = os.getenv("SEC_GROUP")
KEY_NAME = os.getenv("KEY_NAME")
DEMO = os.getenv("DEMO_MODE", "true").lower() == "true"


def lambda_handler(event, context):
    msg = json.loads(event["Records"][0]["Sns"]["Message"])
    instance_id = msg["Trigger"]["Dimensions"][0]["value"]

    if DEMO:
        print(f"[DEMO] Would replace {instance_id}")
        return

    # Step 1: Launch replacement
    res = ec2.run_instances(
        ImageId=AMI_ID, InstanceType=INSTANCE_TYPE,
        MinCount=1, MaxCount=1,
        SubnetId=SUBNET_ID, SecurityGroupIds=[SEC_GROUP],
        KeyName=KEY_NAME
    )
    new_id =  res["Instances"][0]["InstanceId"]
    print(f" Launched replacement instance: {new_id}")

    # Step 2: Wait until running
    waiter = ec2.get_waiter("instance_running")
    waiter.wait(InstanceIds=[new_id])
    print(f" New instance {new_id} is running")

    # Step 3: Tag new instance
    ec2.create_tags(Resources=[new_id], Tags=[
        {"Key": "SelfHealed", "Value": "true"},
        {"Key": "ReplacedInstance", "Value": instance_id},
        {"Key": "Timestamp", "Value": datetime.utcnow().isoformat()}
    ])

    # Step 4: Terminate old instance
    ec2.terminate_instances(InstanceIds=[instance_id])
    print(f" Terminated old instance: {instance_id}")

    # Step 5: Notify
    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Subject=" EC2 Self-Healing Triggered",
        Message=f"Old: {instance_id}\nNew: {new_id}\nTime: {datetime.utcnow().isoformat()}"
    )
