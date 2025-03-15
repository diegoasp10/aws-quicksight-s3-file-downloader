# S3 Download API

A secure API Gateway solution for downloading files from S3 buckets with domain-restricted access.

## Overview

This API provides a secure way to generate pre-signed URLs for downloading files from specified S3 buckets. Access to the API is restricted to authorized domains only, ensuring that only trusted applications can generate download links.

## Features

- ✅ **Domain-restricted access**: Only requests from authorized domains can use this API
- ✅ **Multi-layer security**: CORS restrictions, WAF, and Lambda validations
- ✅ **Multi-bucket support**: Configure access to multiple S3 buckets
- ✅ **Direct redirection**: Automatic redirection to S3 presigned URLs
- ✅ **Configurable origins**: Allow multiple trusted domains to access the API

## Repository Structure

```bash
.
├── cdk                         # CDK application root
│   ├── aws                     # AWS resources
│   │   └── lambda              # Lambda function code
│   ├── bin                     # CDK entry point
│   │   └── cdk.ts              # Main CDK application
│   ├── config                  # Configuration files
│   │   ├── config.json         # Application configuration
│   │   └── tags.json           # Resource tagging
│   ├── lib                     # CDK construct libraries
│   │   └── s3-download-api-stack.ts  # Main stack definition
│   ├── test                    # Test files
│   │   └── cdk.test.ts         # Stack tests
│   ├── cdk.json                # CDK configuration
│   └── package.json            # Node.js dependencies
├── docs                        # API documentation
│   └── api-reference.md        # Detailed API documentation
└── README.md                   # This documentation
```

## Prerequisites

- [Node.js](https://nodejs.org/) 14.x or later
- [AWS CLI](https://aws.amazon.com/cli/) configured with appropriate credentials
- [AWS CDK](https://aws.amazon.com/cdk/) installed globally (`npm install -g aws-cdk`)
- [Python](https://www.python.org/) 3.9 or later for Lambda functions

## Installation and Deployment

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-organization/s3-download-api.git
   cd s3-download-api/cdk
   ```

2. **Install dependencies**

   ```bash
   npm install
   ```

3. **Configure the application**

   Edit `config/config.json` to set your specific configuration:

   ```json
   {
     "prefix": "your-prefix",
     "allowedBuckets": [
       "your-bucket-name-1",
       "your-bucket-name-2"
     ],
     "allowedOrigins": [
       "https://your-allowed-domain-1.com",
       "https://your-allowed-domain-2.com"
     ]
   }
   ```

4. **Bootstrap CDK** (if not already done)

   ```bash
   cdk bootstrap
   ```

5. **Deploy the application**

   ```bash
   cdk deploy
   ```

6. **Note the API URL from the output**

   ```bash
   Outputs:
   S3DownloadApiStack.ApiGatewayUrl = https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/prod/
   ```

## API Usage

### Endpoint

```bash
GET /files
```

### Query Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| uri       | Yes      | S3 URI of the file to download in the format `s3://bucket-name/path/to/file` |

### Example Request

```basg
GET https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/prod/files?uri=s3://your-bucket/path/to/file.pdf
```

### Response

The API will respond with a **302 Found** redirect to a pre-signed S3 URL allowing direct download of the requested file.

#### Error Responses

- **400 Bad Request**: Invalid or missing URI parameter
- **403 Forbidden**: Request from unauthorized domain or for unauthorized bucket
- **404 Not Found**: File does not exist
- **500 Internal Server Error**: Server-side error

### Important Notes

1. Requests **must** come from one of the configured allowed origins
2. The browser will automatically follow the redirect to download the file
3. The pre-signed URL is valid for 1 hour after generation
4. Only files in the configured allowed buckets can be accessed

## Security Considerations

This API implements multiple layers of security:

1. **Origin Restriction**: API Gateway CORS settings only allow requests from specified domains
2. **Web Application Firewall (WAF)**: Additional filtering based on HTTP headers
3. **Lambda Validation**: Request validation at the function level
4. **Resource Policy**: API Gateway resource policy restricts based on the referer header
5. **IAM Permissions**: Lambda functions have minimal required permissions to S3 buckets

## Customization

### Adding Additional Allowed Origins

Edit the `allowedOrigins` array in your stack configuration to add more trusted domains.

### Adding Additional S3 Buckets

Edit the `allowedBuckets` array in your stack configuration to grant access to more buckets.

## Troubleshooting

### Common Issues

1. **403 Forbidden errors**: Verify that requests are coming from an allowed origin
2. **CORS errors**: Check browser console for CORS-related issues
3. **404 Not Found**: Ensure the file exists in the specified S3 bucket path

### Debugging

The Lambda function logs detailed information to CloudWatch Logs:

- Origin and referer validation
- Access attempts from unauthorized domains
- S3 bucket and file validation

## License

[Include your license information here]

## Contact

[Your organization/team contact information]
