import base64
import gzip
import io
import json
import logging
import os
import zipfile
from typing import List

import boto3
import instructor
import requests
from anthropic import AnthropicBedrock
from pydantic import BaseModel

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class GitHubIssue(BaseModel):
    title: str
    body: str
    labels: List[str]


def lambda_handler(event, context):
    # Get the base64 encoded, gzipped log data
    cw_data = event["awslogs"]["data"]

    # Decode and decompress the log data
    compressed_payload = base64.b64decode(cw_data)
    uncompressed_payload = gzip.decompress(compressed_payload)

    # Convert the log data from JSON format to a Python dictionary
    log_data = json.loads(uncompressed_payload)

    # Log the decoded data for debugging
    logger.info(f"Decoded log data: {log_data}")

    # Extract the log group to identify the lambda function
    log_group = log_data.get("logGroup")
    log_events = log_data.get("logEvents", [])
    lambda_name = log_group.split("/")[-1]

    # Get the lambda code from the function name
    lambda_code = get_lambda_code_from_function_name(lambda_name)

    logger.info(f"Lambda code: {lambda_code}")

    error_logs = [event["message"] for event in log_events]

    # Prepare the data for Anthropic API
    prompt = f"""
        Given the following AWS Lambda function details and error logs, create a comprehensive GitHub issue in markdown format. Include both a concise title and a detailed body.

        Lambda Function Name: {lambda_name}

        Lambda Function Code:
        ```python
        {lambda_code}
        ```

        Error Logs:
        ```
        {error_logs}
        ```

        Please structure the GitHub issue as follows:

        1. Title: A brief, descriptive summary of the issue (max 100 characters)

        2. Body:
        - **Problem Description**: Clearly explain the issue, including any error messages or unexpected behavior.
        - **Expected Behavior**: Describe what the Lambda function should do when working correctly.
        - **Actual Behavior**: Detail what's currently happening, including any error messages or unexpected output.
        - **Error Analysis**: Provide insights into what might be causing the error based on the logs and code.
        - **Potential Solutions**: Suggest one or more approaches to fix the issue.
        - **Additional Context**: Include any other relevant information (e.g., AWS region, runtime version, dependencies).
        - **Steps to Reproduce**: If applicable, list the steps to recreate the issue.
        - **Code Snippet**: If the error is in a specific part of the code, include that snippet here.

        3. Labels: Suggest appropriate labels for the issue (e.g., bug, enhancement, documentation).

        Please ensure the response is well-formatted in markdown and ready to be pasted directly into a GitHub issue.
        """

    # Initialize the Anthropic client using IAM authentication
    anthropic_client = instructor.from_anthropic(
        AnthropicBedrock(
            aws_region="us-west-2"  # Specify the correct AWS region
        )
    )

    # Call the Anthropic API to get the suggested solution
    github_issue = anthropic_client.messages.create(
        model="anthropic.claude-3-5-sonnet-20240620-v1:0",
        max_tokens=1024,
        messages=[
            {"role": "system", "content": "You are an expert programmer."},
            {"role": "user", "content": prompt},
        ],
        response_model=GitHubIssue,
    )
    logger.info(
        f"GitHub issue title:\n{github_issue.title}\n\nGitHub issue body:\n{github_issue.body}"
    )
    # Create the GitHub issue
    github_repo_url = get_lambda_github_repo_url(lambda_name)
    if github_repo_url:
        create_github_issue(
            github_repo_url, github_issue.title, github_issue.body, github_issue.labels
        )


def get_lambda_code_from_function_name(lambda_name):
    try:
        lambda_client = boto3.client("lambda")

        # Get the Lambda function's deployment package URL
        response = lambda_client.get_function(FunctionName=lambda_name)
        package_url = response["Code"]["Location"]

        # Download and extract the deployment package
        r = requests.get(package_url)
        zip_content = r.content
        lambda_code = ""

        # Extract the Lambda code from the deployment package
        with zipfile.ZipFile(io.BytesIO(zip_content)) as z:
            for filename in z.namelist():
                with z.open(filename) as f:
                    lambda_code += (
                        f"# Filename: {filename}\n\n"
                        + f.read().decode("utf-8")
                        + "\n\n"
                        + f"# End of file: {filename}"
                        + "\n\n"
                    )
        return lambda_code
    except Exception as e:
        logger.error(f"Failed to retrieve lambda code: {str(e)}")
        return "Error retrieving Lambda code"


def get_lambda_github_repo_url(lambda_name):
    try:
        lambda_client = boto3.client("lambda")
        # Retrieve the full function ARN
        function_arn = lambda_client.get_function(FunctionName=lambda_name)[
            "Configuration"
        ]["FunctionArn"]
        response = lambda_client.list_tags(Resource=function_arn)
        github_repo_url = response["Tags"].get("github-repo", None)
        return github_repo_url
    except Exception as e:
        logger.error(f"Failed to retrieve GitHub repo URL: {str(e)}")
        return None


def create_github_issue(github_repo_url, title, body, labels):
    try:
        ssm = boto3.client("ssm")

        # Get the GitHub access token from SSM Parameter Store
        github_access_token_ssm_param = os.environ.get("GITHUB_ACCESS_TOKEN_SSM_PARAM")
        github_access_token = ssm.get_parameter(
            Name=github_access_token_ssm_param, WithDecryption=True
        )["Parameter"]["Value"]
        headers = {"Authorization": f"token {github_access_token}"}

        # Get the org and repo from the github_repo_url
        org, repo = github_repo_url.split("/")[-2:]
        issue_url = f"https://api.github.com/repos/{org}/{repo}/issues"

        # Create the GitHub issue
        data = {"title": title, "body": body, "labels": labels}
        response = requests.post(issue_url, json=data, headers=headers)
        if response.status_code != 201:
            raise Exception(f"Failed to create GitHub issue: {response.content}")
    except Exception as e:
        logger.error(f"Failed to create GitHub issue: {str(e)}")
