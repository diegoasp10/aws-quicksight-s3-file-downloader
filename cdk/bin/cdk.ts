#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { S3DownloadApiStack } from '../lib/s3-download-api-stack';
import * as fs from 'fs';
import * as path from 'path';

const app = new cdk.App();

const configPath = path.join(__dirname, '..', 'config', 'config.json');
const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));

const tagsPath = path.join(__dirname, '..', 'config', 'tags.json');
const tags = JSON.parse(fs.readFileSync(tagsPath, 'utf8'));

const env = {
  account: process.env.CDK_DEFAULT_ACCOUNT || app.node.tryGetContext('account'),
  region: process.env.CDK_DEFAULT_REGION || app.node.tryGetContext('region')
};

console.log(`Deploying in the account: ${env.account}, region: ${env.region}`);

new S3DownloadApiStack(app, 'S3DownloadApiStack', {
  stackName: `${config.prefix}-s3-download-api-stack`,
  tags: tags,
  prefix: config.prefix,
  allowedBuckets: config.allowedBuckets,
  allowedOrigins: config.allowedOrigins
});