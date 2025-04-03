#!/bin/bash
# Minimalist script to invoke Lambda function

# Check if Lambda function name is provided
if [ $# -lt 1 ]; then
  echo "Usage: $0 <lambda-function-name>"
  exit 1
fi

LAMBDA_FUNCTION_NAME=$1

# Create a simple payload file
echo '{"message": "Hello from bash script"}' > /tmp/payload.json

# Invoke Lambda function
aws lambda invoke \
  --function-name "$LAMBDA_FUNCTION_NAME" \
  --cli-binary-format raw-in-base64-out \
  --payload "$(cat /tmp/payload.json)" \
  /tmp/lambda_output.json

# Check the result
if [ $? -eq 0 ]; then
  echo "Success! Check CloudWatch logs for Lambda function: $LAMBDA_FUNCTION_NAME"
  echo "Output:"
  cat /tmp/lambda_output.json
else
  echo "Failed to invoke Lambda function"
fi