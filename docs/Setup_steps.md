# Setup Steps: ALB + ASG Self-Healing Infrastructure with Terraform

This setup guide follows the current architecture in this repository.

It covers:

1. Terraform-based deployment of ALB, Target Group, Launch Template, and ASG.
2. Optional import of already existing AWS resources into Terraform state.
3. Validation of self-healing and scale-out behavior.

## Project execution in 3 phases

### Phase 1: Lambda-first self-healing automation (initial model)

- Initial recovery logic was built with CloudWatch + SNS + Lambda.
- Lambda handled failure events and launched replacement compute automatically.
- This phase validated the self-healing concept quickly.

### Phase 2: Migration to ALB + ASG architecture (scalable model)

- Replaced Lambda-driven instance replacement with ALB + Target Group + ASG lifecycle management.
- Added /health-based routing and automatic unhealthy instance replacement.
- Added capacity scaling support with CPU-based target tracking.

### Phase 3: Terraform migration and Infrastructure State Reconciliation (advanced model)

- Converted infrastructure into Terraform configuration.
- Imported existing live AWS resources into Terraform state.
- Reconciled drift and aligned runtime resources with version-controlled IaC.

## Prerequisites

- AWS account with required permissions for EC2, ALB, Auto Scaling, IAM, and CloudWatch.
- Terraform installed locally.
- AWS CLI configured with valid credentials.
- Existing key pair available in your AWS region.

## 1. Clone and move to Terraform directory

```bash
git clone <your-repo-url>
cd aws-ec2-self-healing-infra/terraform
```

## 2. Review configuration before deployment

Check these files and update values as needed:

- provider.tf: region
- main.tf:
  - VPC ID
  - Subnet IDs
  - AMI ID
  - Key pair name
  - Security group CIDRs (especially SSH)
- ../user-data/userdata.sh: bootstrap script for Flask app and CloudWatch logs

Important behavior already configured:

- App listens on port 5000
- Target Group health check path is /health
- ALB listener runs on port 80
- ASG health check type is ELB

## 3. Initialize and validate Terraform

```bash
terraform init
terraform fmt
terraform validate
terraform plan
```

If plan looks correct:

```bash
terraform apply
```

## 4. Configure CPU-based scale-out policy

To handle traffic spikes, attach a target-tracking policy on ASG CPU utilization.

Example Terraform resource:

```hcl
resource "aws_autoscaling_policy" "cpu_target_tracking" {
  name                   = "selfheal2-cpu-target-tracking"
  autoscaling_group_name = aws_autoscaling_group.asg.name
  policy_type            = "TargetTrackingScaling"

  target_tracking_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ASGAverageCPUUtilization"
    }
    target_value = 60.0
  }
}
```

Expected result:

- During higher CPU load, ASG launches additional instances.
- ALB automatically distributes traffic to healthy targets, including new instances.

## 5. Phase 3: Infrastructure State Reconciliation

Use this if resources already exist in AWS and you want Terraform to manage them without recreating.

### 5.1 Write matching Terraform resource blocks

Ensure names, IDs, and settings in code match actual AWS resources.

### 5.2 Import resources into state

Pattern:

```bash
terraform import <terraform_resource_address> <aws_resource_id>
```

Typical imports in this project:

```bash
terraform import aws_security_group.app_sg sg-xxxxxxxx
terraform import aws_lb_target_group.tg arn:aws:elasticloadbalancing:...
terraform import aws_lb.alb arn:aws:elasticloadbalancing:...
terraform import aws_launch_template.lt lt-xxxxxxxx
terraform import aws_autoscaling_group.asg selfheal2-asg
```

### 5.3 Reconcile drift safely

Run:

```bash
terraform plan
```

Then fix mismatches until plan is clean and expected.

Known critical drift case from this project:

- ASG was using an outdated launch template version.
- Fix was to align ASG launch template reference so new instances used the latest configuration.

## 6. Verify deployment

1. Open ALB DNS in browser and confirm app response.
2. Confirm /health returns healthy status.
3. Check Target Group shows healthy targets.
4. Check ASG desired capacity and launched instances.

## 7. Test self-healing

SSH into one instance and stop the app process:

```bash
pkill -f flask
```

Expected:

- Health check fails.
- Target is marked unhealthy and removed from ALB routing.
- ASG replaces unhealthy instance.
- New instance becomes healthy and starts receiving traffic.

## 8. Test scaling behavior

Generate load against ALB endpoint.

Expected:

- CPU rises on running instances.
- Target-tracking policy triggers scale-out.
- New instance joins target group.
- ALB balances traffic across healthy instances.

## Common mistakes to avoid

1. Using wrong VPC or subnet IDs.
- This causes ALB, ASG, and instances to fail attachment or routing.

2. Health check path mismatch.
- If Target Group checks /health but app does not expose it, targets stay unhealthy.

3. Security group rules not aligned with ports.
- ALB to instance/app port (5000) must be allowed.
- HTTP 80 and restricted SSH access should be correctly configured.

4. Forgetting to base64 user data in launch template logic.
- Broken startup script means app never starts on new instances.

5. Importing wrong resource IDs during Terraform import.
- Wrong mapping creates confusing drift and unsafe plans.

6. Ignoring terraform plan after import.
- Always review and reconcile before apply.

7. Not attaching CPU target-tracking policy.
- Self-healing works for failures, but scale-out under load may not happen automatically.

8. Keeping ASG tied to old launch template version.
- New instances launch with stale configuration.

9. Committing terraform state files.
- Do not commit terraform.tfstate or backup state files to git.

10. Overly broad IAM and SSH access.
- Use least privilege IAM permissions and restrict SSH CIDR.
