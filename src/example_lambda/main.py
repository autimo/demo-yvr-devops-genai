import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    event_body = json.loads(event.get("body", "{}"))
    if event_body.get("error", False):
        # Intentionally generate an error by misspelling the logger method
        logger.inf("Error generated...")

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Hello from Lambda!"}),
    }
