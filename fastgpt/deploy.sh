# Get the ECR login command
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 462019928087.dkr.ecr.us-east-1.amazonaws.com

# Build the image for ARM64
docker build --platform linux/arm64 -t fastgpt .

# Tag the image
docker tag fastgpt:latest 462019928087.dkr.ecr.us-east-1.amazonaws.com/fastgpt:latest

# Push the image
docker push 462019928087.dkr.ecr.us-east-1.amazonaws.com/fastgpt:latest