#!/bin/bash

# Update system
yum update -y

# Install python + pip
yum install -y python3 python3-pip

# Install flask properly
python3 -m pip install --upgrade pip
python3 -m pip install flask

# Install CloudWatch agent
yum install -y amazon-cloudwatch-agent

# Create Flask app
cat <<EOF > /home/ec2-user/app.py
from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "App is running"

@app.route('/health')
def health():
    return {"status": "ok"}, 200

app.run(host="0.0.0.0", port=5000)
EOF

# Give proper ownership (important for stability)
chown ec2-user:ec2-user /home/ec2-user/app.py

# Run app in background (more reliable)
nohup python3 /home/ec2-user/app.py > /home/ec2-user/output.log 2>&1 &

# Wait a bit to ensure app starts before logs agent
sleep 10

# Create CloudWatch config
cat <<EOF > /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json
{
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/home/ec2-user/output.log",
            "log_group_name": "selfheal-app-logs",
            "log_stream_name": "{instance_id}",
            "timezone": "UTC"
          }
        ]
      }
    }
  }
}
EOF

# Start CloudWatch agent
/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
-a fetch-config \
-m ec2 \
-c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json \
-s
