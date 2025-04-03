import json
import logging
import os

# Configure logging
log_level = os.environ.get('LOG_LEVEL', 'INFO')
numeric_level = getattr(logging, log_level.upper(), None)
if not isinstance(numeric_level, int):
    numeric_level = logging.INFO

logging.basicConfig(
    level=numeric_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger()
logger.setLevel(numeric_level)

def lambda_handler(event, context):
    """
    Simple Lambda function that logs the incoming event.
    This is used to demonstrate CloudWatch logging.
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        # Process S3 event
        if 'Records' in event:
            for record in event['Records']:
                if 's3' in record:
                    bucket = record['s3']['bucket']['name']
                    key = record['s3']['object']['key']
                    logger.info(f"S3 object created in bucket {bucket} with key {key}")
                elif 'sqs' in record:
                    logger.info(f"SQS message received: {record['body']}")
        
        return {
            'statusCode': 200,
            'body': json.dumps('Successfully processed event')
        }
    except Exception as e:
        logger.error(f"Error processing event: {str(e)}")
        raise