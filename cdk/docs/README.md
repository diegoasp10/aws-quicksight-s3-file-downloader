# S3 Download API Documentation

## Overview

This API provides a secure mechanism for downloading files from S3 buckets. It generates pre-signed URLs and redirects users directly to the file. Access is restricted to authorized domains only, ensuring that only trusted applications can use this service.

## Security

- **Domain restriction**: Only requests from authorized domains are accepted
- **Pre-signed URLs**: All S3 access is via temporary URLs valid for 1 hour
- **Bucket restriction**: Only configured S3 buckets can be accessed

## Endpoints

### GET /files

Generates a pre-signed URL for an S3 file and redirects the client to it for direct download.

#### Request Parameters

| Name | Located in | Required | Type | Description |
|------|------------|----------|------|-------------|
| uri | query | Yes | string | S3 URI of the file in format `s3://bucket-name/path/to/file` |

#### Request Example

```http
GET /files?uri=s3://your-bucket/path/to/your-file.pdf HTTP/1.1
Host: xxxxxxxxxx.execute-api.us-east-1.amazonaws.com
Origin: https://your-authorized-domain.com
```

#### Response

##### **Status Code: 302 Found**

```http
HTTP/1.1 302 Found
Location: https://your-bucket.s3.amazonaws.com/path/to/your-file.pdf?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=...&X-Amz-Date=...&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=...
```

The API redirects to a pre-signed S3 URL that:

- Is valid for 1 hour
- Provides direct download access to the requested file
- Does not expose S3 credentials

#### Error Responses

**400 Bad Request** - Invalid URI format or missing URI parameter

```json
{
  "error": "URI parameter is required with format s3://bucket-name/path/to/file"
}
```

**403 Forbidden** - Unauthorized domain or bucket

```json
{
  "error": "Unauthorized origin."
}
```

```json
{
  "error": "You don't have permission to access bucket: unauthorized-bucket. Allowed buckets: [bucket-list]"
}
```

**404 Not Found** - File does not exist in S3

```json
{
  "error": "File not found"
}
```

**500 Internal Server Error** - Server-side error

```json
{
  "error": "Internal server error"
}
```

## CORS Configuration

This API supports Cross-Origin Resource Sharing (CORS) for specific authorized domains configured in the deployment.

## Usage Examples

### Browser Example

```javascript
/**
 * Download a file from S3 via the API
 * @param {string} s3Uri - The S3 URI of the file to download
 */
function downloadFile(s3Uri) {
  // The API will handle the redirect automatically
  window.location.href = `https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/prod/files?uri=${encodeURIComponent(s3Uri)}`;
}

// Example usage
downloadFile('s3://your-bucket/path/to/your-file.pdf');
```

### HTML Link Example

```html
<a href="https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/prod/files?uri=s3://your-bucket/path/to/your-file.pdf">
  Download File
</a>
```

### cURL Example

```bash
curl -L -X GET "https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/prod/files?uri=s3://your-bucket/path/to/your-file.pdf" \
  -H "Origin: https://your-authorized-domain.com"
```

Note: The `-L` flag tells cURL to follow redirects.

## Implementation Details

The API uses AWS Lambda with Python to:

1. Validate the request origin against allowed domains
2. Parse and validate the S3 URI
3. Verify the file exists in an allowed bucket
4. Generate a pre-signed URL for the S3 object
5. Redirect the client to the pre-signed URL

## Rate Limits

- Default AWS API Gateway rate limits apply
- Consider implementing custom rate limiting for production use

## Notes

- The pre-signed URLs expire after 1 hour
- Requests must originate from authorized domains
- Only configured buckets can be accessed through this API
- The endpoint returns a redirect (302) rather than a JSON response
