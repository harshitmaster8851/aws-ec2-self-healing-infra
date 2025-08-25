## 🚑 AWS EC2 Self-Healing Infrastructure.....
This project demonstrates a **self-healing cloud architecture** on AWS.  
If an EC2 instance becomes unhealthy, CloudWatch triggers an alarm → SNS → Lambda → terminates the bad instance and launches a new one automatically.


---


## 🔥 Real-world Use Case
This project simulates a self-healing server architecture often used in production systems where uptime is critical. In enterprises like e-commerce, banking, SaaS platforms, or streaming services, downtime of even a few minutes can cause huge revenue losses and bad user experience.
Self-Healing Infrastructure on AWS – Designed and implemented a fault-tolerant system using EC2, CloudWatch, SNS, and Lambda to automatically detect instance failures and launch replacements. Achieved high availability and resiliency by eliminating manual intervention and ensuring continuous uptime.


---

## 🔧 Tech Stack
- AWS EC2
- AWS CloudWatch (Alarm)
- AWS SNS
- AWS Lambda (Python + boto3)

---

## 🏗️ Flow of Execution (Runtime)

1️⃣ EC2 Boot 🖥️
Your app runs on an EC2 instance.
Tagged with SelfHeal=true, launched from a known AMI.

2️⃣ Health Monitoring 📊
CloudWatch samples StatusCheckFailed_System & StatusCheckFailed_Instance every 1 min.

3️⃣ Alarm Trigger 🚨
If >=1 failed datapoint in 1 eval period → state flips to ALARM.
Missing data = ignored.

4️⃣ SNS Notification 📩
CloudWatch Alarm action publishes JSON to selfheal-topic.

5️⃣ Lambda Trigger ⚡
SNS invokes the selfheal-replacer Lambda with that payload.

6️⃣ Parse & Validate 🔍
Extracts InstanceId from Message.Trigger.Dimensions.
✅ Safety check: only proceed if tag SelfHeal=true.

7️⃣ Terminate Old Instance ❌💻
Lambda calls TerminateInstances for the unhealthy box.

8️⃣ Launch Replacement 🚀
Lambda spins up a fresh EC2 with env-configured params:
AMI_ID
INSTANCE_TYPE
SUBNET_ID
SECURITY_GROUP
KEY_NAME

9️⃣ Tagging 🏷️
New instance auto-tagged:
SelfHealed=true
ReplacedInstance=<old-id>
Timestamp=<UTC>

🔟 Notify & Report 📢
Lambda pushes a summary back to SNS.
You (via email/Slack) get:
❌ Old Instance ID
✅ New Instance ID


---

## 📂 Project Structure Diagram

<img width="1536" height="1024" alt="self-healing-ec2-structure" src="https://github.com/user-attachments/assets/87d5d109-ed00-40b5-9adb-314742fdb42f" />


---

## 🚀 Deployment Steps
1. **Launch EC2 Instance**  
   - Select AMI, instance type, subnet, security group, and key pair.  

2. **Create CloudWatch Alarm**  
   - Metric: `StatusCheckFailed`.  
   - Set threshold = `>= 1` for 1 datapoint.  
   - Action = Send to SNS topic.  

3. **Create SNS Topic**  
   - Create a new topic → Subscribe with your email.  

4. **Lambda Setup**  
   - Runtime: Python 3.x.  
   - IAM Role: Attach `AmazonEC2FullAccess` + `AmazonSNSFullAccess`.  
   - Add environment variables:  
     - `AMI_ID`, `SUBNET_ID`, `SECURITY_GROUP`, `KEY_NAME`, `SNS_TOPIC_ARN`.  
   - Paste the code from `lambda_function.py`.  

5. **Test the System**  
   - Stop or break EC2 instance → Alarm triggers.  
   - Lambda runs → Old instance terminated, new launched.  
   - SNS sends email with details.  

---

## 📸 Screenshots
- CloudWatch Alarm
   <img width="955" height="472" alt="image" src="https://github.com/user-attachments/assets/bde641f9-ebb1-43cd-8f90-9640ff498d83" />
 
- SNS Subscription Email
  <img width="951" height="497" alt="image" src="https://github.com/user-attachments/assets/823442b9-5c3a-4a12-b28d-6be7979ec45d" />

- Lambda Logs (showing termination & new instance ID)
  <img width="959" height="497" alt="image" src="https://github.com/user-attachments/assets/c9bba2d3-fd7b-4027-8da8-90447ccf8a6b" />

- EC2 Dashboard showing new instance
  <img width="959" height="498" alt="image" src="https://github.com/user-attachments/assets/17f12d31-ee0d-4f7e-9175-00e5bd4617b4" />



---

## 🔮 Future Plans
In the next phase of this project, I plan to:
1. Implement Auto Scaling Groups to replace the manual Lambda approach.
2. Integrate application-level health checks for smarter recovery.
3. Migrate deployment to Infrastructure-as-Code using Terraform or CloudFormation.

---

## 👩‍💻 Author
**Harshit Rastogi**  
B.Tech 3rd Year @ USICT, Dwarka    

