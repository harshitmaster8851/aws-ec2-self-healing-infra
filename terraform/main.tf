# -----------------------------
# Provider
# -----------------------------

# -----------------------------
# Security Group (existing)
# -----------------------------
resource "aws_security_group" "app_sg" {
  name        = "selheal2-sg"
  description = "Self-healing Flask app security group"
  vpc_id      = "vpc-0a0778ed3bb0db8bc"

  ingress {
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["119.252.194.81/32"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# -----------------------------
# Target Group (existing)
# -----------------------------
resource "aws_lb_target_group" "tg" {
  name     = "selfheal2-tg"
  port     = 5000
  protocol = "HTTP"
  vpc_id   = "vpc-0a0778ed3bb0db8bc"

  health_check {
    path                = "/health"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
    matcher             = "200"
  }
}

# -----------------------------
# Application Load Balancer
# -----------------------------
resource "aws_lb" "alb" {
  name               = "selfheal2-ALB"
  load_balancer_type = "application"
  internal           = false

  security_groups = [aws_security_group.app_sg.id]

  subnets = [
    "subnet-0baec5a6b73d105b3",
    "subnet-03247d021ea4ba14e",
    "subnet-01938ca055ff62e43",
    "subnet-017f8e6cc0f0ed346",
    "subnet-05718a2d6995920f3",
    "subnet-08cdb9fbda872dea3"
  ]
}

# -----------------------------
# Listener (ALB → Target Group)
# -----------------------------
resource "aws_lb_listener" "listener" {
  load_balancer_arn = aws_lb.alb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.tg.arn
  }
}

# -----------------------------
# Launch Template (existing config replica)
# -----------------------------
resource "aws_launch_template" "lt" {
  name_prefix   = "selfheal2-template"
  image_id      = "ami-0ea87431b78a82070"
  instance_type = "t2.micro"

  key_name = "selfheal2-key"

  network_interfaces {
    associate_public_ip_address = true
    security_groups             = [aws_security_group.app_sg.id]
  }

  user_data = base64encode(file("../user-data/userdata.sh"))
}

# -----------------------------
# Auto Scaling Group
# -----------------------------
resource "aws_autoscaling_group" "asg" {
  name             = "selfheal2-asg"
  desired_capacity = 1
  max_size         = 2
  min_size         = 1

   tag {
    key                 = "Name"
    value               = "selfheal2-terraform"
    propagate_at_launch = true
  }

  vpc_zone_identifier = [
    "subnet-0baec5a6b73d105b3",
    "subnet-01938ca055ff62e43",
    "subnet-017f8e6cc0f0ed346",
    "subnet-05718a2d6995920f3",
    "subnet-08cdb9fbda872dea3"
  ]

  target_group_arns = [aws_lb_target_group.tg.arn]

  launch_template {
    id      = aws_launch_template.lt.id
    version = "$Latest"
  }

  health_check_type         = "ELB"
  health_check_grace_period = 100
}
