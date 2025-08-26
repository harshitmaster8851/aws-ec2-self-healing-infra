import boto3, os, json
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
EIP_ALLOCATION_ID = os.getenv("EIP_ALLOCATION_ID") 
DEMO = os.getenv("DEMO_MODE", "true").lower() == "true"


def lambda_handler(event, context):
    print("==== Incoming Event ====")
    print(json.dumps(event, indent=2)) 

    # Step 0: Extract instance ID safely
    instance_id = None
    try:
        sns_message = event["Records"][0]["Sns"]["Message"]
        msg = json.loads(sns_message)
        print(f" SNS Message Parsed: {msg}")

        if "Trigger" in msg and "Dimensions" in msg["Trigger"]:
            for d in msg["Trigger"]["Dimensions"]:
                if d.get("name") == "InstanceId":
                    instance_id = d.get("value")
                    break
    except Exception as e:
        print(f" Could not parse SNS message: {e}")

    # fallback for manual test events
    if not instance_id:
        instance_id = "i-MANUALTEST"
        print(" No instance ID found. Using fallback:", instance_id)

    if DEMO:
        print(f"[DEMO] Would replace {instance_id}")
        return

    # Step 1: Launch replacement
    res = ec2.run_instances(
        ImageId=AMI_ID,
        InstanceType=INSTANCE_TYPE,
        MinCount=1, MaxCount=1,
        SubnetId=SUBNET_ID,
        SecurityGroupIds=[SEC_GROUP],
        KeyName=KEY_NAME
    )
    new_id = res["Instances"][0]["InstanceId"]
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

    # Step 4: Reattach Elastic IP (using Allocation ID directly)
    if EIP_ALLOCATION_ID:
        ec2.associate_address(
            AllocationId=EIP_ALLOCATION_ID,
            InstanceId=new_id,
            AllowReassociation=True
        )
        print(f" Elastic IP allocation {EIP_ALLOCATION_ID} attached to {new_id}")

    # Step 5: Terminate old instance
    ec2.terminate_instances(InstanceIds=[instance_id])
    print(f" Terminated old instance: {instance_id}")

    # Step 6: Notify via SNS
    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Subject=" EC2 Self-Healing Triggered",
        Message=f"Old: {instance_id}\nNew: {new_id}\nElasticIPAlloc: {EIP_ALLOCATION_ID}\nTime: {datetime.utcnow().isoformat()}"
    )
