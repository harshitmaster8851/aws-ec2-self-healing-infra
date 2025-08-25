# Setup Steps: Deploying Self-Healing Infrastructure on AWS 🛠️

Follow these steps to replicate the project:

---

## 1. Launch EC2 instance
- Go to AWS Console → EC2 → Launch instance.
- Choose AMI (e.g., Amazon Linux 2).
- Configure Security Group, Subnet, KeyPair.
- Add a tag: `SelfHeal=true`.

---

## 2. Create CloudWatch Alarm
- Go to CloudWatch → Alarms → Create alarm.
- Metric: `StatusCheckFailed_Instance` or `StatusCheckFailed_System`.
- Condition: >= 1 for 1 datapoint.
- Missing data → Treat as missing.
- Action: Send to an SNS topic.

---

## 3. Create SNS Topic
- Go to SNS → Topics → Create.
- Name: `selfheal-topic`.
- Add subscription → Email (your ID). Confirm the email.

---

## 4. Deploy Lambda
- Go to Lambda → Create function (Python 3.12 runtime).
- Add SNS trigger → select `selfheal-topic`.
- Paste code from `lambda/lambda_function.py`.
- Add Environment Variables:
  - `AMI_ID`, `INSTANCE_TYPE`, `SUBNET_ID`, `SECURITY_GROUP`, `KEY_NAME`.
- Add IAM Role with permissions: `EC2FullAccess`, `CloudWatchFullAccess`, `SNSFullAccess`.

---

## 5. Test End-to-End
- Stop/terminate your EC2 to simulate failure.
- CloudWatch triggers alarm → SNS → Lambda.
- Lambda kills failed instance + launches a new one.
- You get an email notification with old/new instance IDs. 🎉
