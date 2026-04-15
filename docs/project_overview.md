# Project Overview: AWS Self-Healing Infrastructure

## Vision

This project demonstrates how to build and evolve a production-style, self-healing web infrastructure on AWS.

It started as a Lambda-first recovery setup, then moved to an Auto Scaling and Load Balancing architecture, and finally to full Infrastructure as Code with Terraform and state import.

## Problem statement

Traditional EC2-based deployments can fail due to process crashes, configuration drift, or infrastructure issues. If detection and recovery are manual, the system faces:

- Service downtime
- Slow incident response
- Unpredictable scaling under traffic spikes
- Operational overhead from repeated manual fixes

## Final solution architecture

The final system uses:

- Application Load Balancer (ALB) for traffic distribution
- Target Group health checks on /health
- Auto Scaling Group (ASG) for automatic instance replacement
- EC2 instances running a Flask app
- User data bootstrapping for automatic app provisioning
- CloudWatch observability and alarms

Request flow:

User -> ALB -> Target Group -> ASG-managed EC2 instances -> Flask app

## Evolution journey

### Phase 1: Lambda-first automation

Initial recovery logic used Lambda-based automation for replacing unhealthy resources quickly.

### Phase 2: Migration to ALB + ASG + EC2

The architecture was upgraded for stronger high availability and traffic handling:

- Health-based target registration and deregistration
- Automatic replacement of unhealthy instances by ASG
- Better control over web workload behavior than the initial model

### Phase 3: Terraform migration (IaC)

The entire infrastructure was codified in Terraform to improve repeatability, versioning, and change safety.

## Infrastructure State Reconciliation (ADVANCED)

A key achievement of this project was importing existing live AWS resources into Terraform state and reconciling drift without disrupting running services.

Main reconciliation steps:

1. Wrote Terraform resource definitions to match live AWS resources.
2. Imported existing resources into Terraform state.
3. Resolved code-state mismatches and plan conflicts.
4. Fixed critical drift (ASG linked to outdated launch template version).
5. Stabilized state for predictable future deployments.

This process reflects real-world DevOps work where teams move from manual setup to managed Infrastructure as Code.

## Traffic spike handling

ASG uses a target-tracking inline policy on CPU utilization.

- When CPU utilization rises, ASG launches additional instances.
- ALB automatically distributes incoming traffic to healthy instances, including newly launched ones.
- This maintains response reliability during sudden load increases.

## Impact

- Improved uptime through automatic failure recovery
- Reduced manual intervention
- Scalable traffic management with ALB + ASG
- Production-friendly infrastructure lifecycle with Terraform
