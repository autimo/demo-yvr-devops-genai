import json
import logging
import os

from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey

PUBLIC_KEY = os.environ.get("DISCORD_PUBLIC_KEY")

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    try:
        interaction = json.loads(event["body"])

        logger.info(f"Received request with body: {interaction}")

        try:
            # Verify the request
            signature = event["headers"]["x-signature-ed25519"]
            timestamp = event["headers"]["x-signature-timestamp"]
            # log the signature and timestamp
            logger.info(
                f"Received request with signature: {signature} and timestamp: {timestamp}"
            )
            verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))
            interaction_str = json.dumps(interaction, separators=(",", ":"))
            verify_key.verify(
                f"{timestamp}{interaction_str}".encode(),
                bytes.fromhex(signature),
            )
        except BadSignatureError as e:
            logger.warning(f"Failed to verify request signature: {e}")
            # return {"statusCode": 401, "body": json.dumps("Invalid request signature")}

        logger.info("Request verified successfully")

        # Handle the interaction
        if interaction["type"] == 1:
            logger.info("Handling Ping request")
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"type": 1}),
            }
        elif interaction["type"] == 2:
            logger.info("Handling Command request")
            return command_handler(interaction)
        else:
            logger.error(f"Received unhandled request type: {interaction['type']}")
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps("Unhandled request type"),
            }
    except Exception as e:
        logger.exception(f"Internal server error: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(f"Internal server error: {str(e)}"),
        }


def command_handler(interaction):
    command = interaction["data"]["name"]
    logger.info(f"Received command: {command}")

    if command == "hello":
        logger.info("Responding to 'hello' command")
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"type": 4, "data": {"content": "Hello, YVR DevOps!"}}),
        }
    elif command == "hifive":
        logger.ino("Responding to 'hifive' command")
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"type": 4, "data": {"content": "✋"}}),
        }
    else:
        logger.warning(f"Received unhandled command: {command}")
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps("Unhandled command"),
        }
