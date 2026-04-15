# User Data Templates for Website Deployment

Use this file as a template reference for your Lambda-phase site demos and EC2 website bootstrapping.

## Template 1: Full static website from ZIP (existing style)

```bash
#!/bin/bash
set -e

dnf update -y
dnf install -y httpd unzip wget

systemctl enable httpd
systemctl start httpd

cd /tmp
wget https://www.tooplate.com/zip-templates/2140_stellaris_research.zip -O website.zip
unzip -o website.zip

rm -rf /var/www/html/*
cp -r 2140_stellaris_research/* /var/www/html/

chown -R apache:apache /var/www/html
chmod -R 755 /var/www/html

systemctl restart httpd
```

## Template 2: Flask app + /health + CloudWatch logs (recommended)

Use this when you want the same runtime behavior used in your self-healing architecture.

```bash
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
```

## Notes

- Use Template 1 when you want a complete static demo website.
- Use Template 2 for app-level health checks, ALB integration on port 5000, and CloudWatch log collection.
- If your architecture uses Flask on port 5000 and ALB health check path /health, keep that app-based health endpoint in your main runtime setup.
