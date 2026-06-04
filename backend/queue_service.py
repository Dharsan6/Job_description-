"""SQS queue service with local fallback when AWS is not configured."""

from __future__ import annotations

import json
import os
import queue

_local_queue: queue.Queue = queue.Queue()
_sqs_client = None
_queue_url: str | None = None

QUEUE_NAME = "resume-processing-queue"


def _get_sqs():
    global _sqs_client, _queue_url
    if _sqs_client is not None:
        return _sqs_client, _queue_url

    key = os.getenv("AWS_ACCESS_KEY_ID")
    secret = os.getenv("AWS_SECRET_ACCESS_KEY")
    region = os.getenv("AWS_REGION", "us-east-1")

    if not (key and secret):
        return None, None

    try:
        import boto3
        client = boto3.client(
            "sqs",
            region_name=region,
            aws_access_key_id=key,
            aws_secret_access_key=secret,
        )
        response = client.create_queue(QueueName=QUEUE_NAME)
        _sqs_client = client
        _queue_url = response["QueueUrl"]
        print(f"[SQS] Connected to queue: {_queue_url}", flush=True)
        return _sqs_client, _queue_url
    except Exception as e:
        print(f"[SQS] Falling back to local queue: {e}", flush=True)
        return None, None


def send_to_queue(message: dict) -> bool:
    """Send a message to SQS or local fallback queue. Returns True on success."""
    client, url = _get_sqs()
    if client and url:
        client.send_message(QueueUrl=url, MessageBody=json.dumps(message))
        return True
    _local_queue.put(message)
    return True


def receive_from_queue(wait_seconds: int = 5) -> dict | None:
    """Receive one message from SQS or local fallback queue."""
    client, url = _get_sqs()
    if client and url:
        response = client.receive_message(
            QueueUrl=url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=wait_seconds,
        )
        messages = response.get("Messages", [])
        if not messages:
            return None
        msg = messages[0]
        client.delete_message(QueueUrl=url, ReceiptHandle=msg["ReceiptHandle"])
        return json.loads(msg["Body"])

    try:
        return _local_queue.get(timeout=wait_seconds)
    except queue.Empty:
        return None
