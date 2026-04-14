# 🚀 AWS Self-Healing Infrastructure using Terraform

## 📌 Project Overview

This project demonstrates a **production-grade self-healing cloud architecture on AWS**, designed to maintain high availability and automatically recover from failures.

Initially built using a **manual AWS setup**, the system was later migrated to **Terraform (Infrastructure as Code)** to achieve:

- ⚡ Scalability  
- 🧾 Version-controlled infrastructure  
- 🔄 Automated state management  
- ❌ Reduced manual intervention  

This mirrors how real-world systems (SaaS, e-commerce platforms) ensure **fault tolerance and continuous uptime**.

---

## 🛠️ Tech Stack

| Category       | Tools |
|---------------|------|
| Cloud         | AWS (EC2, ALB, ASG, CloudWatch, SNS) |
| IaC           | Terraform |
| Application   | Python (Flask) |
| OS            | Amazon Linux |

---

## 🏗️ Architecture

### 🔄 Request Flow

User → ALB → Target Group → Auto Scaling Group → EC2 → Flask App

---


### 📊 Diagram

        ┌───────────────┐
        │     User      │
        └──────┬────────┘
               │ HTTP Request
        ┌──────▼────────┐
        │      ALB      │
        └──────┬────────┘
               │
        ┌──────▼────────┐
        │ Target Group  │
        │   (/health)   │
        └──────┬────────┘
               │
    ┌──────────▼──────────┐
    │   Auto Scaling Group│
    └──────┬────────┬─────┘
           │        │
    ┌──────▼───┐ ┌──▼──────┐
    │  EC2 #1  │ │  EC2 #2 │
    │ Flask App│ │ Flask App│
    └──────────┘ └─────────┘


---

## ✨ System Highlights

### 🔁 Self-Healing Mechanism
- Health checks via `/health` endpoint  
- Unhealthy instances are:
  - Removed from traffic  
  - Terminated by ASG  
  - Replaced automatically  

---

### ⚡ Zero Downtime
- ALB routes traffic **only to healthy instances**
- Replacement happens **seamlessly in the background**

---

### ⚙️ Automated Provisioning
EC2 instances use **User Data scripts** to:

- Install Python + Flask  
- Deploy application  
- Start services automatically  

---

### 📊 Centralized Logging
- CloudWatch Agent pushes logs (`output.log`)
- Enables:
  - Monitoring  
  - Debugging  
  - Alerting  

---

## 🚀 Infrastructure State Reconciliation (Advanced)

This is the **core highlight** of the project — not just building infra, but **migrating real infrastructure into Terraform safely**.

### 🔄 Migration Strategy

#### 1. Code Definition
- Created:
  - `provider.tf`
  - `main.tf`
  - `userdata.sh`
- Matched Terraform config with live AWS setup  

---

#### 2. State Import
Imported existing resources:

- Security Groups  
- Target Group  
- ALB  
- Auto Scaling Group  

```bash
terraform import <resource> <aws-resource-id>

---

### 3. Conflict Resolution

- Fixed duplicate resource definitions  
- Resolved provider issues  
- Ensured clean `terraform plan`  

---

### 4. Drift Correction (Critical Fix)

- Detected ASG using outdated Launch Template  
- Replaced ASG via Terraform  
- Ensured new instances use latest configuration  

---

### 5. State Management

- Maintained clean Terraform state  
- Prevented drift and misconfiguration  

---

## 🔧 Deployment Workflow

### 🔹 Manual Setup (Initial Phase)

- Deploy Flask app on EC2  
- Configure `/health` endpoint  
- Create Target Group + ALB  
- Configure Auto Scaling Group  

---

### 🔹 Terraform Transition

```bash
# Initialize Terraform
terraform init

# Import existing resources
terraform import ...

# Validate infrastructure
terraform plan

# Apply configuration
terraform apply

## Testing Self-Healing

```bash
# SSH into instance
ssh -i your-key.pem ec2-user@<instance-ip>

# Simulate failure
pkill -f flask

Expected Behavior
Instance marked unhealthy
Traffic stopped
ASG terminates instance
New instance launched automatically
Learning Outcomes
Deep understanding of AWS high-availability architecture
Hands-on with:
Terraform (init, plan, apply, import, state)
Learned state reconciliation (real DevOps skill)
Debugged real infrastructure issues
Migrated manual (click-ops) → IaC pipeline
Best Practices
Do NOT commit terraform.tfstate
Restrict SSH access (port 22)
Use least-privilege IAM policies
Real-World Impact

This architecture is used in:

SaaS platforms → uptime guarantee
E-commerce → traffic spike handling
APIs → automatic failure recovery
Author
Harshit Rastogi
B.Tech 3rd Year — USICT, Dwarka
Aspiring DevOps & Cloud Engineer
