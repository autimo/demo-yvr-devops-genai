# AWS Error Insights with GenAI

Welcome to the Demo YVR DevOps GenAI Project!

This repository contains the source code for an Issue Creator Lambda function, designed to showcase the integration of AWS services, Terraform infrastructure as code, with an innovative approach to automated GitHub issue creation using AWS Bedrock generative AI.

## Join Our Discord

[Autimo's Between Two Clouds](https://discord.gg/6cD9utuW9k)

## Overview

The main component of this project is:

1. **Example Lambda Function**: A Python-based AWS Lambda function that is triggered by API Gateway. It processes HTTP requests, parses JSON payloads, and demonstrates error handling and logging in a serverless environment.
2. **Issue Creator Lambda Function**: An AWS Lambda function that uses the Anthropic API via AWS Bedrock to generate GitHub issues based on error logs captured from the example Lambda function. This demonstrates an innovative approach to automated issue creation by using a large language model to interpret error logs.

## Architecture Diagram

<p align="center">
  <img src="./images/architecture.png" alt="architecture">
</p>

## Getting Started

To get started with this project, you'll need to have the following prerequisites:

- An AWS account
- Terraform installed
- A GitHub account, Personal Access Token (PAT), and a repository where you can create issues

### Setup Instructions

1. **Clone the Repository**: Clone this repository to your local machine.

   ```shell
   git clone https://github.com/autimo/demo-yvr-devops-genai.git
   ```

2. **Configure AWS Credentials**: Ensure your AWS credentials are configured properly. This can be done by setting up the AWS CLI and running `aws configure` or setting the `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_REGION` environment variables.
3. **Terraform Initialization**: Navigate to the `terraform` directory and run `terraform init` to initialize the Terraform environment.
4. **Deploy Infrastructure**: Apply the Terraform configuration to deploy the necessary infrastructure to AWS.

   ```shell
   terraform apply
   ```

   Enter the required variables when prompted or create a `terraform.tfvars` file in the `terraform` directory with your specific values.

## GitHub Secrets and Variables

In order to successfully deploy and operate the components of this project, certain variables and secrets need to be configured in your GitHub repository's actions. Here's a breakdown of what's required:

### Secrets

- `GH_PAT`: A GitHub Personal Access Token with the necessary permissions to create issues in the specified repository.

### Variables

These are configured as environment variables in the `.github/workflows/push.yaml` file and are used across different steps in the GitHub Actions workflow:

- `TF_VERSION`: The version of Terraform to use.
- `PYTHON_VERSION`: The version of Python to use for running scripts.

Additionally, the following variables are used within the Terraform configuration and are prompted during the `terraform apply` command, but can also be predefined in a `terraform.tfvars` file:

- `AWS_IAM_ROLE_ARN`: The ARN of the AWS IAM role that GitHub Actions will assume for deploying resources.
- `AWS_REGION`: The AWS region where resources will be deployed.
- `AWS_S3_BUCKET_NAME`: The name of the S3 bucket used by Terraform for state storage.
- `AWS_DYNAMODB_TABLE_NAME`: The name of the DynamoDB table used by Terraform for state locking.

Ensure these secrets and variables are correctly set up in your GitHub repository and AWS account for the smooth operation of the project.

## Automated Subscription Filter

This project includes an automated subscription filter feature that dynamically creates or updates CloudWatch Log subscription filters for Lambda functions. This allows for automatic error reporting based on specific tags applied to the Lambda functions.

### How it works

1. A Lambda function (`create_sub_filters`) listens to CloudTrail events for Lambda function creation, deletion, and tagging operations.
2. When a Lambda function is created or tagged with a specific key, a subscription filter is automatically created or updated for that function's log group.
3. If a Lambda function is deleted or the specific tag is removed, the corresponding subscription filter is removed.

### Tagging Features

You can control the behavior of the error reporting system by applying specific tags to your Lambda functions:

1. **Enable Error Reporting**
   - Tag Key: `create_error_reports`
   - Tag Value: The filter pattern to use (e.g., `"ERROR"`, `"WARN"`, etc.)
   - Description: Enables error reporting for the Lambda function using the specified filter pattern.
   - Example: `create_error_reports = "ERROR"`

2. **Custom Filter Pattern**
   - If you don't specify a value for the `create_error_reports` tag, it will use the default filter pattern defined in the `DEFAULT_FILTER_PATTERN` environment variable (default is `"ERROR"`).

3. **GitHub Repository URL**
   - Tag Key: `github-repo`
   - Tag Value: The URL of the GitHub repository associated with the Lambda function.
   - Description: Specifies the GitHub repository where issues should be created for this Lambda function.
   - Example: `github-repo = "https://github.com/username/repo-name"`

### Environment Variables

The `create_sub_filters` Lambda function uses the following environment variables:

- `DESTINATION_ARN`: The ARN of the destination Lambda function (Issue Creator) for the subscription filter.
- `SUBSCRIPTION_FILTER_PREFIX`: Prefix for the subscription filter names (default: "ErrorSubscription").
- `FILTER_PATTERN`: Default filter pattern to use if not specified in the tag (default: "ERROR").
- `TAG_KEY`: The tag key to look for when creating subscription filters (default: "create_error_reports").

### Usage

To enable automated error reporting for your Lambda function:

1. Add the `create_error_reports` tag to your Lambda function with the desired filter pattern as the value.
2. Add the `github-repo` tag with the URL of the associated GitHub repository.

The system will automatically create a subscription filter for the Lambda function's log group, and any matching log events will trigger the Issue Creator Lambda to create GitHub issues.

## Contributing

Contributions are welcome! If you have improvements or bug fixes, please feel free to fork the repository and submit a pull request.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## TODO

- [ ] Read tag from lambda to decide if logs should be redacted from the issue
- [ ] Optionally get Github token SSM parameter from tag
- [ ] Instead of function name report the function arn in the issue. This provides more info
- [ ] Add timestamp of the event to the issue
- [ ] Add link to the cloudwatch log to the issue
- [ ] Store event metadata in dynamodb
- [ ] Add ECS support
- [ ] Custom prompt support for the issue creator
