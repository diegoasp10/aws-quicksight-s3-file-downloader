import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import { Construct } from 'constructs';
import { join } from "path"; 

export interface S3DownloadApiStackProps extends cdk.StackProps {
  prefix: string;
  allowedBuckets: string[];
  allowedOrigins: string[];
}

export class S3DownloadApiStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: S3DownloadApiStackProps) {
    super(scope, id, props);

    const lambdaRole = new iam.Role(this, 'DownloadFunctionRole', {
      roleName: `${props.prefix}-download-s3-lambda-role`,
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
    });
    lambdaRole.addManagedPolicy(
      iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaBasicExecutionRole')
    );
    lambdaRole.addToPolicy(
      new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        actions: [
          's3:GetObject',
          's3:HeadObject',
        ],
        resources: props.allowedBuckets.map(bucketName => `arn:aws:s3:::${bucketName}/*`),
      })
    );

    const lambdaFunction = new lambda.Function(this, `LambdaDownloadS3Function`, {
      runtime: lambda.Runtime.PYTHON_3_12,
      functionName: `${props.prefix}-download-s3-lambda-function`,
      handler: "lambda_function.lambda_handler",
      code: lambda.Code.fromAsset(
          join(__dirname, "..", "aws/lambda/functions/download_files_s3")
      ),
      timeout: cdk.Duration.minutes(15),
      memorySize: 2048,
      role: lambdaRole,
      environment: {
        ALLOWED_BUCKETS: props.allowedBuckets.join(','),
        ALLOWED_ORIGINS: props.allowedOrigins.join(','),
      },
    });

    const api = new apigateway.RestApi(this, 'DownloadS3ApiGateway', {
      restApiName: `${props.prefix}-download-s3-api-gateway`,
      defaultCorsPreflightOptions: {
        allowOrigins: props.allowedOrigins,
        allowMethods: apigateway.Cors.ALL_METHODS,
        allowHeaders: apigateway.Cors.DEFAULT_HEADERS,
        allowCredentials: true,
      },
    });

    const files = api.root.addResource('files');
    files.addMethod('GET', new apigateway.LambdaIntegration(lambdaFunction));


  }
}