# Deploying FastGPT to AWS ECS

This document outlines the steps to deploy the FastGPT application to AWS ECS (Elastic Container Service) using Fargate.

## Prerequisites

- AWS CLI installed and configured
- Docker installed
- Access to AWS ECR (Elastic Container Registry)
- AWS Account with appropriate permissions
- OpenAI API Key

## Step 1: Prepare the Docker Image

1. Remove the `--reload` flag from the Dockerfile for production deployment:
```dockerfile
FROM python:3.10

WORKDIR /code

COPY --link --chown=1000 . .

RUN pip install --no-cache-dir -r requirements.txt

# The OpenAI API key will be provided at runtime through environment variables
ENV PYTHONUNBUFFERED=1 PORT=7860

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
```

## Step 2: Create and Push to ECR Repository

```bash
# Create ECR repository
aws ecr create-repository --repository-name fastgpt --region us-east-1

# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 462019928087.dkr.ecr.us-east-1.amazonaws.com

# Build the image
docker build -t fastgpt .

# Tag the image
docker tag fastgpt:latest 462019928087.dkr.ecr.us-east-1.amazonaws.com/fastgpt:latest

# Push the image
docker push 462019928087.dkr.ecr.us-east-1.amazonaws.com/fastgpt:latest
```

## Step 3: Set Up ECS Infrastructure

### Create ECS Cluster
```bash
aws ecs create-cluster --cluster-name fastgpt-cluster --region us-east-1
```

### Create Task Definition
Create a file named `task-definition.json`:
```json
{
    "family": "fastgpt",
    "networkMode": "awsvpc",
    "requiresCompatibilities": ["FARGATE"],
    "cpu": "256",
    "memory": "512",
    "executionRoleArn": "arn:aws:iam::462019928087:role/ecsTaskExecutionRole",
    "containerDefinitions": [
        {
            "name": "fastgpt",
            "image": "462019928087.dkr.ecr.us-east-1.amazonaws.com/fastgpt:latest",
            "portMappings": [
                {
                    "containerPort": 7860,
                    "protocol": "tcp"
                }
            ],
            "environment": [
                {
                    "name": "PYTHONUNBUFFERED",
                    "value": "1"
                },
                {
                    "name": "PORT",
                    "value": "7860"
                }
            ],
            "secrets": [
                {
                    "name": "OPENAI_API_KEY",
                    "valueFrom": "/fastgpt/openai-api-key"
                }
            ],
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-group": "/ecs/fastgpt",
                    "awslogs-region": "us-east-1",
                    "awslogs-stream-prefix": "ecs"
                }
            }
        }
    ]
}
```

### Create CloudWatch Log Group
```bash
aws logs create-log-group --log-group-name /ecs/fastgpt --region us-east-1
```

### Register Task Definition
```bash
aws ecs register-task-definition --cli-input-json file://task-definition.json --region us-east-1
```

## Step 4: Network Configuration

### Create Security Group
```bash
# Create security group
aws ec2 create-security-group --group-name fastgpt-ecs-sg --description "Security group for FastGPT ECS tasks" --region us-east-1

# Add inbound rule for application port
aws ec2 authorize-security-group-ingress --group-id sg-0c58d69c4cbc4e328 --protocol tcp --port 7860 --cidr 0.0.0.0/0 --region us-east-1
```

## Step 5: Create ECS Service

```bash
aws ecs create-service \
    --cluster fastgpt-cluster \
    --service-name fastgpt-service \
    --task-definition fastgpt:1 \
    --desired-count 1 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[subnet-0bc2d7b816d989e51],securityGroups=[sg-0c58d69c4cbc4e328],assignPublicIp=ENABLED}" \
    --region us-east-1
```

## Step 6: Monitor Deployment

Check the status of your tasks:
```bash
# List tasks
aws ecs list-tasks --cluster fastgpt-cluster --service-name fastgpt-service --region us-east-1

# Get task details
aws ecs describe-tasks --cluster fastgpt-cluster --tasks <task-arn> --region us-east-1
```

## Accessing the Application

Once deployed, the application will be accessible at:
```
http://<task-public-ip>:7860
```

## Stopping the Service

To temporarily stop the service without deleting resources:

```bash
# Set the desired count to 0 to stop all tasks
aws ecs update-service \
    --cluster fastgpt-cluster \
    --service fastgpt-service \
    --desired-count 0 \
    --region us-east-1

# Verify that tasks are stopped
aws ecs list-tasks --cluster fastgpt-cluster --service-name fastgpt-service --region us-east-1
```

To restart the service later:
```bash
# Set the desired count back to 1 to start the service
aws ecs update-service \
    --cluster fastgpt-cluster \
    --service fastgpt-service \
    --desired-count 1 \
    --region us-east-1
```

## Cleanup

To clean up the resources:

```bash
# Delete the service
aws ecs delete-service --cluster fastgpt-cluster --service fastgpt-service --force --region us-east-1

# Delete the cluster
aws ecs delete-cluster --cluster fastgpt-cluster --region us-east-1

# Delete the log group
aws logs delete-log-group --log-group-name /ecs/fastgpt --region us-east-1

# Delete the security group
aws ec2 delete-security-group --group-id sg-0c58d69c4cbc4e328 --region us-east-1

# Delete the ECR repository
aws ecr delete-repository --repository-name fastgpt --force --region us-east-1
```

## Troubleshooting

1. Check CloudWatch logs for container issues:
   - Navigate to CloudWatch > Log groups > /ecs/fastgpt

2. Common issues:
   - Container health check failures
   - Network connectivity issues
   - Resource constraints (CPU/Memory)
   - OpenAI API key configuration issues

## Security Considerations

1. The security group is configured to allow access from any IP (0.0.0.0/0) to port 7860
2. Consider implementing:
   - HTTPS using AWS Application Load Balancer
   - More restrictive security group rules
   - VPC endpoints for ECR and CloudWatch
   - AWS Secrets Manager for sensitive environment variables like OPENAI_API_KEY
   - Use AWS Systems Manager Parameter Store or Secrets Manager instead of hardcoding the API key in the task definition 