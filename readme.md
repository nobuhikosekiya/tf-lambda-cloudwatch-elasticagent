![Terraform CI/CD Tests](https://github.com/nobuhikosekiya/tf-lambda-cloudwatch-elasticagent/actions/workflows/terraform-test.yml/badge.svg)

## Troubleshooting

If you encounter issues with the Elastic Agent not collecting logs, try the following:

### Increase Elastic Agent logging level

1. SSH into the EC2 instance:
   ```bash
   ssh -i ~/.ssh/id_rsa ec2-user@<instance-ip>
   ```

2. Modify the Elastic Agent configuration to increase logging verbosity:
   ```bash
   sudo vi /etc/elastic-agent/elastic-agent.yml
   ```

3. Update the logging level:
   ```yaml
   logging:
     level: debug  # Change from info to debug
   ```

4. Restart the Elastic Agent:
   ```bash
   sudo systemctl restart elastic-agent
   ```

5. Check the logs:
   ```bash
   sudo journalctl -u elastic-agent -f
   ```

### Common issues

1. **CloudWatch input worker stopped**: If you see an error like "cloudwatch input worker for log group has stopped", check:
   - IAM permissions
   - Whether the Lambda function is generating logs
   - Network connectivity from the EC2 instance

2. **Permission errors**: Look for access denied errors in the logs:
   ```bash
   sudo grep -i "permission denied\|access denied\|error\|exception" /var/log/elastic-agent/elastic-agent.log
   ```

3. **Configuration issues**: Verify the CloudWatch input configuration:
   ```bash
   sudo grep -A 20 "cloudwatch" /etc/elastic-agent/agent.yml
   ```

Remember to check logs in the "logs-generic-default" data stream in Elasticsearch, as this is where the CloudWatch logs will be indexed.# AWS Elastic Stack Monitoring with S3-SQS Notifications

This Terraform project sets up AWS infrastructure to collect logs using the S3-SQS notification pattern for Elastic Stack monitoring. The infrastructure includes:

- An S3 bucket for storing logs
- An SQS queue for receiving S3 object creation notifications
- An EC2 instance with appropriate IAM permissions to run the Elastic Agent
- A Lambda function that generates logs to CloudWatch

## Architecture

```
                    +------------+     +----------------+     +---------------+
                    |   Lambda   | --> | CloudWatch Logs| --> | Elastic Agent |
                    | (logging)  |     | (Lambda logs)  |     | (EC2)         |
                    +------------+     +----------------+     +---------------+
                                                                      |
                                                                      v
                                                              +-------------+
                                                              | Elastic Stack|
                                                              | (monitoring) |
                                                              +-------------+
```

## Prerequisites

- AWS account with appropriate permissions
- Terraform installed (v1.0.0 or later)
- AWS CLI configured with a profile

## Usage

1. Clone this repository
2. Create a `terraform.tfvars` file based on the provided example
3. Initialize Terraform:

```bash
terraform init
```

4. Plan the deployment:

```bash
terraform plan
```

5. Apply the changes:

```bash
terraform apply
```

6. To destroy all resources when finished:

```bash
terraform destroy
```

## Elastic Agent Configuration

After deploying the infrastructure, you can configure the Elastic Agent with the following configuration for collecting CloudWatch logs:

```yaml
- type: aws-cloudwatch
  log_group_name_prefix: /aws/lambda/<lambda_function_name>
  scan_frequency: 1m
  region: <aws_region>
```

This configuration will be output by Terraform after a successful deployment.

## Required IAM Permissions

The EC2 instance running the CloudWatch Logs Elastic Agent has these permissions:

### EC2 Permissions (all resources)
- `ec2:DescribeTags`
- `ec2:DescribeInstances`

### CloudWatch Logs Permissions for All Log Groups
- `logs:DescribeLogGroups`

### CloudWatch Logs Permissions for Specific Lambda Log Group
- `logs:DescribeLogStreams`
- `logs:FilterLogEvents`
- `logs:GetLogEvents`
- `logs:StartQuery`
- `logs:StopQuery`
- `logs:GetQueryResults` 
- `logs:TestMetricFilter`
- `logs:GetLogRecord`

> **IMPORTANT NOTE ABOUT CLOUDWATCH LOGS PERMISSIONS**: 
> 
> CloudWatch Logs API has specific resource-level restrictions that must be followed:
> 
> 1. The `FilterLogEvents` API only supports log-group level resource types, not log-stream level restrictions.
> 
> 2. Resource ARN format for log groups must be:
>    ```
>    arn:${Partition}:logs:${Region}:${Account}:log-group:${LogGroupName}
>    ```
>    or with a wildcard suffix:
>    ```
>    arn:${Partition}:logs:${Region}:${Account}:log-group:${LogGroupName}:*
>    ```
> 
> 3. Some APIs like `DescribeLogGroups` don't support resource-level permissions and must use `"*"` as the resource.
>
> Incorrectly formatting these resource ARNs or attempting to apply inappropriate resource-level restrictions will result in permission errors like `AccessDeniedException` when trying to access CloudWatch Logs.

The policy follows AWS's recommended practice of using least privilege and respects the resource-level restrictions for each CloudWatch Logs API action.

## Customization

You can customize this deployment by modifying the `terraform.tfvars` file. Key customizable parameters include:

- AWS region and profile
- Resource prefix
- EC2 instance type and AMI
- S3 bucket and SQS queue names
- Tags for resource management

## Testing CloudWatch Logs Integration

Two test scripts are included to generate logs by invoking the Lambda function:

### Bash Script

```bash
# Make the script executable
chmod +x basic_invoke_lambda.sh

# Invoke the Lambda function
./basic_invoke_lambda.sh <lambda-function-name>

# Example
./basic_invoke_lambda.sh elastic-log-generator
```

### Python Script

```bash
# Make the script executable
chmod +x simple_invoke_lambda.py

# Install required dependencies
pip install boto3

# Invoke the Lambda function
./simple_invoke_lambda.py <lambda-function-name>

# Example
./simple_invoke_lambda.py elastic-log-generator
```

After running either script, check the CloudWatch logs to verify the logs were generated, and then verify that the Elastic Agent is collecting these logs correctly.

### Viewing the collected logs

When the Elastic Agent successfully collects logs from CloudWatch, the logs will be available in the **logs-generic-default** data stream in Elasticsearch. You can query this data stream to view the Lambda function logs:

```
GET logs-generic-default/_search
{
  "query": {
    "bool": {
      "must": [
        { "term": { "aws.cloudwatch.log_group": "/aws/lambda/elastic-log-generator" } }
      ]
    }
  },
  "sort": [{ "@timestamp": "desc" }],
  "size": 20
}
```

In Kibana, you can navigate to:
1. Stack Management > Index Management
2. Search for "logs-generic-default" index
3. Go to Discover and select this data stream
4. Filter for `aws.cloudwatch.log_group: "/aws/lambda/elastic-log-generator"`

If logs are not appearing in this data stream, check the Elastic Agent logs for errors.

## Lambda Function

The included Lambda function logs events to CloudWatch when triggered. The CloudWatch log group name is output after deployment, and logs can be viewed in the AWS Console.

## Security Considerations

- The EC2 instance is accessible via SSH from any IP address. In a production environment, restrict this to known IP addresses.
- IAM permissions are relatively broad for demonstration purposes. In a production environment, restrict these permissions further based on the principle of least privilege.

## Reference Documentation

For more information about AWS S3-SQS integration with Elastic Stack, see:
- [AWS S3 Input Documentation](https://www.elastic.co/guide/en/beats/filebeat/current/filebeat-input-aws-s3.html)
- [AWS Integration Documentation](https://www.elastic.co/integrations/aws)