import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    try:
        # Parse the event body
        event_body = json.loads(event.get("body", "{}"))

        if event_body.get("error", False):
            # Intentionally generate an error by raising an exception
            raise Exception("Intentional error generated")

        # Process the request (you can add more logic here)
        message = "Hello from Lambda!"

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": message}),
        }
    except json.JSONDecodeError:
        logger.error("Invalid JSON in the request body")
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Invalid JSON in request body"}),
        }
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Internal server error"}),
        }
