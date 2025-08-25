# Project Overview: Self-Healing Infrastructure on AWS 🚀

## Problem Statement ❌
In cloud environments, applications often rely on EC2 instances. But sometimes these instances can fail due to hardware issues, misconfigurations, or crashes.  
Manual intervention to detect and replace instances causes **downtime, lost revenue, and poor user experience**.

## Solution ✅
We built a **self-healing infrastructure** using AWS services:
- **CloudWatch** monitors EC2 health.
- **SNS** sends notifications when alarms trigger.
- **Lambda** automatically replaces unhealthy instances with a fresh one.
- **Tags & metadata** ensure only the correct instances are managed.

This ensures **high availability, resilience, and automation** with zero manual effort.
