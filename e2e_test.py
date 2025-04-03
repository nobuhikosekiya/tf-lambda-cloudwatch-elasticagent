#!/usr/bin/env python3
"""
End-to-end test script for Elastic Stack monitoring setup.
This script verifies the entire pipeline from Lambda invocation to CloudWatch logs.
"""

import argparse
import boto3
import json
import time
import sys
import os

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Test the Elastic monitoring setup')
    parser.add_argument('--region', default=os.environ.get('AWS_REGION', 'ap-northeast-1'), 
                        help='AWS region (default: from env or ap-northeast-1)')
    parser.add_argument('--log-group', required=True, help='CloudWatch log group to check')
    parser.add_argument('--lambda-function', required=True, help='Lambda function to invoke')
    parser.add_argument('--s3-bucket', required=True, help='S3 bucket name')
    parser.add_argument('--wait-time', type=int, default=30, 
                        help='Time to wait for logs to propagate (default: 30 seconds)')
    return parser.parse_args()

def invoke_lambda(lambda_client, function_name):
    """Invoke Lambda function with a test payload."""
    print(f"Invoking Lambda function: {function_name}")
    
    test_payload = {
        "test_event": True,
        "message": "CI/CD test event",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "metadata": {
            "source": "cicd-test-script",
            "environment": "test"
        }
    }
    
    try:
        response = lambda_client.invoke(
            FunctionName=function_name,
            Payload=json.dumps(test_payload),
            InvocationType='RequestResponse'
        )
        
        if response['StatusCode'] >= 200 and response['StatusCode'] < 300:
            print(f"Successfully invoked Lambda function (Status: {response['StatusCode']})")
            return True
        else:
            print(f"Failed to invoke Lambda function. Status code: {response['StatusCode']}")
            return False
    except Exception as e:
        print(f"Error invoking Lambda function: {e}")
        return False

def verify_cloudwatch_logs(logs_client, log_group_name, wait_time):
    """Verify logs were created in CloudWatch."""
    print(f"Waiting {wait_time} seconds for logs to propagate to CloudWatch...")
    time.sleep(wait_time)
    
    print(f"Checking for logs in CloudWatch log group: {log_group_name}")
    try:
        # List the log streams
        response = logs_client.describe_log_streams(
            logGroupName=log_group_name,
            orderBy='LastEventTime',
            descending=True,
            limit=5
        )
        
        if not response.get('logStreams'):
            print("No log streams found.")
            return False
            
        # Get the most recent log stream
        log_stream = response['logStreams'][0]['logStreamName']
        
        # Get events from the log stream
        events = logs_client.get_log_events(
            logGroupName=log_group_name,
            logStreamName=log_stream,
            limit=10
        )
        
        if not events.get('events'):
            print(f"No log events found in stream {log_stream}")
            return False
            
        print(f"Found {len(events['events'])} log events. Most recent:")
        for event in events['events'][:3]:
            print(f"  {event.get('message', '')[:100]}...")
            
        return True
    except Exception as e:
        print(f"Error checking CloudWatch logs: {e}")
        return False

def verify_s3_bucket(s3_client, bucket_name):
    """Verify the S3 bucket exists and is accessible."""
    print(f"Verifying S3 bucket: {bucket_name}")
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"S3 bucket {bucket_name} exists and is accessible.")
        return True
    except Exception as e:
        print(f"Error accessing S3 bucket: {e}")
        return False

def main():
    """Main test function."""
    args = parse_args()
    
    # Create AWS clients
    session = boto3.Session(region_name=args.region)
    lambda_client = session.client('lambda')
    logs_client = session.client('logs')
    s3_client = session.client('s3')
    
    # Step 1: Verify S3 bucket
    if not verify_s3_bucket(s3_client, args.s3_bucket):
        print("S3 bucket verification failed")
        return 1
        
    # Step 2: Invoke Lambda function
    if not invoke_lambda(lambda_client, args.lambda_function):
        print("Lambda invocation failed")
        return 1
    
    # Step 3: Verify CloudWatch logs
    if not verify_cloudwatch_logs(logs_client, args.log_group, args.wait_time):
        print("CloudWatch logs verification failed")
        return 1
    
    print("\n✅ All tests passed! The infrastructure is working correctly.")
    return 0

if __name__ == "__main__":
    sys.exit(main())