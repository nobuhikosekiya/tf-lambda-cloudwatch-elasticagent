#!/usr/bin/env python3
"""
Script to invoke AWS Lambda function to generate logs in CloudWatch.
This script allows you to generate test logs for testing your Elastic Agent configuration.
"""

import argparse
import boto3
import json
import time
import datetime
import sys
import random
import os

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Invoke Lambda function to generate logs')
    parser.add_argument('function_name', help='Name of the Lambda function to invoke')
    parser.add_argument('--count', type=int, default=1, help='Number of invocations (default: 1)')
    parser.add_argument('--region', default=os.environ.get('AWS_REGION', 'ap-northeast-1'), 
                       help='AWS region (default: from env or ap-northeast-1)')
    parser.add_argument('--profile', help='AWS profile to use (optional)')
    parser.add_argument('--access-key', help='AWS access key (optional, overrides profile if provided)')
    parser.add_argument('--secret-key', help='AWS secret key (optional, must be provided if access-key is used)')
    parser.add_argument('--delay', type=float, default=2.0, 
                       help='Delay between invocations in seconds (default: 2.0)')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], 
                        default='INFO', help='Log level to use in the payload (default: INFO)')
    return parser.parse_args()

def generate_payload(invocation_number, log_level):
    """Generate a test payload with timestamp and random values."""
    timestamp = datetime.datetime.utcnow().isoformat() + 'Z'
    
    # Random user IDs and actions for more realistic logs
    user_ids = [f"user-{random.randint(1000, 9999)}" for _ in range(5)]
    actions = ["login", "logout", "view", "edit", "delete", "create", "update", "download", "upload"]
    
    return {
        "test_event": True,
        "timestamp": timestamp,
        "message": f"Test event #{invocation_number} with {log_level} level",
        "log_level": log_level,
        "metadata": {
            "source": "invoke_lambda.py",
            "invocation_number": invocation_number,
            "environment": "test",
            "user_id": random.choice(user_ids),
            "action": random.choice(actions),
            "duration_ms": random.randint(10, 5000),
            "status_code": random.choice([200, 201, 204, 400, 401, 403, 404, 500])
        }
    }

def create_session(args):
    """
    Create AWS session based on provided credentials or profile.
    Credential resolution order:
    1. Command line arguments (--access-key and --secret-key) if provided
    2. Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    3. Profile specified by --profile argument
    4. Default credential chain (env, credentials file, instance profile, etc.)
    """
    # Check for environment variables first (for GitHub Actions)
    aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    
    # Command line args override environment variables
    if args.access_key and args.secret_key:
        aws_access_key = args.access_key
        aws_secret_key = args.secret_key
        print(f"Using provided AWS access key and secret key")
    
    # If we have explicit keys, use them
    if aws_access_key and aws_secret_key:
        return boto3.Session(
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=args.region
        )
    # Otherwise, try to use profile if specified
    elif args.profile:
        print(f"Using AWS region: {args.region}, profile: {args.profile}")
        return boto3.Session(profile_name=args.profile, region_name=args.region)
    # If no profile specified, let boto3 use its default credential resolution
    else:
        print(f"Using AWS region: {args.region}, default credentials")
        return boto3.Session(region_name=args.region)

def invoke_lambda(function_name, payload, session):
    """Invoke Lambda function with the provided payload."""
    lambda_client = session.client('lambda')
    
    try:
        response = lambda_client.invoke(
            FunctionName=function_name,
            Payload=json.dumps(payload),
            InvocationType='RequestResponse'
        )
        return response
    except Exception as e:
        print(f"Error invoking Lambda function: {e}")
        sys.exit(1)

def main():
    """Main function to invoke Lambda multiple times."""
    args = parse_args()
    
    print(f"Invoking Lambda function '{args.function_name}' {args.count} times")
    
    # Create AWS session
    try:
        session = create_session(args)
    except Exception as e:
        print(f"Error creating AWS session: {e}")
        sys.exit(1)
    
    # Invoke Lambda function multiple times
    for i in range(1, args.count + 1):
        print(f"Invocation {i} of {args.count}")
        
        # Generate a unique payload for this invocation
        payload = generate_payload(i, args.log_level)
        
        # Invoke Lambda function
        response = invoke_lambda(args.function_name, payload, session)
        
        if response['StatusCode'] >= 200 and response['StatusCode'] < 300:
            print(f"Successfully invoked Lambda function (Status: {response['StatusCode']})")
            
            # If there's a function error, show it
            if 'FunctionError' in response:
                print(f"Function error: {response['FunctionError']}")
                payload_response = json.loads(response['Payload'].read().decode())
                print(f"Error details: {json.dumps(payload_response, indent=2)}")
        else:
            print(f"Failed to invoke Lambda function. Status code: {response['StatusCode']}")
            sys.exit(1)
        
        # Add a delay between invocations
        if i < args.count:
            print(f"Waiting {args.delay} seconds before next invocation...")
            time.sleep(args.delay)
    
    print("\nAll invocations completed. Check CloudWatch logs for Lambda function.")
    print(f"Logs should be available in log group: /aws/lambda/{args.function_name}")
    print("\nTo check logs using AWS CLI:")
    print(f"aws logs filter-log-events --log-group-name /aws/lambda/{args.function_name}")

if __name__ == "__main__":
    main()