import logging
import os

import boto3

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

logs_client = boto3.client("logs")
lambda_client = boto3.client("lambda")

DESTINATION_ARN = os.environ["DESTINATION_ARN"]
SUBSCRIPTION_FILTER_PREFIX = os.environ.get(
    "SUBSCRIPTION_FILTER_PREFIX", "ErrorSubscription"
)
DEFAULT_FILTER_PATTERN = os.environ.get("FILTER_PATTERN", '"ERROR"')
TAG_KEY = os.environ.get("TAG_KEY", "create_error_reports")


def lambda_handler(event, context):
    detail = event["detail"]
    event_name = detail["eventName"]
    request_parameters = detail.get("requestParameters", {})

    function_name = request_parameters.get("functionName")
    if not function_name:
        function_name = (
            detail.get("requestParameters", {}).get("resourceArn", "").split(":")[-1]
        )

    tags = request_parameters.get("tags", {})

    if event_name == "CreateFunction" or (
        event_name == "TagResource" and TAG_KEY in tags
    ):
        tag_value = tags.get(TAG_KEY, DEFAULT_FILTER_PATTERN)
        create_or_update_log_subscription_filter(function_name, tag_value)
    elif event_name == "DeleteFunction" or (
        event_name == "UntagResource" and TAG_KEY in tags
    ):
        remove_log_subscription_filter(function_name)


def create_or_update_log_subscription_filter(function_name, filter_pattern):
    log_group_name = f"/aws/lambda/{function_name}"
    subscription_filter_name = f"{SUBSCRIPTION_FILTER_PREFIX}-{function_name}"

    try:
        # Check if subscription filter already exists
        response = logs_client.describe_subscription_filters(
            logGroupName=log_group_name, filterNamePrefix=subscription_filter_name
        )
        if response["subscriptionFilters"]:
            # Update existing subscription filter
            logs_client.put_subscription_filter(
                logGroupName=log_group_name,
                filterName=subscription_filter_name,
                filterPattern=filter_pattern,
                destinationArn=DESTINATION_ARN,
            )
            logger.info(
                f"Updated subscription filter {subscription_filter_name} for {log_group_name} with pattern {filter_pattern}"
            )
        else:
            # Create new subscription filter
            logs_client.put_subscription_filter(
                logGroupName=log_group_name,
                filterName=subscription_filter_name,
                filterPattern=filter_pattern,
                destinationArn=DESTINATION_ARN,
            )
            logger.info(
                f"Created subscription filter {subscription_filter_name} for {log_group_name} with pattern {filter_pattern}"
            )
    except logs_client.exceptions.ResourceNotFoundException:
        logger.error(f"Log group {log_group_name} not found.")
    except Exception as e:
        logger.error(f"Error creating or updating subscription filter: {e}")


def remove_log_subscription_filter(function_name):
    log_group_name = f"/aws/lambda/{function_name}"
    subscription_filter_name = f"{SUBSCRIPTION_FILTER_PREFIX}-{function_name}"

    try:
        logs_client.delete_subscription_filter(
            logGroupName=log_group_name, filterName=subscription_filter_name
        )
        logger.info(
            f"Removed subscription filter {subscription_filter_name} for {log_group_name}"
        )
    except logs_client.exceptions.ResourceNotFoundException:
        logger.error(f"Log group {log_group_name} not found.")
    except Exception as e:
        logger.error(f"Error removing subscription filter: {e}")
