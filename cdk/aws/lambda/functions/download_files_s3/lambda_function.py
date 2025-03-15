"""
AWS Lambda function for generating presigned URLs for S3 objects.

This module provides secure access to S3 objects through presigned URLs.
It includes validation for authorized origins and buckets.
"""

import json
import os
from typing import Dict, Any, Optional, List

import boto3 # type: ignore pylint: disable=E0401
from botocore.exceptions import ClientError # type: ignore pylint: disable=E0401


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]: # type: ignore pylint: disable=W0613
    """
    Handle requests for generating presigned URLs for S3 objects.

    Validates the request origin, parses S3 URI parameters, and generates
    a presigned URL for the requested S3 object if all validations pass.

    Args:
        event (Dict[str, Any]): The Lambda event object containing request details
        context (Any): The Lambda context object

    Returns:
        Dict[str, Any]: Response containing either a redirect to the presigned URL
                        or an error message with appropriate status code
    """
    # Initialize S3 client
    s3_client = boto3.client('s3')

    # Get configurations from environment variables
    allowed_buckets = os.environ['ALLOWED_BUCKETS'].split(',')
    allowed_origins = os.environ['ALLOWED_ORIGINS'].split(',')

    try:
        # Extract request origin information
        headers = event.get('headers', {}) or {}
        referer = headers.get('Referer', '') or headers.get('referer', '')
        origin = headers.get('Origin', '') or headers.get('origin', '')

        # Log debugging information
        print(f"Verifying origin: {origin}, Referer: {referer}")
        print(f"Allowed origins: {allowed_origins}")

        # Validate request origin
        is_authorized = _is_origin_authorized(origin, referer, allowed_origins)

        if not is_authorized:
            print(f"Request rejected: Unauthorized origin - Origin: {origin}, Referer: {referer}")

            # Determine which origin to use for CORS in the response
            cors_origin = origin if origin in allowed_origins else allowed_origins[0]

            return _create_error_response(
                status_code=403,
                error_message="Unauthorized origin.",
                cors_origin=cors_origin
            )

        # Extract the S3 URI from request parameters
        s3_uri = _extract_uri_from_request(event)

        if not s3_uri:
            return _create_error_response(
                status_code=400,
                error_message="URI parameter is required with format s3://bucket-name/path/to/file",
                cors_origin=_get_cors_origin(origin, allowed_origins)
            )

        # Validate the S3 URI format
        if not s3_uri.startswith('s3://'):
            return _create_error_response(
                status_code=400,
                error_message="URI must have the format s3://bucket-name/path/to/file",
                cors_origin=_get_cors_origin(origin, allowed_origins)
            )

        # Extract bucket name and key from S3 URI
        bucket_name, key = _parse_s3_uri(s3_uri)

        if not key:
            return _create_error_response(
                status_code=400,
                error_message="Invalid S3 URI. Expected format: s3://bucket-name/path/to/file",
                cors_origin=_get_cors_origin(origin, allowed_origins)
            )

        # Validate bucket is in allowed list
        if bucket_name not in allowed_buckets:
            return _create_error_response(
                status_code=403,
                error_message=f"You don't have permission to access bucket: {bucket_name}. "
                             f"Allowed buckets: {allowed_buckets}",
                cors_origin=_get_cors_origin(origin, allowed_origins)
            )

        # Verify object exists in S3
        try:
            s3_client.head_object(Bucket=bucket_name, Key=key)
        except ClientError:
            return _create_error_response(
                status_code=404,
                error_message="File not found",
                cors_origin=_get_cors_origin(origin, allowed_origins)
            )

        # Generate a presigned URL (valid for 60 minutes)
        signed_url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket_name,
                'Key': key
            },
            ExpiresIn=3600  # In seconds (1 hour)
        )

        # Return redirect to the presigned URL
        return {
            'statusCode': 302,
            'headers': {'Location': signed_url}
        }

    except Exception as exc: # pylint: disable=W0718
        print(f'Error: {str(exc)}')
        return _create_error_response(
            status_code=500,
            error_message="Internal server error",
            cors_origin=_get_cors_origin(origin, allowed_origins)
        )


def _is_origin_authorized(origin: str, referer: str,
                         allowed_origins: List[str]) -> bool:
    """
    Check if the request origin is authorized.

    Args:
        origin (str): The Origin header value
        referer (str): The Referer header value
        allowed_origins (List[str]): List of allowed origins

    Returns:
        bool: True if the origin is authorized, False otherwise
    """
    # Check if origin is in allowed list
    if origin in allowed_origins:
        print(f"Authorized origin: {origin}")
        return True

    # Check if referer starts with any allowed origin
    for allowed_origin in allowed_origins:
        if referer.startswith(f"{allowed_origin}/"):
            print(f"Authorized referer: {referer}")
            return True

    return False


def _extract_uri_from_request(event: Dict[str, Any]) -> Optional[str]:
    """
    Extract S3 URI from request parameters.

    Args:
        event (Dict[str, Any]): The Lambda event object

    Returns:
        Optional[str]: The S3 URI if found, None otherwise
    """
    query_params = event.get('queryStringParameters', {}) or {}
    path_params = event.get('pathParameters', {}) or {}

    return query_params.get('uri') or path_params.get('uri')


def _parse_s3_uri(s3_uri: str) -> tuple:
    """
    Parse an S3 URI to extract bucket name and key.

    Args:
        s3_uri (str): The S3 URI in format s3://bucket-name/path/to/file

    Returns:
        tuple: A tuple containing (bucket_name, key) or (bucket_name, None) if invalid
    """
    uri_parts = s3_uri[5:].split('/', 1)

    if len(uri_parts) != 2:
        return uri_parts[0], None

    return uri_parts[0], uri_parts[1]


def _get_cors_origin(origin: str, allowed_origins: List[str]) -> str:
    """
    Determine which origin to use for CORS headers.

    Args:
        origin (str): The Origin header from the request
        allowed_origins (List[str]): List of allowed origins

    Returns:
        str: The appropriate origin for CORS headers
    """
    return origin if origin in allowed_origins else allowed_origins[0]


def _create_error_response(status_code: int, error_message: str,
                          cors_origin: str) -> Dict[str, Any]:
    """
    Create a standardized error response.

    Args:
        status_code (int): HTTP status code
        error_message (str): Error message
        cors_origin (str): Origin to use for CORS headers

    Returns:
        Dict[str, Any]: The formatted error response
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': cors_origin,
            'Access-Control-Allow-Methods': 'OPTIONS,GET',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Credentials': 'true'
        },
        'body': json.dumps({
            'error': error_message
        })
    }
